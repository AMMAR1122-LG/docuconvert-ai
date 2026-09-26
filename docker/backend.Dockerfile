FROM python:3.12-slim

# System dependencies needed by the PDF/OCR/Office pipeline:
#   - libreoffice: Word/Excel/PowerPoint <-> PDF conversion (headless)
#   - tesseract-ocr (+ language packs): OCR PDF, with eng/ara/urd from day one
#   - poppler-utils, ghostscript: used transitively by some PDF operations
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-ara \
    tesseract-ocr-urd \
    poppler-utils \
    ghostscript \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
