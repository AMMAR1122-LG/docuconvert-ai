from __future__ import annotations

from fastapi import APIRouter, Depends, File, Request, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.db import User, get_db
from app.services import convert as cv
from app.services.auth import get_optional_user
from app.services.usage import check_and_record
from app.services.validation import validate_upload

router = APIRouter()


def _max_mb(user: User | None) -> int:
    return settings.MAX_UPLOAD_MB_PRO if (user and user.plan == "pro") else settings.MAX_UPLOAD_MB_FREE


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


@router.post("/pdf/to-word")
async def pdf_to_word(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    check_and_record(db, user=user, ip_address=_client_ip(request), tool="pdf-to-word")
    data = await file.read()
    validate_upload(data, ["pdf"], _max_mb(user))
    result = cv.pdf_to_docx(data)
    return Response(
        content=result,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": 'attachment; filename="converted.docx"'},
    )


@router.post("/word/to-pdf")
async def word_to_pdf(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    check_and_record(db, user=user, ip_address=_client_ip(request), tool="word-to-pdf")
    data = await file.read()
    kind = validate_upload(data, ["docx"], _max_mb(user))
    result = cv.docx_to_pdf(data, original_suffix=f".{kind}")
    return Response(
        content=result,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="converted.pdf"'},
    )


@router.post("/pdf/to-excel")
async def pdf_to_excel(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    check_and_record(db, user=user, ip_address=_client_ip(request), tool="pdf-to-excel")
    data = await file.read()
    validate_upload(data, ["pdf"], _max_mb(user))
    result = cv.pdf_to_xlsx(data)
    return Response(
        content=result,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": 'attachment; filename="converted.xlsx"',
            "X-Warning": "Complex layouts may not convert perfectly.",
        },
    )


@router.post("/pdf/to-ppt")
async def pdf_to_ppt(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    check_and_record(db, user=user, ip_address=_client_ip(request), tool="pdf-to-ppt")
    data = await file.read()
    validate_upload(data, ["pdf"], _max_mb(user))
    result = cv.pdf_to_pptx_fallback(data)
    return Response(
        content=result,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": 'attachment; filename="converted.pptx"'},
    )
