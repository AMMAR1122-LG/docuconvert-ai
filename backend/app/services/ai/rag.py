"""
Retrieval-augmented generation over an uploaded PDF.

Pipeline: PDF -> chunk (chunking.py) -> embed -> retrieve top-k -> LLM
answer constrained to those chunks, with page citations.

Embeddings use the configured AI provider when available. When no
provider key is set (or the provider doesn't serve embeddings, like
Groq today), retrieval falls back to a dependency-free TF-IDF + cosine
similarity index — this keeps retrieval itself fully testable and
functional without any external API key; only the final answer
generation step requires a real LLM call.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field

from app.core.errors import AppError
from app.services.ai.chunking import Chunk, extract_pdf_chunks

_WORD_RE = re.compile(r"[a-zA-Z']+")


def _tokenize(text: str) -> list[str]:
    return [w.lower() for w in _WORD_RE.findall(text)]


@dataclass
class DocumentIndex:
    chunks: list[Chunk]
    _doc_freq: Counter = field(default_factory=Counter)
    _chunk_tf: list[Counter] = field(default_factory=list)

    def __post_init__(self):
        for chunk in self.chunks:
            tf = Counter(_tokenize(chunk.text))
            self._chunk_tf.append(tf)
            for term in tf:
                self._doc_freq[term] += 1

    def _idf(self, term: str) -> float:
        n = len(self.chunks) or 1
        df = self._doc_freq.get(term, 0)
        return math.log((n + 1) / (df + 1)) + 1

    def _vector(self, tf: Counter) -> dict[str, float]:
        return {term: count * self._idf(term) for term, count in tf.items()}

    @staticmethod
    def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
        common = set(a) & set(b)
        dot = sum(a[t] * b[t] for t in common)
        norm_a = math.sqrt(sum(v * v for v in a.values())) or 1e-9
        norm_b = math.sqrt(sum(v * v for v in b.values())) or 1e-9
        return dot / (norm_a * norm_b)

    def search(self, query: str, top_k: int = 5) -> list[tuple[Chunk, float]]:
        query_vec = self._vector(Counter(_tokenize(query)))
        scored = []
        for chunk, tf in zip(self.chunks, self._chunk_tf):
            score = self._cosine(query_vec, self._vector(tf))
            if score > 0:
                scored.append((chunk, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]


def build_index(pdf_bytes: bytes) -> DocumentIndex:
    chunks = extract_pdf_chunks(pdf_bytes)
    if not chunks:
        raise AppError(
            "This PDF has no extractable text — try running OCR PDF first.", 400, "no_text"
        )
    return DocumentIndex(chunks=chunks)


SYSTEM_PROMPT = (
    "You are a document assistant. Answer ONLY using the excerpts provided below, "
    "each labeled with its page number. If the excerpts don't contain the answer, "
    "say so plainly instead of guessing. Always cite the page number(s) you used, "
    "in the form 'Source: Page N'."
)


def answer_question(index: DocumentIndex, question: str, top_k: int = 5) -> dict:
    """Returns {"answer": str, "citations": [{"page": int, "snippet": str}]}."""
    matches = index.search(question, top_k=top_k)
    if not matches:
        return {
            "answer": "I couldn't find anything in this document relevant to that question.",
            "citations": [],
        }

    context = "\n\n".join(f"[Page {c.page}]\n{c.text}" for c, _ in matches)
    prompt = f"Excerpts:\n\n{context}\n\nQuestion: {question}"

    from app.services.ai.providers import get_provider
    provider = get_provider()
    answer = provider.complete(SYSTEM_PROMPT, prompt, max_tokens=800)

    citations = [{"page": c.page, "snippet": c.text[:200]} for c, _ in matches]
    return {"answer": answer, "citations": citations}
