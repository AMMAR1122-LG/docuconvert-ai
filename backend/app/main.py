"""
DocuConvert AI — FastAPI backend entrypoint.

This process serves the REST API described in the architecture docs.
CPU-heavy conversion work happens synchronously in these routes for the
MVP; see app/services/jobs.py for the seam where a real queue (Celery /
RQ + Redis) plugs in for Phase 2+ without changing the router contracts.
"""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.errors import AppError
from app.models.db import init_db
from app.routers import auth, pdf_tools, convert, files, usage, health, ai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("docuconvert")

app = FastAPI(
    title="DocuConvert AI API",
    version="0.1.0",
    description="REST API for document conversion, PDF tools, and AI document features.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(request, exc: AppError):
    """Never leak raw tracebacks/internal errors to the client (see product rule #33/#54)."""
    logger.warning("AppError on %s: %s", request.url.path, exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail, "code": exc.code})


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail, "code": "http_error"})


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"error": "Invalid request.", "code": "validation_error"})


@app.exception_handler(Exception)
async def unhandled_error_handler(request, exc: Exception):
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error": "We couldn't process this document. Please try another file.", "code": "internal_error"},
    )


app.include_router(health.router, tags=["health"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(pdf_tools.router, prefix="/api/pdf", tags=["pdf-tools"])
app.include_router(convert.router, prefix="/api", tags=["convert"])
app.include_router(files.router, prefix="/api/user/files", tags=["files"])
app.include_router(usage.router, prefix="/api/user", tags=["usage"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])


@app.on_event("startup")
def on_startup():
    init_db()
