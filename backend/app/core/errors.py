from __future__ import annotations


class AppError(Exception):
    """
    Raised anywhere in the app for an expected, user-facing failure
    (bad file, unsupported format, quota exceeded, etc.). The FastAPI
    handler in main.py turns this into a clean JSON error — never a
    raw traceback — per the "never expose raw backend errors" rule.
    """

    def __init__(self, detail: str, status_code: int = 400, code: str = "app_error"):
        self.detail = detail
        self.status_code = status_code
        self.code = code
        super().__init__(detail)


class UnsupportedFileType(AppError):
    def __init__(self, allowed: list[str]):
        super().__init__(
            detail=f"Unsupported file type. Allowed: {', '.join(allowed)}.",
            status_code=415,
            code="unsupported_file_type",
        )


class FileTooLarge(AppError):
    def __init__(self, max_mb: int):
        super().__init__(
            detail=f"File exceeds the {max_mb}MB limit for your plan.",
            status_code=413,
            code="file_too_large",
        )


class QuotaExceeded(AppError):
    def __init__(self):
        super().__init__(
            detail="You've reached your daily limit. Upgrade to Pro for more.",
            status_code=429,
            code="quota_exceeded",
        )
