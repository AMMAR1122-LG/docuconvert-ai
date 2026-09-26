from __future__ import annotations

import datetime as dt

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.db import FileRecord, UsageRecord, User, get_db
from app.services.auth import get_current_user

router = APIRouter()


@router.get("/usage")
def get_usage(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    since = dt.datetime.utcnow() - dt.timedelta(days=30)
    conversions = db.query(func.count(UsageRecord.id)).filter(
        UsageRecord.user_id == user.id, UsageRecord.kind == "conversion", UsageRecord.created_at >= since
    ).scalar() or 0
    ai_requests = db.query(func.count(UsageRecord.id)).filter(
        UsageRecord.user_id == user.id, UsageRecord.kind == "ai_request", UsageRecord.created_at >= since
    ).scalar() or 0
    storage_used = db.query(func.coalesce(func.sum(FileRecord.size_bytes), 0)).filter(
        FileRecord.user_id == user.id
    ).scalar() or 0

    return {
        "plan": user.plan,
        "conversions_last_30d": conversions,
        "ai_requests_last_30d": ai_requests,
        "storage_used_bytes": storage_used,
    }
