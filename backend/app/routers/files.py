from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models.db import FileRecord, User, get_db
from app.services.auth import get_current_user
from app.services.storage import storage

router = APIRouter()


@router.get("")
def list_files(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    records = db.query(FileRecord).filter(FileRecord.user_id == user.id).order_by(FileRecord.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "name": r.original_filename,
            "type": r.file_type,
            "size_bytes": r.size_bytes,
            "tool_used": r.tool_used,
            "status": r.status,
            "created_at": r.created_at.isoformat(),
            "expires_at": r.expires_at.isoformat(),
        }
        for r in records
    ]


@router.delete("/{file_id}")
def delete_file(file_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = db.get(FileRecord, file_id)
    if not record or record.user_id != user.id:
        raise AppError("File not found.", 404, "not_found")
    storage.delete(record.storage_key)
    db.delete(record)
    db.commit()
    return {"deleted": True}
