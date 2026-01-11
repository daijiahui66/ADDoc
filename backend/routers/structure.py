from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import SessionLocal
import models, schemas
from routers.auth import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Categories ---

@router.post("/categories", response_model=schemas.CategoryOut)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_category = models.Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.get("/categories", response_model=List[schemas.CategoryOut])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categories = db.query(models.Category).order_by(models.Category.sort_order).offset(skip).limit(limit).all()
    return categories

@router.put("/categories/reorder")
def reorder_categories(request: schemas.ReorderRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    for index, cat_id in enumerate(request.ids):
        db.query(models.Category).filter(models.Category.id == cat_id).update({"sort_order": index})
    db.commit()
    return {"status": "success"}

@router.put("/categories/{category_id}", response_model=schemas.CategoryOut)
def update_category(category_id: int, category: schemas.CategoryUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    for key, value in category.model_dump().items():
        setattr(db_category, key, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category

@router.delete("/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(db_category)
    db.commit()
    return {"status": "success"}

# --- SubCategories ---

@router.post("/subcategories", response_model=schemas.SubCategoryOut)
def create_subcategory(subcategory: schemas.SubCategoryCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_subcategory = models.SubCategory(**subcategory.model_dump())
    db.add(db_subcategory)
    db.commit()
    db.refresh(db_subcategory)
    return db_subcategory

@router.put("/subcategories/reorder")
def reorder_subcategories(request: schemas.ReorderRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    for index, sub_id in enumerate(request.ids):
        db.query(models.SubCategory).filter(models.SubCategory.id == sub_id).update({"sort_order": index})
    db.commit()
    return {"status": "success"}

@router.put("/subcategories/{subcategory_id}", response_model=schemas.SubCategoryOut)
def update_subcategory(subcategory_id: int, subcategory: schemas.SubCategoryUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_subcategory = db.query(models.SubCategory).filter(models.SubCategory.id == subcategory_id).first()
    if not db_subcategory:
        raise HTTPException(status_code=404, detail="SubCategory not found")
    
    for key, value in subcategory.model_dump().items():
        setattr(db_subcategory, key, value)
    
    db.commit()
    db.refresh(db_subcategory)
    return db_subcategory

@router.delete("/subcategories/{subcategory_id}")
def delete_subcategory(subcategory_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_subcategory = db.query(models.SubCategory).filter(models.SubCategory.id == subcategory_id).first()
    if not db_subcategory:
        raise HTTPException(status_code=404, detail="SubCategory not found")
    db.delete(db_subcategory)
    db.commit()
    return {"status": "success"}

# --- Tree Structure ---

@router.get("/structure/tree", response_model=List[schemas.CategoryWithSubs])
def read_structure_tree(db: Session = Depends(get_db)):
    categories = db.query(models.Category).order_by(models.Category.sort_order).all()
    # Ensure subcategories and documents are sorted
    for cat in categories:
        cat.sub_categories.sort(key=lambda x: x.sort_order)
        for sub in cat.sub_categories:
            sub.documents.sort(key=lambda x: x.sort_order)
    return categories
