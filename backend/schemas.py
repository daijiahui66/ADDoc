from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    role: str
    avatar: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

# Document Schemas
class DocumentBase(BaseModel):
    title: str
    content: str
    is_public: bool = True
    sub_category_id: int
    sort_order: Optional[int] = 0

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(DocumentBase):
    pass

class DocumentOut(DocumentBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime
    author: Optional[UserOut] = None
    category_name: Optional[str] = None
    sub_category_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# Reorder Schema
class ReorderRequest(BaseModel):
    ids: List[int]

# Category/SubCategory Schemas
class SubCategoryBase(BaseModel):
    name: str
    sort_order: Optional[int] = 0

class SubCategoryCreate(SubCategoryBase):
    category_id: int

class SubCategoryUpdate(SubCategoryBase):
    pass

class SubCategoryOut(SubCategoryBase):
    id: int
    category_id: int
    documents: List[DocumentOut] = []
    
    model_config = ConfigDict(from_attributes=True)

class CategoryBase(BaseModel):
    name: str
    sort_order: Optional[int] = 0

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

class CategoryWithSubs(CategoryOut):
    sub_categories: List[SubCategoryOut] = []

# Document Schemas
class DocumentBase(BaseModel):
    title: str
    content: str
    is_public: bool = True
    sub_category_id: int
    sort_order: Optional[int] = 0

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(DocumentBase):
    pass

class DocumentOut(DocumentBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime
    author: Optional[UserOut] = None
    category_name: Optional[str] = None
    sub_category_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# Search Response
class SearchResult(BaseModel):
    id: int
    title: str
    content: Optional[str] = None
    category_name: Optional[str] = None
    sub_category_name: Optional[str] = None
    snippet: Optional[str] = None
    is_public: bool
    updated_at: datetime
