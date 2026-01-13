from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from database import SessionLocal
import models
from routers.auth import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/latest")
def get_latest_activity(limit: int = 10, db: Session = Depends(get_db)):
    """
    Get the latest activity logs for all users.
    Useful for a public dashboard or admin view.
    """
    logs = db.query(models.ActivityLog).order_by(models.ActivityLog.created_at.desc()).limit(limit).all()
    
    result = []
    for log in logs:
        user_name = log.user.username if log.user else "Unknown"
        result.append({
            "id": log.id,
            "user_name": user_name,
            "action": log.action,
            "target_type": log.target_type,
            "target_id": log.target_id,
            "details": log.details,
            "time": log.created_at
        })
    return result

@router.get("/heatmap")
def get_activity_heatmap(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Get activity heatmap data for the current logged-in user.
    Groups activity counts by date.
    """
    # SQLite uses strftime for date formatting
    # For PostgreSQL, use date_trunc('day', ...) or cast to date
    # Assuming SQLite for now as per requirements
    
    # Query: SELECT date(created_at) as day, count(*) as count FROM activity_logs WHERE user_id = ? GROUP BY day
    
    # Using SQLAlchemy func.date for SQLite compatibility
    stats = db.query(
        func.date(models.ActivityLog.created_at).label('date'),
        func.count(models.ActivityLog.id).label('count')
    ).filter(
        models.ActivityLog.user_id == current_user.id
    ).group_by(
        func.date(models.ActivityLog.created_at)
    ).all()
    
    # Transform to dict: { "2023-01-01": 5, ... }
    heatmap_data = {str(stat.date): stat.count for stat in stats}
    return heatmap_data
