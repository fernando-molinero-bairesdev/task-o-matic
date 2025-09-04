from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.orm import Session
from typing import List
from db import get_db
from services.user_service import UserService
from models.user import User
from dto.user_dto import UserCreate, UserUpdate, UserResponse
from authorization.dependencies import get_current_active_user

router = APIRouter(tags=["users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new user (admin only)."""
    service = UserService(db)
    
    # Check if user already exists
    existing_user = service.get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    existing_email = service.get_user_by_email(user.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    created = service.create_user(**user.model_dump())
    return created

@router.get("/{user_uuid}", response_model=UserResponse)
def get_user(
    user_uuid: UUID, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a user by UUID."""
    service = UserService(db)
    user = service.get_user(user_uuid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    return user

@router.get("/", response_model=List[UserResponse])
def get_users(
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all users with pagination."""
    service = UserService(db)
    return service.get_users(skip=skip, limit=limit)

@router.put("/{user_uuid}", response_model=UserResponse)
def update_user(
    user_uuid: UUID, 
    user: UserUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a user by UUID."""
    service = UserService(db)
    
    # Get the user to update
    existing_user = service.get_user(user_uuid)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    
    # Check for conflicts if updating username or email
    update_data = user.model_dump(exclude_unset=True)
    
    if "username" in update_data:
        username_check = service.get_user_by_username(update_data["username"])
        if username_check and username_check.user_uuid != user_uuid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    if "email" in update_data:
        email_check = service.get_user_by_email(update_data["email"])
        if email_check and email_check.user_uuid != user_uuid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already taken"
            )
    
    updated = service.update_user(user_uuid, **update_data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    return updated

@router.delete("/{user_uuid}", response_model=UserResponse)
def delete_user(
    user_uuid: UUID, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Soft delete a user by UUID."""
    service = UserService(db)
    deleted = service.delete_user(user_uuid)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    return deleted

@router.get("/me/profile", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's profile."""
    return current_user

@router.put("/me/profile", response_model=UserResponse)
def update_current_user_profile(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update current user's profile."""
    service = UserService(db)
    
    # Check for conflicts if updating username or email
    update_data = user_update.model_dump(exclude_unset=True)
    
    if "username" in update_data:
        username_check = service.get_user_by_username(update_data["username"])
        if username_check and username_check.user_uuid != current_user.user_uuid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    if "email" in update_data:
        email_check = service.get_user_by_email(update_data["email"])
        if email_check and email_check.user_uuid != current_user.user_uuid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already taken"
            )
    
    updated = service.update_user(current_user.user_uuid, **update_data)
    return updated
