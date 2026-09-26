"""
Storage abstraction so the rest of the app never talks to boto3 or the
filesystem directly. STORAGE_BACKEND=local writes to disk (good for
running the MVP without any cloud account); STORAGE_BACKEND=s3 talks to
S3 or Cloudflare R2 (R2 is S3-compatible, so the same client works —
just point S3_ENDPOINT at the R2 endpoint).

Every stored file gets a randomized name (never the user's original
filename) and is tracked for automatic deletion after
settings.FILE_RETENTION_MINUTES.
"""
from __future__ import annotations

import io
import secrets
import time
from dataclasses import dataclass
from pathlib import Path

from app.core.config import settings

try:
    import boto3
except ImportError:  # boto3 is only required when STORAGE_BACKEND=s3
    boto3 = None


@dataclass
class StoredFile:
    key: str
    size_bytes: int
    expires_at: float  # unix timestamp


def random_key(suffix: str) -> str:
    return f"{secrets.token_urlsafe(24)}{suffix}"


class LocalStorage:
    def __init__(self):
        self.root = Path(settings.LOCAL_STORAGE_DIR)
        self.root.mkdir(parents=True, exist_ok=True)

    def put(self, data: bytes, suffix: str = "") -> StoredFile:
        key = random_key(suffix)
        (self.root / key).write_bytes(data)
        expires_at = time.time() + settings.FILE_RETENTION_MINUTES * 60
        return StoredFile(key=key, size_bytes=len(data), expires_at=expires_at)

    def get(self, key: str) -> bytes:
        return (self.root / key).read_bytes()

    def delete(self, key: str) -> None:
        path = self.root / key
        if path.exists():
            path.unlink()

    def sweep_expired(self, registry: dict[str, float]) -> list[str]:
        """Delete anything past its retention window. registry maps key -> expires_at."""
        now = time.time()
        expired = [k for k, exp in registry.items() if exp <= now]
        for k in expired:
            self.delete(k)
        return expired


class S3Storage:
    def __init__(self):
        if boto3 is None:
            raise RuntimeError("boto3 is required for STORAGE_BACKEND=s3 (pip install boto3)")
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
        )
        self.bucket = settings.S3_BUCKET

    def put(self, data: bytes, suffix: str = "") -> StoredFile:
        key = random_key(suffix)
        self.client.upload_fileobj(io.BytesIO(data), self.bucket, key)
        expires_at = time.time() + settings.FILE_RETENTION_MINUTES * 60
        return StoredFile(key=key, size_bytes=len(data), expires_at=expires_at)

    def get(self, key: str) -> bytes:
        buf = io.BytesIO()
        self.client.download_fileobj(self.bucket, key, buf)
        return buf.getvalue()

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)


def get_storage():
    if settings.STORAGE_BACKEND == "s3":
        return S3Storage()
    return LocalStorage()


storage = get_storage()
