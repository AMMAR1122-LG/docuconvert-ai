# DocuConvert AI

An all-in-one online document and PDF toolkit: convert, compress, merge,
split, OCR, edit, and chat with documents using AI.

This is a working MVP, not a mockup. Every tool listed below as
"tested" was verified by actually running requests against a live
backend during development — see [What's been tested](#whats-been-tested-and-how).

---

## Project structure

```
/backend           FastAPI app — REST API + PDF/OCR/AI processing
/frontend          Next.js (TypeScript, Tailwind) — the website
/docker            Dockerfiles for backend, worker, frontend
docker-compose.yml Full local stack: postgres, redis, backend, frontend
.env.example       Every environment variable the app reads
```

## Quick start

### Option A — Docker Compose (closest to production)

```bash
cp .env.example .env      # fill in real secrets as needed
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000 (docs at /docs)

### Option B — Run locally without Docker

You'll need Python 3.12+, Node 22+, and, for full functionality,
**Tesseract OCR** and **LibreOffice** installed and on `PATH`
(`tesseract`, `soffice`). Without them, every tool still works except
OCR PDF and Word↔PDF, which fail with a clean "temporarily
unavailable" error rather than crashing.

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
cp .env.local.example .env.local   # point NEXT_PUBLIC_API_BASE at your backend
npm run dev
```

### Running the test suite

```bash
cd backend
pytest -v
```

10 tests, all passing as of this build — see `backend/tests/test_integration.py`.
Two are skipped automatically if `soffice`/`tesseract` aren't on `PATH`.

---

## What's implemented

### Backend — real, working PDF/document processing
Merge · Split (all-pages or custom ranges) · Compress (low/medium/high,
with honest before/after size reporting) · Rotate · Delete pages ·
Extract pages · Watermark · Password protect · Unlock · PDF→Text ·
PDF→JPG · JPG/PNG/WebP→PDF · PDF→Word · Word→PDF (via LibreOffice
headless) · PDF→Excel (table extraction) · PDF→PowerPoint
(page-image fallback) · OCR PDF (English/Arabic/Urdu, via Tesseract,
produces a genuinely searchable PDF with an invisible text layer)

### Auth
Email/password registration and login with bcrypt hashing and JWT
sessions. Google OAuth is stubbed (returns a clear 501) until
`GOOGLE_CLIENT_ID`/`SECRET` are set and the verification call is wired
in — see `backend/app/routers/auth.py`.

### AI / RAG pipeline
Real page-aware PDF chunking and a dependency-free TF-IDF + cosine
similarity retriever (no API key needed for retrieval itself — verified
against a real multi-chapter test PDF, correctly ranking the right
chapter for a topical query). The final answer-generation step calls
an abstracted LLM provider (OpenAI / Gemini / Groq — swap via
`AI_PROVIDER` and the matching `*_API_KEY`); with no key configured it
fails cleanly with a 503 rather than crashing, which is exactly what
was verified in this build. `/api/ai/chat`, `/api/ai/summarize`, and
`/api/ai/mcqs` are wired end-to-end.

### Frontend
Homepage, `/tools` (all tools, categorized), a config-driven dynamic
`/tools/[slug]` page that powers every live tool with the right
inputs (file count, compression level, rotation degrees, page ranges,
OCR language, etc.), `/ai`, `/pricing`, `/login` + `/signup` (wired to
the real auth API), `/dashboard` (fetches real usage from the API),
plus about/contact/security/privacy/terms/refund-policy/blog stub
pages, `sitemap.xml`, and `robots.txt`.

### Security & correctness details worth knowing about
- File type is validated by **sniffing actual file bytes** (magic
  numbers / ZIP-internal markers for Office formats), never by trusting
  the extension.
- Stored files get **randomized names**, never the original filename.
- Compress never claims a size reduction it didn't actually get — if
  re-encoding would make the file bigger, the original is returned
  unchanged.
- Wrong PDF passwords, corrupt files, and bad page ranges all return
  clean, specific error messages (never a raw traceback) — verified by
  deliberately triggering each case during testing.
- Per-plan daily rate limiting for anonymous, free, and pro tiers.

## What's stubbed or not started

- **Payments/Stripe** — `Payment` and `Subscription` tables exist;
  checkout/webhook endpoints are not implemented.
- **Admin panel** — no UI yet; `SystemSetting`, `ToolUsage`, `AuditLog`
  tables exist for it.
- **Ads system, i18n/RTL, Alembic migrations, S3 upload UI** — not
  built. `STORAGE_BACKEND=s3` in `app/services/storage.py` is real
  code but untested here (no live bucket to test against).
- **Background job queue** — conversions run synchronously in the
  request/response cycle, which is fine for the file sizes tested but
  won't scale to very large files or high concurrency. `docker/worker.Dockerfile`
  and the `worker` service in `docker-compose.yml` (behind the `queue`
  profile) are scaffolded for when this moves to Celery/RQ.
- **Malware scanning** — file-type validation is real; a
  ClamAV-style content scan is not implemented.

## What's been tested, and how

Every core tool was exercised with real generated files (a multi-page
PDF with embedded images, a genuinely "scanned" image-only PDF for
OCR, a real .docx) against a running FastAPI server, not just written
and assumed to work. In the process, two real bugs were found and
fixed:

1. **LibreOffice output-file collision** — the code that located
   LibreOffice's converted output was matching the *input* file
   sitting in the same temp directory, silently returning the wrong
   file. Fixed by matching on the output extension specifically.
2. **passlib/bcrypt incompatibility** — passlib's bcrypt backend has a
   known issue with bcrypt ≥ 4.1 that broke every password hash, even
   short ones. Fixed by calling the `bcrypt` library directly.

Both fixes are captured as regression tests in
`backend/tests/test_integration.py`.

## Environment variables

See `.env.example` at the repo root for the full list with comments.
Nothing is hardcoded — pricing, AI provider, storage backend, and rate
limits are all environment-driven.
