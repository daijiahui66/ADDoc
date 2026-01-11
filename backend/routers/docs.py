from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from database import SessionLocal
import models, schemas
from routers.auth import get_current_user, oauth2_scheme
from jose import jwt, JWTError
import auth_utils

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user_optional(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[models.User]:
    # This is a bit tricky because oauth2_scheme raises 401 if no token.
    # For optional auth, we might need a custom dependency or just handle the error in the caller 
    # if we change how we retrieve the token (e.g. from header manually).
    # However, FastAPI's OAuth2PasswordBearer is strict. 
    # Let's try to get user if token exists, else return None.
    # But Depends(oauth2_scheme) will fail if no header.
    # So we define a lenient dependency.
    return None

# Custom lenient dependency for optional auth
from fastapi.security import OAuth2PasswordBearer
from fastapi import Request

oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

async def get_optional_user(token: Optional[str] = Depends(oauth2_scheme_optional), db: Session = Depends(get_db)) -> Optional[models.User]:
    if not token:
        return None
    try:
        payload = jwt.decode(token, auth_utils.SECRET_KEY, algorithms=[auth_utils.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
    user = db.query(models.User).filter(models.User.username == username).first()
    return user


@router.get("/activity/latest", response_model=List[schemas.DocumentOut])
def get_recent_activity(
    limit: int = 10, 
    db: Session = Depends(get_db), 
    current_user: Optional[models.User] = Depends(get_optional_user)
):
    query = db.query(models.Document).order_by(models.Document.updated_at.desc())
    
    # If not logged in, filter only public
    if not current_user:
        query = query.filter(models.Document.is_public == True)
        
    documents = query.limit(limit).all()
    
    # Enrich with category info to avoid 422 if client expects it
    for doc in documents:
        # Initialize with None/Empty to prevent Pydantic validation errors
        doc.sub_category_name = None
        doc.category_name = None
        
        if doc.sub_category:
            doc.sub_category_name = doc.sub_category.name
            if doc.sub_category.category:
                doc.category_name = doc.sub_category.category.name
                
    return documents

@router.post("/docs", response_model=schemas.DocumentOut)
def create_document(document: schemas.DocumentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_document = models.Document(**document.model_dump(), author_id=current_user.id)
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    # Enrich with category info to avoid 422 if client expects it
    db_document.sub_category_name = None
    db_document.category_name = None
    
    if db_document.sub_category:
        db_document.sub_category_name = db_document.sub_category.name
        if db_document.sub_category.category:
            db_document.category_name = db_document.sub_category.category.name
            
    return db_document

@router.get("/docs/{doc_id}", response_model=schemas.DocumentOut)
def read_document(doc_id: int, db: Session = Depends(get_db), current_user: Optional[models.User] = Depends(get_optional_user)):
    document = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not document.is_public and not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated to view this document")
    
    # Enrich with category info
    document.sub_category_name = None
    document.category_name = None
    
    if document.sub_category:
        document.sub_category_name = document.sub_category.name
        if document.sub_category.category:
            document.category_name = document.sub_category.category.name
    
    return document

@router.put("/docs/reorder")
def reorder_documents(request: schemas.ReorderRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    for index, doc_id in enumerate(request.ids):
        db.query(models.Document).filter(models.Document.id == doc_id).update({"sort_order": index})
    db.commit()
    return {"status": "success"}

@router.put("/docs/{doc_id}", response_model=schemas.DocumentOut)
def update_document(doc_id: int, document: schemas.DocumentUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_document = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Optional: Check if user is author or admin
    if db_document.author_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to edit this document")

    for key, value in document.model_dump().items():
        setattr(db_document, key, value)
    
    db.commit()
    db.refresh(db_document)
    return db_document

@router.delete("/docs/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_document = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if db_document.author_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this document")

    db.delete(db_document)
    db.commit()
    return {"status": "success"}
