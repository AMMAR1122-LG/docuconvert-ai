from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models.db import User, get_db
from app.services.auth import create_access_token, get_current_user, hash_password, verify_password

router = APIRouter()


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class GoogleLoginRequest(BaseModel):
    id_token: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


def _user_out(user: User) -> dict:
    return {"id": user.id, "name": user.name, "email": user.email, "plan": user.plan, "email_verified": user.email_verified}


@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if len(payload.password) < 8:
        raise AppError("Password must be at least 8 characters.", 400, "weak_password")
    if db.query(User).filter(User.email == payload.email).first():
        raise AppError("An account with this email already exists.", 409, "email_taken")
    user = User(name=payload.name, email=payload.email, hashed_password=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    # TODO(production): send verification email via transactional email provider.
    return TokenResponse(access_token=create_access_token(user.id), user=_user_out(user))


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not user.hashed_password or not verify_password(payload.password, user.hashed_password):
        raise AppError("Incorrect email or password.", 401, "invalid_credentials")
    return TokenResponse(access_token=create_access_token(user.id), user=_user_out(user))


@router.post("/google", response_model=TokenResponse)
def google_login(payload: GoogleLoginRequest, db: Session = Depends(get_db)):
    """
    Verifies the Google ID token (via google-auth's id_token.verify_oauth2_token
    in production, using GOOGLE_CLIENT_ID from settings) and creates/logs in
    the user. Stubbed here since it requires live Google credentials.
    """
    raise AppError(
        "Google sign-in isn't configured in this environment. Set GOOGLE_CLIENT_ID/SECRET to enable it.",
        501,
        "not_configured",
    )


@router.post("/forgot-password")
def forgot_password(email: EmailStr, db: Session = Depends(get_db)):
    # Always return the same response whether or not the email exists, to avoid account enumeration.
    # TODO(production): generate a signed reset token and email it via the transactional provider.
    return {"message": "If an account exists for this email, a reset link has been sent."}


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return _user_out(user)
