from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    name: str
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]

class UserResponse(BaseModel):
    user_uuid: UUID
    username: str
    name: str
    email: EmailStr
    created_date: Optional[datetime]
    deleted_date: Optional[datetime]
