import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, DateTime
from datetime import datetime
from models.base import Base

class User(Base):
    __tablename__ = "users"
    user_uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)
    deleted_date = Column(DateTime, nullable=True, index=True)
