from __future__ import annotations

import json

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.db import User, get_db
from app.services.ai.chunking import extract_pdf_chunks
from app.services.ai.rag import answer_question, build_index
from app.services.auth import get_optional_user
from app.services.usage import check_and_record
from app.services.validation import validate_upload

router = APIRouter()


def _max_mb(user: User | None) -> int:
    return settings.MAX_UPLOAD_MB_PRO if (user and user.plan == "pro") else settings.MAX_UPLOAD_MB_FREE


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


@router.post("/chat")
async def chat(
    request: Request,
    question: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    """
    Full RAG pipeline on a single request for simplicity: PDF -> chunk -> TF-IDF
    index -> retrieve top matches for the question -> LLM answer with page
    citations. A production build would persist the index per file_id
    (AIConversation/AIMessage tables already model this) so repeat questions
    don't re-chunk the PDF; that's a straightforward follow-up, not a
    pipeline change.
    """
    check_and_record(db, user=user, ip_address=_client_ip(request), tool="ai-pdf-chat", kind="ai_request")
    data = await file.read()
    validate_upload(data, ["pdf"], _max_mb(user))
    index = build_index(data)
    result = answer_question(index, question)
    return result


@router.post("/summarize")
async def summarize(
    request: Request,
    length: str = Form("medium"),  # short | medium | detailed
    format: str = Form("paragraphs"),  # paragraphs | bullets | key_takeaways
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    check_and_record(db, user=user, ip_address=_client_ip(request), tool="ai-summarize", kind="ai_request")
    data = await file.read()
    validate_upload(data, ["pdf"], _max_mb(user))
    chunks = extract_pdf_chunks(data)
    full_text = "\n\n".join(c.text for c in chunks)[:12000]  # keep prompt bounded

    length_map = {"short": "in 3-4 sentences", "medium": "in 2-3 short paragraphs", "detailed": "in detail, covering every major section"}
    format_map = {"paragraphs": "as flowing paragraphs", "bullets": "as bullet points", "key_takeaways": "as a short list of key takeaways"}

    from app.services.ai.providers import get_provider
    provider = get_provider()
    prompt = (
        f"Summarize the following document {length_map.get(length, length_map['medium'])}, "
        f"formatted {format_map.get(format, format_map['paragraphs'])}. "
        f"Base the summary only on this text:\n\n{full_text}"
    )
    summary = provider.complete("You are a precise document summarizer. Never invent facts not in the source text.", prompt, max_tokens=1200)
    return {"summary": summary}


@router.post("/mcqs")
async def generate_mcqs(
    request: Request,
    count: int = Form(10),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    check_and_record(db, user=user, ip_address=_client_ip(request), tool="ai-mcqs", kind="ai_request")
    data = await file.read()
    validate_upload(data, ["pdf"], _max_mb(user))
    chunks = extract_pdf_chunks(data)
    full_text = "\n\n".join(c.text for c in chunks)[:12000]

    from app.services.ai.providers import get_provider
    provider = get_provider()
    system = (
        "You generate multiple-choice questions strictly from the provided text. "
        "Respond ONLY with a JSON array, no preamble, no markdown fences. Each item: "
        '{"question": str, "options": {"A": str, "B": str, "C": str, "D": str}, '
        '"correct_answer": "A"|"B"|"C"|"D", "explanation": str}'
    )
    prompt = f"Generate {count} multiple-choice questions from this text:\n\n{full_text}"
    raw = provider.complete(system, prompt, max_tokens=2000)
    try:
        questions = json.loads(raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```"))
    except json.JSONDecodeError:
        questions = []
    return {"questions": questions}
