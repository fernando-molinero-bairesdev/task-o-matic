from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import tomli
from pathlib import Path
from services.user_service import UserService
from models.user import User

# Load configuration
config_path = Path(__file__).parent.parent / "config.toml"
with open(config_path, "rb") as f:
    config = tomli.load(f)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings from config
SECRET_KEY = config["auth"]["secret_key"]
ALGORITHM = config["auth"]["algorithm"]
ACCESS_TOKEN_EXPIRE_MINUTES = config["auth"]["access_token_expire_minutes"]

class AuthService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user by username and password."""
        user = self.user_service.get_user_by_username(username)
        if not user:
            return None
        if not self.verify_password(password, user.password):
            return None
        return user

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[dict]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return None
            return payload
        except JWTError:
            return None

    def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from JWT token."""
        payload = self.verify_token(token)
        if not payload:
            return None
        
        username = payload.get("sub")
        if not username:
            return None
            
        user = self.user_service.get_user_by_username(username)
        return user