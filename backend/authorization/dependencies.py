from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from authorization.auth_service import AuthService
from services.user_service import UserService
from db import get_db
from models.user import User
from sqlalchemy.orm import Session

security = HTTPBearer()

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Dependency to get AuthService instance."""
    user_service = UserService(db)
    return AuthService(user_service)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """Dependency to get current authenticated user."""
    token = credentials.credentials
    user = auth_service.get_current_user(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to get current active (non-deleted) user."""
    if current_user.deleted_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user