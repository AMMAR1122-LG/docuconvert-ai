"""
Actual PDF operations. Every function takes bytes in and returns bytes
(or a list of (filename, bytes) for multi-file results) — no disk state,
no fake success. If a page range is invalid or a PDF is corrupt, these
raise AppError with a message safe to show the user.
"""
from __future__ import annotations

import io
import zipfile

import fitz  # PyMuPDF
from pypdf import PdfReader, PdfWriter
from PIL import Image
from reportlab.lib.pagesizes import A4, LETTER
from reportlab.pdfgen import canvas

from app.core.errors import AppError

PAGE_SIZES = {"A4": A4, "Letter": LETTER}


def _reader(data: bytes) -> PdfReader:
    try:
        r = PdfReader(io.BytesIO(data))
        if r.is_encrypted:
            raise AppError("This PDF is password-protected. Unlock it first.", 400, "pdf_encrypted")
        return r
    except AppError:
        raise
    except Exception as exc:
        raise AppError("We couldn't read this PDF. It may be corrupted.", 400, "pdf_unreadable") from exc


def merge_pdfs(files: list[bytes]) -> bytes:
    if len(files) < 2:
        raise AppError("Select at least two PDFs to merge.", 400, "not_enough_files")
    writer = PdfWriter()
    for data in files:
        reader = _reader(data)
        for page in reader.pages:
            writer.add_page(page)
    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


def _parse_ranges(ranges: str, page_count: int) -> list[tuple[int, int]]:
    """'1-5,8,10-12' -> [(0,4),(7,7),(9,11)] (0-indexed, inclusive)."""
    spans = []
    for part in ranges.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            start, end = int(a) - 1, int(b) - 1
        else:
            start = end = int(part) - 1
        if start < 0 or end >= page_count or start > end:
            raise AppError(f"Page range '{part}' is out of bounds for a {page_count}-page PDF.", 400, "bad_range")
        spans.append((start, end))
    if not spans:
        raise AppError("No valid page ranges given.", 400, "bad_range")
    return spans


def split_pdf(data: bytes, mode: str, ranges: str | None) -> list[tuple[str, bytes]]:
    """mode: 'all' (one PDF per page) or 'ranges' (ranges string like '1-5,6-10')."""
    reader = _reader(data)
    n = len(reader.pages)
    results: list[tuple[str, bytes]] = []

    if mode == "all":
        for i in range(n):
            writer = PdfWriter()
            writer.add_page(reader.pages[i])
            buf = io.BytesIO()
            writer.write(buf)
            results.append((f"page_{i + 1}.pdf", buf.getvalue()))
    elif mode == "ranges":
        if not ranges:
            raise AppError("Provide page ranges, e.g. 1-5,6-10.", 400, "bad_range")
        spans = _parse_ranges(ranges, n)
        for idx, (start, end) in enumerate(spans, start=1):
            writer = PdfWriter()
            for p in range(start, end + 1):
                writer.add_page(reader.pages[p])
            buf = io.BytesIO()
            writer.write(buf)
            results.append((f"split_{idx}_pages_{start + 1}-{end + 1}.pdf", buf.getvalue()))
    else:
        raise AppError("Unknown split mode.", 400, "bad_mode")
    return results


