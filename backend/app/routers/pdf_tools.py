from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.db import User, get_db
from app.services import pdf_tools as pt
from app.services.auth import get_optional_user
from app.services.usage import check_and_record
from app.services.validation import validate_upload

router = APIRouter()


def _max_mb(user: User | None) -> int:
    return settings.MAX_UPLOAD_MB_PRO if (user and user.plan == "pro") else settings.MAX_UPLOAD_MB_FREE


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


async def _read_validated(file: UploadFile, allowed: list[str], user: User | None) -> bytes:
    data = await file.read()
    validate_upload(data, allowed, _max_mb(user))
    return data


def _pdf_response(data: bytes, filename: str) -> Response:
    return Response(
        content=data,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/merge")
async def merge(
    request: Request,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    check_and_record(db, user=user, ip_address=_client_ip(request), tool="merge-pdf")
    datas = []
    for f in files:
        datas.append(await _read_validated(f, ["pdf"], user))
    result = pt.merge_pdfs(datas)
    return _pdf_response(result, "merged.pdf")


@router.post("/split")
async def split(
    request: Request,
    mode: str = Form(...),
    ranges: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    check_and_record(db, user=user, ip_address=_client_ip(request), tool="split-pdf")
    data = await _read_validated(file, ["pdf"], user)
    results = pt.split_pdf(data, mode, ranges)
    if len(results) == 1:
        return _pdf_response(results[0][1], results[0][0])
    zipped = pt.zip_results(results)
    return Response(
        content=zipped,
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="split_pages.zip"'},
    )


@router.post("/compress")
async def compress(
    request: Request,
    level: str = Form("medium"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    check_and_record(db, user=user, ip_address=_client_ip(request), tool="compress-pdf")
    data = await _read_validated(file, ["pdf"], user)
    result, original_size, new_size = pt.compress_pdf(data, level)
    pct_saved = round(100 * (1 - new_size / original_size), 1) if original_size else 0
    return Response(
        content=result,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="compressed.pdf"',
            "X-Original-Size": str(original_size),
            "X-Compressed-Size": str(new_size),
            "X-Percent-Saved": str(pct_saved),
        },
    )


@router.post("/rotate")
async def rotate(
    request: Request,
    degrees: int = Form(...),
    pages: str | None = Form(None),  # comma-separated 1-indexed, or omit for all
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    check_and_record(db, user=user, ip_address=_client_ip(request), tool="rotate-pdf")
    data = await _read_validated(file, ["pdf"], user)
    page_list = [int(p) - 1 for p in pages.split(",")] if pages else None
    result = pt.rotate_pdf(data, degrees, page_list)
    return _pdf_response(result, "rotated.pdf")


@router.post("/delete-pages")
async def delete_pages(
    request: Request,
    pages: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    check_and_record(db, user=user, ip_address=_client_ip(request), tool="delete-pdf-pages")
    data = await _read_validated(file, ["pdf"], user)
    result = pt.delete_pages(data, [int(p) for p in pages.split(",")])
    return _pdf_response(result, "edited.pdf")


@router.post("/extract-pages")
async def extract_pages(
    request: Request,
    pages: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    check_and_record(db, user=user, ip_address=_client_ip(request), tool="extract-pdf-pages")
    data = await _read_validated(file, ["pdf"], user)
    result = pt.extract_pages(data, [int(p) for p in pages.split(",")])
    return _pdf_response(result, "extracted.pdf")


@router.post("/to-text")
async def to_text(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    check_and_record(db, user=user, ip_address=_client_ip(request), tool="pdf-to-text")
    data = await _read_validated(file, ["pdf"], user)
    text = pt.pdf_to_text(data)
    return {"text": text}


@router.post("/to-jpg")
async def to_jpg(
    request: Request,
    quality: str = Form("medium"),
    pages: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    check_and_record(db, user=user, ip_address=_client_ip(request), tool="pdf-to-jpg")
    data = await _read_validated(file, ["pdf"], user)
    page_list = [int(p) - 1 for p in pages.split(",")] if pages else None
    results = pt.pdf_to_images(data, quality, page_list)
    if len(results) == 1:
        return Response(
            content=results[0][1],
            media_type="image/jpeg",
            headers={"Content-Disposition": f'attachment; filename="{results[0][0]}"'},
        )
    zipped = pt.zip_results(results)
    return Response(
        content=zipped,
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="pages.zip"'},
    )


@router.post("/from-images")
async def from_images(
    request: Request,
    page_size: str = Form("A4"),
    orientation: str = Form("portrait"),
    margin_pt: int = Form(0),
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    check_and_record(db, user=user, ip_address=_client_ip(request), tool="jpg-to-pdf")
    images = []
    for f in files:
        images.append(await _read_validated(f, ["jpg", "png", "webp"], user))
    result = pt.images_to_pdf(images, page_size, margin_pt, orientation)
    return _pdf_response(result, "converted.pdf")


@router.post("/watermark")
async def watermark(
    request: Request,
    text: str = Form(...),
    opacity: float = Form(0.3),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    check_and_record(db, user=user, ip_address=_client_ip(request), tool="watermark-pdf")
    data = await _read_validated(file, ["pdf"], user)
    result = pt.add_watermark(data, text, opacity)
    return _pdf_response(result, "watermarked.pdf")


@router.post("/protect")
async def protect(
    request: Request,
    password: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    check_and_record(db, user=user, ip_address=_client_ip(request), tool="password-protect-pdf")
    data = await _read_validated(file, ["pdf"], user)
    result = pt.password_protect(data, password)
    return _pdf_response(result, "protected.pdf")


@router.post("/unlock")
async def unlock(
    request: Request,
    password: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    check_and_record(db, user=user, ip_address=_client_ip(request), tool="unlock-pdf")
    data = await _read_validated(file, ["pdf"], user)
    result = pt.unlock_pdf(data, password)
    return _pdf_response(result, "unlocked.pdf")


@router.post("/ocr")
async def ocr(
    request: Request,
    languages: str = Form("english"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    from app.services import ocr as ocr_service

    check_and_record(db, user=user, ip_address=_client_ip(request), tool="ocr-pdf")
    data = await _read_validated(file, ["pdf"], user)
    lang_list = [l.strip().lower() for l in languages.split(",")]
    result, text = ocr_service.ocr_pdf(data, lang_list)
    return Response(
        content=result,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="searchable.pdf"'},
    )
