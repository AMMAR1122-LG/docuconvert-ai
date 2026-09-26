"""
All configuration comes from environment variables (12-factor). Nothing
secret is hardcoded. See ../../.env.example for the full list.
"""
from __future__ import annotations

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- General ---
    ENV: str = "development"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # --- Auth ---
    JWT_SECRET: str = "dev-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None

    # --- Database ---
    DATABASE_URL: str = "sqlite:///./docuconvert.db"

    # --- File storage ---
    # Local disk by default for the MVP; STORAGE_BACKEND=s3 switches to
    # S3/R2 using the S3_* vars below (see app/services/storage.py).
    STORAGE_BACKEND: str = "local"
    LOCAL_STORAGE_DIR: str = "./storage"
    S3_ENDPOINT: str | None = None
    S3_ACCESS_KEY: str | None = None
    S3_SECRET_KEY: str | None = None
    S3_BUCKET: str | None = None
    S3_REGION: str = "auto"

    # --- File lifecycle ---
    FILE_RETENTION_MINUTES: int = 60  # auto-delete uploaded/result files after this window
    MAX_UPLOAD_MB_FREE: int = 10
    MAX_UPLOAD_MB_PRO: int = 100

    # --- AI providers (abstraction layer picks one at runtime) ---
    AI_PROVIDER: str = "openai"  # openai | gemini | groq
    OPENAI_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None

    # --- Payments ---
    STRIPE_SECRET_KEY: str | None = None
    STRIPE_WEBHOOK_SECRET: str | None = None

    # --- Rate limiting ---
    RATE_LIMIT_ANON_PER_DAY: int = 5
    RATE_LIMIT_FREE_PER_DAY: int = 5
    RATE_LIMIT_PRO_PER_DAY: int = 1000


settings = Settings()
Path(settings.LOCAL_STORAGE_DIR).mkdir(parents=True, exist_ok=True)
