from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import SessionLocal
import models, schemas
from routers.docs import get_optional_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/api/search", response_model=List[schemas.SearchResult])
def search_documents(
    q: str = Query(..., min_length=1), 
    db: Session = Depends(get_db), 
    current_user: Optional[models.User] = Depends(get_optional_user)
):
    query = db.query(models.Document).filter(
        (models.Document.title.ilike(f"%{q}%")) | 
        (models.Document.content.ilike(f"%{q}%"))
    )
    
    if not current_user:
        query = query.filter(models.Document.is_public == True)
        
    documents = query.all()
    
    results = []
    for doc in documents:
        # Simple snippet generation
        snippet = doc.content[:200] + "..." if len(doc.content) > 200 else doc.content
        
        cat_name = None
        sub_name = None
        if doc.sub_category:
            sub_name = doc.sub_category.name
            if doc.sub_category.category:
                cat_name = doc.sub_category.category.name

        results.append(schemas.SearchResult(
            id=doc.id,
            title=doc.title,
            content=doc.content,
            snippet=snippet,
            category_name=cat_name,
            sub_category_name=sub_name,
            is_public=doc.is_public,
            updated_at=doc.updated_at
        ))
        
    return results
