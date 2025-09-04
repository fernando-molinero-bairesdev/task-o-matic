from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from config.settings import settings
from services.user_service import UserService
from models.user import User
import logging

logger = logging.getLogger(__name__)

class AuthService:
    """Authentication service for handling user authentication and JWT tokens."""
    
    def __init__(self, user_service: UserService):
        self.user_service = user_service
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        # Use settings values directly instead of instance attributes
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS
    
    @property
    def ACCESS_TOKEN_EXPIRE_MINUTES(self):
        """Property to maintain compatibility with existing code."""
        return self.access_token_expire_minutes
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        try:
            return self.pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def get_password_hash(self, password: str) -> str:
        """Generate password hash."""
        try:
            return self.pwd_context.hash(password)
        except Exception as e:
            logger.error(f"Password hashing error: {e}")
            raise ValueError("Failed to hash password")
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password."""
        try:
            user = self.user_service.get_user_by_username(username)
            if not user:
                logger.warning(f"User not found: {username}")
                return None
            
            if not self.verify_password(password, user.password):
                logger.warning(f"Invalid password for user: {username}")
                return None
                
            logger.info(f"User authenticated successfully: {username}")
            return user
        except Exception as e:
            logger.error(f"Authentication error for user {username}: {e}")
            return None
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        try:
            to_encode = data.copy()
            
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
            
            to_encode.update({
                "exp": expire,
                "iat": datetime.utcnow(),
                "type": "access"
            })
            
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            logger.debug(f"Access token created for: {data.get('sub', 'unknown')}")
            return encoded_jwt
        except Exception as e:
            logger.error(f"Token creation error: {e}")
            raise ValueError("Failed to create access token")
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check if token is expired
            exp = payload.get("exp")
            if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
                raise JWTError("Token expired")
            
            # Validate token type
            token_type = payload.get("type", "access")
            if token_type != "access":
                raise JWTError("Invalid token type")
            
            return payload
        except JWTError as e:
            logger.warning(f"Token verification failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected token verification error: {e}")
            raise JWTError("Token verification failed")
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token."""
        try:
            to_encode = data.copy()
            expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
            
            to_encode.update({
                "exp": expire,
                "iat": datetime.utcnow(),
                "type": "refresh"
            })
            
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            logger.debug(f"Refresh token created for: {data.get('sub', 'unknown')}")
            return encoded_jwt
        except Exception as e:
            logger.error(f"Refresh token creation error: {e}")
            raise ValueError("Failed to create refresh token")
    
    def verify_refresh_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT refresh token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check if token is expired
            exp = payload.get("exp")
            if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
                raise JWTError("Refresh token expired")
            
            # Validate token type
            token_type = payload.get("type")
            if token_type != "refresh":
                raise JWTError("Invalid token type - expected refresh token")
            
            return payload
        except JWTError as e:
            logger.warning(f"Refresh token verification failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected refresh token verification error: {e}")
            raise JWTError("Refresh token verification failed")
    
    def decode_token_payload(self, token: str, verify_exp: bool = True) -> Dict[str, Any]:
        """Decode token payload without full verification (useful for expired tokens)."""
        try:
            options = {"verify_exp": verify_exp}
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                options=options
            )
            return payload
        except Exception as e:
            logger.error(f"Token payload decode error: {e}")
            raise JWTError("Failed to decode token payload")
    
    def is_token_expired(self, token: str) -> bool:
        """Check if token is expired without raising an exception."""
        try:
            payload = self.decode_token_payload(token, verify_exp=False)
            exp = payload.get("exp")
            if exp:
                return datetime.utcnow() > datetime.fromtimestamp(exp)
            return True  # No expiration time means invalid token
        except Exception:
            return True  # If we can't decode, consider it expired
    
    def get_token_subject(self, token: str) -> Optional[str]:
        """Get the subject (username) from token without full verification."""
        try:
            payload = self.decode_token_payload(token, verify_exp=False)
            return payload.get("sub")
        except Exception:
            return None

    def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from JWT token."""
        try:
            # Verify the token and get payload
            payload = self.verify_token(token)
            username = payload.get("sub")
            
            if not username:
                logger.warning("No username in token payload")
                return None
            
            # Get user from database
            user = self.user_service.get_user_by_username(username)
            if not user:
                logger.warning(f"User not found in database: {username}")
                return None
            
            # Check if user is not deleted
            if user.deleted_date:
                logger.warning(f"User is deleted: {username}")
                return None
            
            return user
        except JWTError as e:
            logger.warning(f"JWT error in get_current_user: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in get_current_user: {e}")
            return None