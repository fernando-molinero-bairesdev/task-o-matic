from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import timedelta
from authorization.auth_service import AuthService
from authorization.models import Token, UserLogin
from authorization.dependencies import get_auth_service, get_current_active_user
from services.user_service import UserService
from dto.user_dto import UserCreate, UserResponse
from db import get_db
from models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Register a new user."""
    # Check if user already exists
    user_service = UserService(db)
    existing_user = user_service.get_user_by_username(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Hash password and create user
    hashed_password = auth_service.get_password_hash(user_data.password)
    user_dict = user_data.dict()
    user_dict["password"] = hashed_password
    
    user = user_service.create_user(**user_dict)
    return user

@router.post("/login", response_model=Token)
def login_user(
    user_credentials: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Login user and return access token."""
    user = auth_service.authenticate_user(user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)  # From config
    access_token = auth_service.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
def logout_user():
    """Logout user (client-side token removal)."""
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user