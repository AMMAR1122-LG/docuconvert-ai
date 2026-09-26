# Same runtime as the backend (needs the same PDF/OCR/Office tools) but
# runs a queue worker instead of the HTTP API. Phase 2+: point this at
# Celery/RQ once conversions move off the request/response path for
# large files. For the MVP the backend processes synchronously, so this
# Dockerfile is here for when that split happens — see docs/scaling.md.
FROM python:3.12-slim

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
RUN pip install --no-cache-dir -r requirements.txt celery[redis]==5.4.0

COPY . .

CMD ["celery", "-A", "app.worker", "worker", "--loglevel=info"]
