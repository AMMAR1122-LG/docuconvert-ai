from __future__ import annotations

import datetime as dt

import bcrypt
from fastapi import Depends, Header
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AppError
from app.models.db import User, get_db

# Using bcrypt directly rather than through passlib: passlib's bcrypt
# backend has a known incompatibility with bcrypt>=4.1 (its self-test
# raises "password cannot be longer than 72 bytes" even for short
# passwords). bcrypt itself has no such issue.
_BCRYPT_MAX_BYTES = 72


def hash_password(password: str) -> str:
    pw_bytes = password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    return bcrypt.hashpw(pw_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    pw_bytes = password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    return bcrypt.checkpw(pw_bytes, hashed.encode("utf-8"))


def create_access_token(user_id: str) -> str:
    expire = dt.datetime.utcnow() + dt.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload["sub"]
    except JWTError as exc:
        raise AppError("Your session has expired. Please log in again.", 401, "invalid_token") from exc


def get_current_user(authorization: str | None = Header(default=None), db: Session = Depends(get_db)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise AppError("Authentication required.", 401, "not_authenticated")
    token = authorization.removeprefix("Bearer ").strip()
    user_id = decode_token(token)
    user = db.get(User, user_id)
    if not user:
        raise AppError("Account not found.", 401, "not_authenticated")
    return user


def get_optional_user(authorization: str | None = Header(default=None), db: Session = Depends(get_db)) -> User | None:
    if not authorization:
        return None
    try:
        return get_current_user(authorization, db)
    except AppError:
        return None
