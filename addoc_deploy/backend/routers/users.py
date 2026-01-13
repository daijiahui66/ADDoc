from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List
from database import SessionLocal
import models, schemas, auth_utils
from routers.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_admin(current_user: models.User):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

@router.get("/", response_model=List[schemas.UserOut])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    check_admin(current_user)
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@router.post("/", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    check_admin(current_user)
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = auth_utils.get_password_hash(user.password)
    new_user = models.User(username=user.username, password_hash=hashed_password, role="user")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.put("/{user_id}/password")
def reset_password(user_id: int, password: str = Body(..., embed=True), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    check_admin(current_user)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.password_hash = auth_utils.get_password_hash(password)
    db.commit()
    return {"status": "success", "message": "Password updated"}

@router.put("/{user_id}/role")
def update_role(user_id: int, role: str = Body(..., embed=True), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    check_admin(current_user)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Protection for super-admin
    if user.username == "admin":
        raise HTTPException(status_code=403, detail="Operation not allowed on super-admin")

    if role not in ["admin", "user"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    user.role = role
    db.commit()
    return {"status": "success", "message": "Role updated"}

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    check_admin(current_user)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Protection for super-admin
    if user.username == "admin":
        raise HTTPException(status_code=403, detail="Operation not allowed on super-admin")

    db.delete(user)
    db.commit()
    return {"status": "success"}

@router.put("/me/password")
def update_me_password(password: str = Body(..., embed=True), current_password: str = Body(..., embed=True), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if not auth_utils.verify_password(current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    current_user.password_hash = auth_utils.get_password_hash(password)
    db.commit()
    return {"status": "success", "message": "Password updated"}
