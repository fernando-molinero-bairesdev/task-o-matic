from models.user import User
from sqlalchemy.orm import Session
from datetime import datetime

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, **kwargs):
        user = User(**kwargs)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user(self, user_uuid):
        return self.db.query(User).filter(User.user_uuid == user_uuid, User.deleted_date == None).first()

    def get_user_by_username(self, username):
        return self.db.query(User).filter(User.username == username, User.deleted_date == None).first()

    def get_users(self, skip=0, limit=10):
        return self.db.query(User).filter(User.deleted_date == None).offset(skip).limit(limit).all()

    def update_user(self, user_uuid, **kwargs):
        user = self.db.query(User).filter(User.user_uuid == user_uuid, User.deleted_date == None).first()
        if not user:
            return None
        for key, value in kwargs.items():
            setattr(user, key, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_uuid):
        user = self.db.query(User).filter(User.user_uuid == user_uuid, User.deleted_date == None).first()
        if not user:
            return None
        user.deleted_date = datetime.utcnow()
        self.db.commit()
        return user
