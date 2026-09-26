"""
OCR PDF -> searchable PDF. Renders each page to an image, runs
Tesseract to get a text layer, and uses PyMuPDF to write an invisible
text layer back over the original page image (the standard
"searchable PDF" technique — visible content is unchanged, but text
becomes selectable/searchable).

Language codes follow Tesseract's 3-letter codes: eng, ara, urd.
Architected as a plain function so a cloud OCR provider can be swapped
in later without touching callers (see product_self_knowledge-style
provider abstraction used for AI).
"""
from __future__ import annotations

import io

import fitz
import pytesseract
from PIL import Image

from app.core.errors import AppError

LANGUAGE_CODES = {"english": "eng", "arabic": "ara", "urdu": "urd"}
SUPPORTED_LANGUAGES = list(LANGUAGE_CODES.keys())


def _tesseract_lang(languages: list[str]) -> str:
    codes = [LANGUAGE_CODES[l] for l in languages if l in LANGUAGE_CODES]
    if not codes:
        raise AppError(f"Unsupported OCR language. Choose from: {', '.join(SUPPORTED_LANGUAGES)}.", 400, "bad_language")
    return "+".join(codes)


def ocr_pdf(data: bytes, languages: list[str] | None = None) -> tuple[bytes, str]:
    """Returns (searchable_pdf_bytes, extracted_text)."""
    lang = _tesseract_lang(languages or ["english"])
    doc = fitz.open(stream=data, filetype="pdf")
    all_text = []

    for page in doc:
        pix = page.get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        try:
            page_text = pytesseract.image_to_string(img, lang=lang)
        except pytesseract.TesseractError as exc:
            raise AppError("OCR failed for this page. Try a clearer scan.", 400, "ocr_failed") from exc
        all_text.append(page_text)

        # Get word-level boxes to place an invisible, searchable text layer.
        try:
            ocr_data = pytesseract.image_to_data(img, lang=lang, output_type=pytesseract.Output.DICT)
        except pytesseract.TesseractError:
            continue
        scale_x = page.rect.width / pix.width
        scale_y = page.rect.height / pix.height
        for i, word in enumerate(ocr_data["text"]):
            if not word.strip():
                continue
            x, y, w, h = (
                ocr_data["left"][i] * scale_x,
                ocr_data["top"][i] * scale_y,
                ocr_data["width"][i] * scale_x,
                ocr_data["height"][i] * scale_y,
            )
            page.insert_text(
                (x, y + h),
                word,
                fontsize=max(1, h * 0.9),
                render_mode=3,  # invisible
            )

    out = doc.tobytes(garbage=4, deflate=True)
    doc.close()
    return out, "\n\n".join(all_text)


def detect_scanned_pages(data: bytes) -> list[int]:
    """Heuristic: a page with (almost) no extractable text is probably a scan."""
    doc = fitz.open(stream=data, filetype="pdf")
    scanned = [i for i, page in enumerate(doc) if len(page.get_text().strip()) < 20]
    doc.close()
    return scanned
