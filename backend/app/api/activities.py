from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.core.database import get_db
from app.models.activity import ActivityLog

router = APIRouter(prefix="/activities", tags=["Activities"])

@router.get("")
def get_activity_logs(
    job_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Fetches real timestamped activity and event logs."""
    query = db.query(ActivityLog)
    if job_id:
        query = query.filter(ActivityLog.job_id == job_id)
    
    logs = query.order_by(ActivityLog.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": l.id,
            "job_id": l.job_id,
            "assignment_id": l.assignment_id,
            "event_type": l.event_type,
            "message": l.message,
            "severity": l.severity,
            "metadata": l.metadata_json,
            "created_at": l.created_at.isoformat() + "Z"
        }
        for l in logs
    ]
