from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, create_engine,
)
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


def _uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=_uuid)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=True)  # null for OAuth-only accounts
    google_id = Column(String, unique=True, nullable=True)
    email_verified = Column(Boolean, default=False)
    plan = Column(String, default="free")  # free | pro
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    subscriptions = relationship("Subscription", back_populates="user")
    files = relationship("FileRecord", back_populates="user")


class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(String, primary_key=True, default=_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    plan = Column(String, nullable=False)  # pro_monthly | pro_annual
    status = Column(String, default="active")  # active | canceled | past_due
    stripe_subscription_id = Column(String, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    user = relationship("User", back_populates="subscriptions")


class FileRecord(Base):
    __tablename__ = "files"
    id = Column(String, primary_key=True, default=_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)  # nullable: anonymous usage allowed
    storage_key = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    size_bytes = Column(Integer, nullable=False)
    tool_used = Column(String, nullable=False)
    status = Column(String, default="ready")  # uploading | processing | ready | failed
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="files")


class ConversionJob(Base):
    __tablename__ = "conversion_jobs"
    id = Column(String, primary_key=True, default=_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    tool = Column(String, nullable=False)
    status = Column(String, default="queued")  # queued | processing | complete | failed
    error_message = Column(String, nullable=True)
    input_file_id = Column(String, ForeignKey("files.id"), nullable=True)
    output_file_id = Column(String, ForeignKey("files.id"), nullable=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class UsageRecord(Base):
    __tablename__ = "usage_records"
    id = Column(String, primary_key=True, default=_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    ip_address = Column(String, nullable=True)  # for anonymous rate limiting
    tool = Column(String, nullable=False)
    kind = Column(String, nullable=False)  # conversion | ai_request
    created_at = Column(DateTime, default=dt.datetime.utcnow)


class AIConversation(Base):
    __tablename__ = "ai_conversations"
    id = Column(String, primary_key=True, default=_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    file_id = Column(String, ForeignKey("files.id"), nullable=True)
    title = Column(String, default="New conversation")
    created_at = Column(DateTime, default=dt.datetime.utcnow)


class AIMessage(Base):
    __tablename__ = "ai_messages"
    id = Column(String, primary_key=True, default=_uuid)
    conversation_id = Column(String, ForeignKey("ai_conversations.id"), nullable=False)
    role = Column(String, nullable=False)  # user | assistant
    content = Column(Text, nullable=False)
    citations = Column(Text, nullable=True)  # JSON-encoded list of {page, snippet}
    created_at = Column(DateTime, default=dt.datetime.utcnow)


class Payment(Base):
    __tablename__ = "payments"
    id = Column(String, primary_key=True, default=_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    stripe_payment_id = Column(String, nullable=True)
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String, default="usd")
    status = Column(String, nullable=False)
    created_at = Column(DateTime, default=dt.datetime.utcnow)


class BlogPost(Base):
    __tablename__ = "blog_posts"
    id = Column(String, primary_key=True, default=_uuid)
    slug = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False)
    content_md = Column(Text, nullable=False)
    published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=dt.datetime.utcnow)


class ToolUsage(Base):
    __tablename__ = "tool_usage"
    id = Column(String, primary_key=True, default=_uuid)
    tool = Column(String, nullable=False)
    date = Column(String, nullable=False)  # YYYY-MM-DD, aggregated daily
    count = Column(Integer, default=0)


class SystemSetting(Base):
    __tablename__ = "system_settings"
    key = Column(String, primary_key=True)
    value = Column(String, nullable=False)  # JSON-encoded; used for admin-configurable pricing, tool enable/disable


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String, primary_key=True, default=_uuid)
    actor_id = Column(String, nullable=True)
    action = Column(String, nullable=False)
    detail = Column(Text, nullable=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)


engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
