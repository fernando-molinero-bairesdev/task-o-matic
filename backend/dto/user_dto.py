from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class UserCreate(BaseModel):
    """User creation request model."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=6, max_length=100)

class UserUpdate(BaseModel):
    """User update request model."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=2, max_length=100)

class UserResponse(BaseModel):
    """User response model for API responses."""
    user_uuid: UUID
    username: str
    name: str
    email: str
    created_date: datetime
    
    class Config:
        from_attributes = True

class UserList(BaseModel):
    """User list response model."""
    users: list[UserResponse]
    total: int
    skip: int
    limit: int
