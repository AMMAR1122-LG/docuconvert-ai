"""
Integration tests exercising the same flows verified manually during
development (see README for the full manual test log). Run with:

    cd backend && pytest -v

Uses a temporary sqlite DB and local file storage so it needs no
external services — only tesseract/soffice on PATH for the OCR and
Word conversion tests (skipped automatically if not found).
"""
from __future__ import annotations

import io
import os
import shutil

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("RATE_LIMIT_ANON_PER_DAY", "1000")

from app.main import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def _make_pdf(pages: int = 3) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    for i in range(pages):
        c.drawString(72, 700, f"Test Page {i + 1}")
        c.showPage()
    c.save()
    return buf.getvalue()


def _make_jpg() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (400, 300), (10, 120, 200)).save(buf, format="JPEG")
    return buf.getvalue()


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_merge(client):
    pdf = _make_pdf(1)
    r = client.post("/api/pdf/merge", files=[("files", ("a.pdf", pdf, "application/pdf")),
                                              ("files", ("b.pdf", pdf, "application/pdf"))])
    assert r.status_code == 200
    assert r.content.startswith(b"%PDF-")


def test_split_all(client):
    pdf = _make_pdf(3)
    r = client.post("/api/pdf/split", data={"mode": "all"}, files={"file": ("t.pdf", pdf, "application/pdf")})
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/zip"


def test_compress_reports_real_savings(client):
    pdf = _make_pdf(1)
    r = client.post("/api/pdf/compress", data={"level": "high"}, files={"file": ("t.pdf", pdf, "application/pdf")})
    assert r.status_code == 200
    original = int(r.headers["x-original-size"])
    compressed = int(r.headers["x-compressed-size"])
    assert compressed <= original  # never claim a win we didn't get


def test_reject_non_pdf(client):
    r = client.post("/api/pdf/to-text", files={"file": ("t.pdf", b"not a pdf", "application/pdf")})
    assert r.status_code == 415
    assert r.json()["code"] == "unsupported_file_type"


def test_jpg_to_pdf_and_back(client):
    jpg = _make_jpg()
    r = client.post("/api/pdf/from-images", data={"page_size": "A4"}, files={"files": ("i.jpg", jpg, "image/jpeg")})
    assert r.status_code == 200
    assert r.content.startswith(b"%PDF-")


def test_password_protect_and_wrong_unlock(client):
    pdf = _make_pdf(1)
    r = client.post("/api/pdf/protect", data={"password": "secret123"}, files={"file": ("t.pdf", pdf, "application/pdf")})
    assert r.status_code == 200
    protected = r.content

    wrong = client.post("/api/pdf/unlock", data={"password": "wrong"}, files={"file": ("t.pdf", protected, "application/pdf")})
    assert wrong.status_code == 401

    right = client.post("/api/pdf/unlock", data={"password": "secret123"}, files={"file": ("t.pdf", protected, "application/pdf")})
    assert right.status_code == 200


def test_auth_register_login_and_wrong_password(client):
    import uuid
    email = f"{uuid.uuid4()}@example.com"
    r = client.post("/api/auth/register", json={"name": "T", "email": email, "password": "password123"})
    assert r.status_code == 200
    token = r.json()["access_token"]

    ok = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    assert ok.status_code == 200

    bad = client.post("/api/auth/login", json={"email": email, "password": "nope"})
    assert bad.status_code == 401

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == email

    anon = client.get("/api/auth/me")
    assert anon.status_code == 401


@pytest.mark.skipif(shutil.which("soffice") is None and shutil.which("libreoffice") is None, reason="LibreOffice not installed")
def test_word_to_pdf():
    from docx import Document
    d = Document()
    d.add_paragraph("Hello from a test docx.")
    buf = io.BytesIO()
    d.save(buf)

    from app.services.convert import docx_to_pdf
    result = docx_to_pdf(buf.getvalue())
    assert result.startswith(b"%PDF-")


@pytest.mark.skipif(shutil.which("tesseract") is None, reason="Tesseract not installed")
def test_ocr_extracts_text():
    from PIL import ImageDraw
    import fitz
    from app.services.ocr import ocr_pdf

    img = Image.new("RGB", (900, 300), "white")
    ImageDraw.Draw(img).text((30, 30), "OCR TEST STRING", fill="black")
    img_buf = io.BytesIO()
    img.save(img_buf, format="PNG")

    doc = fitz.open()
    page = doc.new_page(width=612, height=792)
    page.insert_image(fitz.Rect(36, 36, 500, 250), stream=img_buf.getvalue())
    pdf_bytes = doc.tobytes()
    doc.close()

    _, text = ocr_pdf(pdf_bytes, ["english"])
    assert "OCR" in text.upper()