def zip_results(files: list[tuple[str, bytes]]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in files:
            zf.writestr(name, data)
    return buf.getvalue()


_COMPRESSION_PROFILES = {
    # (image DPI target, JPEG quality)
    "low": (150, 85),
    "medium": (110, 70),
    "high": (72, 45),
}


def compress_pdf(data: bytes, level: str = "medium") -> tuple[bytes, int, int]:
    """Downsamples embedded images and re-writes the PDF. Returns (bytes, original_size, new_size)."""
    if level not in _COMPRESSION_PROFILES:
        raise AppError("Compression level must be low, medium, or high.", 400, "bad_level")
    dpi, quality = _COMPRESSION_PROFILES[level]
    original_size = len(data)

    try:
        doc = fitz.open(stream=data, filetype="pdf")
    except Exception as exc:
        raise AppError("We couldn't read this PDF. It may be corrupted.", 400, "pdf_unreadable") from exc

    for page in doc:
        for img in page.get_images(full=True):
            xref = img[0]
            try:
                base = doc.extract_image(xref)
                pil_img = Image.open(io.BytesIO(base["image"])).convert("RGB")
                w, h = pil_img.size
                scale = min(1.0, dpi / 150)
                if scale < 1.0:
                    pil_img = pil_img.resize((max(1, int(w * scale)), max(1, int(h * scale))))
                out_buf = io.BytesIO()
                pil_img.save(out_buf, format="JPEG", quality=quality, optimize=True)
                doc.update_stream(xref, out_buf.getvalue())
            except Exception:
                continue  # skip images we can't safely re-encode rather than fail the whole job

    out = doc.tobytes(garbage=4, deflate=True)
    doc.close()
    new_size = len(out)
    # Never claim a compression win we didn't get.
    if new_size >= original_size:
        return data, original_size, original_size
    return out, original_size, new_size


def rotate_pdf(data: bytes, degrees: int, pages: list[int] | None = None) -> bytes:
    if degrees % 90 != 0:
        raise AppError("Rotation must be a multiple of 90 degrees.", 400, "bad_rotation")
    reader = _reader(data)
    writer = PdfWriter()
    target = set(pages) if pages else None
    for i, page in enumerate(reader.pages):
        if target is None or i in target:
            page.rotate(degrees % 360)
        writer.add_page(page)
    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


def delete_pages(data: bytes, pages: list[int]) -> bytes:
    reader = _reader(data)
    n = len(reader.pages)
    remove = set(p - 1 for p in pages)
    if not remove or any(p < 0 or p >= n for p in remove):
        raise AppError("Invalid page numbers for this document.", 400, "bad_pages")
    if len(remove) >= n:
        raise AppError("Can't delete every page in the document.", 400, "bad_pages")
    writer = PdfWriter()
    for i, page in enumerate(reader.pages):
        if i not in remove:
            writer.add_page(page)
    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


def extract_pages(data: bytes, pages: list[int]) -> bytes:
    reader = _reader(data)
    n = len(reader.pages)
    keep = [p - 1 for p in pages]
    if not keep or any(p < 0 or p >= n for p in keep):
        raise AppError("Invalid page numbers for this document.", 400, "bad_pages")
    writer = PdfWriter()
    for i in keep:
        writer.add_page(reader.pages[i])
    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


def pdf_to_text(data: bytes) -> str:
    doc = fitz.open(stream=data, filetype="pdf")
    parts = [page.get_text() for page in doc]
    doc.close()
    return "\n\n".join(parts)


def pdf_to_images(data: bytes, quality: str = "medium", pages: list[int] | None = None) -> list[tuple[str, bytes]]:
    dpi_map = {"low": 96, "medium": 150, "high": 300}
    dpi = dpi_map.get(quality, 150)
    doc = fitz.open(stream=data, filetype="pdf")
    results = []
    indices = pages if pages else range(len(doc))
    for i in indices:
        if i < 0 or i >= len(doc):
            continue
        page = doc[i]
        pix = page.get_pixmap(dpi=dpi)
        results.append((f"page_{i + 1}.jpg", pix.tobytes("jpg")))
    doc.close()
    if not results:
        raise AppError("No valid pages to render.", 400, "bad_pages")
    return results


def images_to_pdf(images: list[bytes], page_size: str = "A4", margin_pt: int = 0, orientation: str = "portrait") -> bytes:
    if not images:
        raise AppError("Add at least one image.", 400, "no_images")
    size = PAGE_SIZES.get(page_size, A4)
    if orientation == "landscape":
        size = (size[1], size[0])
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=size)
    page_w, page_h = size
    for img_bytes in images:
        try:
            pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        except Exception as exc:
            raise AppError("One of the images couldn't be read.", 400, "bad_image") from exc
        avail_w, avail_h = page_w - 2 * margin_pt, page_h - 2 * margin_pt
        img_ratio = pil_img.width / pil_img.height
        box_ratio = avail_w / avail_h
        if img_ratio > box_ratio:
            draw_w = avail_w
            draw_h = avail_w / img_ratio
        else:
            draw_h = avail_h
            draw_w = avail_h * img_ratio
        x = margin_pt + (avail_w - draw_w) / 2
        y = margin_pt + (avail_h - draw_h) / 2
        img_reader_buf = io.BytesIO()
        pil_img.save(img_reader_buf, format="PNG")
        img_reader_buf.seek(0)
        from reportlab.lib.utils import ImageReader
        c.drawImage(ImageReader(img_reader_buf), x, y, width=draw_w, height=draw_h)
        c.showPage()
    c.save()
    return buf.getvalue()


def add_watermark(data: bytes, text: str, opacity: float = 0.3) -> bytes:
    reader = _reader(data)
    writer = PdfWriter()

    # Build a one-page watermark overlay sized to the first page, then stamp every page.
    first = reader.pages[0]
    w, h = float(first.mediabox.width), float(first.mediabox.height)
    overlay_buf = io.BytesIO()
    c = canvas.Canvas(overlay_buf, pagesize=(w, h))
    c.saveState()
    c.setFillColorRGB(0.5, 0.5, 0.5, alpha=opacity)
    c.setFont("Helvetica-Bold", 40)
    c.translate(w / 2, h / 2)
    c.rotate(45)
    c.drawCentredString(0, 0, text)
    c.restoreState()
    c.save()
    overlay_buf.seek(0)
    overlay_reader = PdfReader(overlay_buf)
    overlay_page = overlay_reader.pages[0]

    for page in reader.pages:
        page.merge_page(overlay_page)
        writer.add_page(page)
    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


def password_protect(data: bytes, user_password: str, owner_password: str | None = None) -> bytes:
    reader = _reader(data)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.encrypt(user_password=user_password, owner_password=owner_password or user_password)
    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


def unlock_pdf(data: bytes, password: str) -> bytes:
    try:
        reader = PdfReader(io.BytesIO(data))
        if reader.is_encrypted:
            ok = reader.decrypt(password)
            if not ok:
                raise AppError("Incorrect password.", 401, "wrong_password")
    except AppError:
        raise
    except Exception as exc:
        raise AppError("We couldn't read this PDF.", 400, "pdf_unreadable") from exc
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()
