from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from uuid import UUID
import re

class UserLogin(BaseModel):
    """User login request model for JSON requests."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)

class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str
    expires_in: int
    user: Optional[dict] = None

class UserRegister(BaseModel):
    """User registration request model with validation."""
    username: str = Field(
        ..., 
        min_length=3, 
        max_length=50, 
        description="Unique username (3-50 characters)"
    )
    email: EmailStr = Field(..., description="Valid email address")
    name: str = Field(
        ..., 
        min_length=2, 
        max_length=100, 
        description="Full name (2-100 characters)"
    )
    password: str = Field(
        ..., 
        min_length=6, 
        max_length=100, 
        description="Password (6-100 characters)"
    )

    @validator('username')
    def validate_username(cls, v):
        """Validate username format."""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')
        return v.lower()  # Convert to lowercase for consistency

    @validator('name')
    def validate_name(cls, v):
        """Validate name format."""
        if not v.strip():
            raise ValueError('Name cannot be empty or just whitespace')
        return v.strip()

    @validator('password')
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v

class UserResponse(BaseModel):
    """User response model without modified_date."""
    user_uuid: UUID
    username: str
    name: str
    email: str
    created_date: datetime
    
    class Config:
        from_attributes = True

class TokenData(BaseModel):
    """Token data model for internal use."""
    username: Optional[str] = None
    user_id: Optional[str] = None