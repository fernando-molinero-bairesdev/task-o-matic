from uuid import UUID
from sqlalchemy.orm import Session
from models.user import User
from datetime import datetime
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class UserService:
    """Service class for user-related operations."""
    
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, **kwargs) -> User:
        """Create a new user."""
        try:
            user = User(**kwargs)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            logger.info(f"User created: {user.username}")
            return user
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            self.db.rollback()
            raise

    def get_user(self, user_uuid: UUID) -> Optional[User]:
        """Get a user by UUID."""
        return self.db.query(User).filter(
            User.user_uuid == user_uuid, 
            User.deleted_date == None
        ).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username (case-insensitive)."""
        return self.db.query(User).filter(
            User.username.ilike(username.lower()),
            User.deleted_date == None
        ).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email (case-insensitive)."""
        return self.db.query(User).filter(
            User.email.ilike(email.lower()),
            User.deleted_date == None
        ).first()

    def get_users(self, skip: int = 0, limit: int = 10) -> List[User]:
        """Get all users with pagination."""
        return self.db.query(User).filter(
            User.deleted_date == None
        ).offset(skip).limit(limit).all()

    def update_user(self, user_uuid: UUID, **kwargs) -> Optional[User]:
        """Update a user by UUID."""
        try:
            user = self.get_user(user_uuid)
            if not user:
                return None
            
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            self.db.commit()
            self.db.refresh(user)
            logger.info(f"User updated: {user.username}")
            return user
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            self.db.rollback()
            raise

    def delete_user(self, user_uuid: UUID) -> Optional[User]:
        """Soft delete a user by UUID."""
        try:
            user = self.get_user(user_uuid)
            if not user:
                return None
            
            user.deleted_date = datetime.utcnow()
            self.db.commit()
            logger.info(f"User deleted: {user.username}")
            return user
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            self.db.rollback()
            raise

    def get_user_count(self) -> int:
        """Get total count of active users."""
        return self.db.query(User).filter(User.deleted_date == None).count()
