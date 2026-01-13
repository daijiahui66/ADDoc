from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
import models

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total_docs = db.query(models.Document).count()
    public_docs = db.query(models.Document).filter(models.Document.is_public == True).count()
    private_docs = db.query(models.Document).filter(models.Document.is_public == False).count()
    total_users = db.query(models.User).count()
    
    return {
        "total_docs": total_docs,
        "public_docs": public_docs,
        "private_docs": private_docs,
        "total_users": total_users
    }
