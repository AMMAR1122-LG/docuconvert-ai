"""
File type validation by content, not filename.

Product rule: "Never trust the filename extension alone." We sniff the
first bytes of the upload against known magic numbers. This covers the
formats the MVP actually processes; DOCX/XLSX/PPTX are all ZIP
containers so we additionally peek inside for their marker file.
"""
from __future__ import annotations

import zipfile
import io

from app.core.errors import UnsupportedFileType, FileTooLarge

MAGIC_PDF = b"%PDF-"
MAGIC_JPG = b"\xff\xd8\xff"
MAGIC_PNG = b"\x89PNG\r\n\x1a\n"
MAGIC_WEBP_RIFF = b"RIFF"
MAGIC_ZIP = b"PK\x03\x04"


def _is_office_zip(head: bytes, data: bytes, marker: str) -> bool:
    if not head.startswith(MAGIC_ZIP):
        return False
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            return any(marker in name for name in zf.namelist())
    except zipfile.BadZipFile:
        return False


def detect_kind(data: bytes) -> str | None:
    """Return a short kind string ('pdf', 'jpg', 'png', 'webp', 'docx', 'xlsx', 'pptx') or None."""
    head = data[:16]
    if head.startswith(MAGIC_PDF):
        return "pdf"
    if head.startswith(MAGIC_JPG):
        return "jpg"
    if head.startswith(MAGIC_PNG):
        return "png"
    if head.startswith(MAGIC_WEBP_RIFF) and b"WEBP" in data[:16]:
        return "webp"
    if head.startswith(MAGIC_ZIP):
        if _is_office_zip(head, data, "word/"):
            return "docx"
        if _is_office_zip(head, data, "xl/"):
            return "xlsx"
        if _is_office_zip(head, data, "ppt/"):
            return "pptx"
    return None


def validate_upload(data: bytes, allowed_kinds: list[str], max_mb: int) -> str:
    size_mb = len(data) / (1024 * 1024)
    if size_mb > max_mb:
        raise FileTooLarge(max_mb)
    kind = detect_kind(data)
    if kind is None or kind not in allowed_kinds:
        raise UnsupportedFileType(allowed_kinds)
    return kind
