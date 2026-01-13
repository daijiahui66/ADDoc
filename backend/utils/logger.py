from sqlalchemy.orm import Session
from models import ActivityLog

def log_activity(db: Session, user_id: int, action: str, target_id: int, target_type: str, details: str = None):
    try:
        activity = ActivityLog(
            user_id=user_id,
            action=action,
            target_id=target_id,
            target_type=target_type,
            details=details
        )
        db.add(activity)
        db.commit()
    except Exception as e:
        print(f"Failed to log activity: {e}")
        db.rollback()
