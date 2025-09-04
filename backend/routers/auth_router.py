from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from db import get_db
from services.user_service import UserService
from authorization.auth_service import AuthService
from authorization.dependencies import get_current_active_user
from dto.auth_dto import Token, UserRegister, UserResponse, UserLogin
from dependencies.rate_limit_dependencies import check_auth_rate_limit
from models.user import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/login-json", response_model=Token)
async def login_json(
    user_login: UserLogin,
    request: Request,
    db: Session = Depends(get_db),
    rate_limit: dict = Depends(check_auth_rate_limit)
):
    """JSON-only login endpoint for frontend applications."""
    try:
        user_service = UserService(db)
        auth_service = AuthService(user_service)
        
        # Authenticate user
        user = auth_service.authenticate_user(user_login.username, user_login.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        # Create access token
        access_token = auth_service.create_access_token(
            data={"sub": user.username, "user_id": str(user.user_uuid)}
        )
        
        logger.info(f"User {user.username} logged in successfully via JSON")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": auth_service.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "user_uuid": str(user.user_uuid),
                "username": user.username,
                "name": user.name,
                "email": user.email
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"JSON login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )

@router.post("/register", response_model=dict)
async def register_user(
    user_data: UserRegister,
    request: Request,
    db: Session = Depends(get_db),
    rate_limit: dict = Depends(check_auth_rate_limit)
):
    """Register a new user with comprehensive validation."""
    try:
        user_service = UserService(db)
        auth_service = AuthService(user_service)
        
        # Check if user already exists (case-insensitive)
        existing_user = user_service.get_user_by_username(user_data.username.lower())
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if email already exists
        existing_email = user_service.get_user_by_email(user_data.email.lower())
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user with hashed password
        hashed_password = auth_service.get_password_hash(user_data.password)
        
        user = user_service.create_user(
            username=user_data.username.lower(),
            email=user_data.email.lower(),
            name=user_data.name,
            password=hashed_password
        )
        
        logger.info(f"New user registered: {user.username}")
        
        return {
            "message": "User registered successfully",
            "user_id": str(user.user_uuid),
            "username": user.username,
            "email": user.email,
            "name": user.name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information without modified_date."""
    return UserResponse(
        user_uuid=current_user.user_uuid,
        username=current_user.username,
        name=current_user.name,
        email=current_user.email,
        created_date=current_user.created_date
    )

@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    rate_limit: dict = Depends(check_auth_rate_limit)
):
    """Refresh access token with rate limiting."""
    try:
        user_service = UserService(db)
        auth_service = AuthService(user_service)
        
        # Create new access token
        access_token = auth_service.create_access_token(
            data={"sub": current_user.username, "user_id": str(current_user.user_uuid)}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": auth_service.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during token refresh"
        )

@router.get("/rate-limit/status")
async def get_auth_rate_limit_status(request: Request):
    """Get current rate limit status for authentication endpoints."""
    from services.rate_limiter import rate_limiter
    info = await rate_limiter.get_rate_limit_info(request, "auth")
    return info