"""
Provider abstraction so the rest of the app calls one interface
(`complete` / `embed`) regardless of which LLM vendor is configured.
Swapping AI_PROVIDER in settings, or the API key, is the only change
needed anywhere else in the codebase — no provider-specific code
should leak into routers or the RAG pipeline.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.config import settings
from app.core.errors import AppError


class AIProvider(ABC):
    @abstractmethod
    def complete(self, system: str, prompt: str, max_tokens: int = 1000) -> str: ...

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]: ...


class OpenAIProvider(AIProvider):
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise AppError("OpenAI is not configured (OPENAI_API_KEY missing).", 503, "ai_not_configured")
        try:
            from openai import OpenAI  # imported lazily so the package is optional
        except ImportError as exc:
            raise AppError("The openai package isn't installed on the server.", 503, "ai_not_configured") from exc
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def complete(self, system: str, prompt: str, max_tokens: int = 1000) -> str:
        resp = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content or ""

    def embed(self, texts: list[str]) -> list[list[float]]:
        resp = self.client.embeddings.create(model="text-embedding-3-small", input=texts)
        return [d.embedding for d in resp.data]


class GeminiProvider(AIProvider):
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise AppError("Gemini is not configured (GEMINI_API_KEY missing).", 503, "ai_not_configured")
        try:
            import google.generativeai as genai
        except ImportError as exc:
            raise AppError("The google-generativeai package isn't installed on the server.", 503, "ai_not_configured") from exc
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.genai = genai

    def complete(self, system: str, prompt: str, max_tokens: int = 1000) -> str:
        model = self.genai.GenerativeModel("gemini-1.5-flash", system_instruction=system)
        resp = model.generate_content(prompt, generation_config={"max_output_tokens": max_tokens})
        return resp.text

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [
            self.genai.embed_content(model="models/text-embedding-004", content=t)["embedding"] for t in texts
        ]


class GroqProvider(AIProvider):
    def __init__(self):
        if not settings.GROQ_API_KEY:
            raise AppError("Groq is not configured (GROQ_API_KEY missing).", 503, "ai_not_configured")
        try:
            from groq import Groq
        except ImportError as exc:
            raise AppError("The groq package isn't installed on the server.", 503, "ai_not_configured") from exc
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    def complete(self, system: str, prompt: str, max_tokens: int = 1000) -> str:
        resp = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content or ""

    def embed(self, texts: list[str]) -> list[list[float]]:
        # Groq doesn't currently serve an embeddings endpoint; RAG falls back
        # to the local TF-IDF-style retriever (see rag.py) when this raises.
        raise AppError("Groq does not provide an embeddings API; configure OpenAI or Gemini for embeddings.", 501, "not_supported")


_PROVIDERS = {"openai": OpenAIProvider, "gemini": GeminiProvider, "groq": GroqProvider}


def get_provider() -> AIProvider:
    cls = _PROVIDERS.get(settings.AI_PROVIDER)
    if not cls:
        raise AppError(f"Unknown AI provider '{settings.AI_PROVIDER}'.", 500, "bad_provider")
    return cls()
