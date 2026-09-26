from __future__ import annotations

from dataclasses import dataclass

import fitz  # PyMuPDF


@dataclass
class Chunk:
    text: str
    page: int  # 1-indexed


def extract_pdf_chunks(data: bytes, chunk_chars: int = 1200, overlap_chars: int = 200) -> list[Chunk]:
    """
    Extracts text per page, then splits into overlapping chunks. Chunks
    never cross a page boundary, so every chunk can be cited with a
    single, accurate page number (spec: "Source: Page 27").
    """
    doc = fitz.open(stream=data, filetype="pdf")
    chunks: list[Chunk] = []

    for page_index in range(len(doc)):
        page_text = doc[page_index].get_text().strip()
        if not page_text:
            continue
        start = 0
        while start < len(page_text):
            end = min(start + chunk_chars, len(page_text))
            chunk_text = page_text[start:end].strip()
            if chunk_text:
                chunks.append(Chunk(text=chunk_text, page=page_index + 1))
            if end == len(page_text):
                break
            start = end - overlap_chars

    doc.close()
    return chunks
