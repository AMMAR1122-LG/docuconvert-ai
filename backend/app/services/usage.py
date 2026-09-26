from __future__ import annotations

import datetime as dt

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import QuotaExceeded
from app.models.db import UsageRecord, User


def _today_count(db: Session, *, user_id: str | None, ip_address: str | None, kind: str) -> int:
    since = dt.datetime.utcnow() - dt.timedelta(hours=24)
    q = db.query(func.count(UsageRecord.id)).filter(UsageRecord.created_at >= since, UsageRecord.kind == kind)
    q = q.filter(UsageRecord.user_id == user_id) if user_id else q.filter(UsageRecord.ip_address == ip_address)
    return q.scalar() or 0


def check_and_record(
    db: Session, *, user: User | None, ip_address: str, tool: str, kind: str = "conversion"
) -> None:
    """Raises QuotaExceeded if the caller is over their daily limit; otherwise records the usage."""
    if user and user.plan == "pro":
        limit = settings.RATE_LIMIT_PRO_PER_DAY
        used = _today_count(db, user_id=user.id, ip_address=None, kind=kind)
    elif user:
        limit = settings.RATE_LIMIT_FREE_PER_DAY
        used = _today_count(db, user_id=user.id, ip_address=None, kind=kind)
    else:
        limit = settings.RATE_LIMIT_ANON_PER_DAY
        used = _today_count(db, user_id=None, ip_address=ip_address, kind=kind)

    if used >= limit:
        raise QuotaExceeded()

    db.add(UsageRecord(
        user_id=user.id if user else None,
        ip_address=None if user else ip_address,
        tool=tool,
        kind=kind,
    ))
    db.commit()
