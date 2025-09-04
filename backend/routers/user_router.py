from fastapi import APIRouter, Depends, HTTPException
from db import get_db
from services.user_service import UserService
from models.user import User
from sqlalchemy.orm import Session
from typing import Optional, List
from dto.user_dto import UserCreate, UserUpdate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    service = UserService(db)
    created = service.create_user(**user.dict())
    return created

@router.get("/{user_uuid}", response_model=UserResponse)
def get_user(user_uuid: int, db: Session = Depends(get_db)):
    service = UserService(db)
    user = service.get_user(user_uuid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    service = UserService(db)
    return service.get_users(skip=skip, limit=limit)

@router.put("/{user_uuid}", response_model=UserResponse)
def update_user(user_uuid: int, user: UserUpdate, db: Session = Depends(get_db)):
    service = UserService(db)
    updated = service.update_user(user_uuid, **user.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated

@router.delete("/{user_uuid}", response_model=UserResponse)
def delete_user(user_uuid: int, db: Session = Depends(get_db)):
    service = UserService(db)
    deleted = service.delete_user(user_uuid)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return deleted
