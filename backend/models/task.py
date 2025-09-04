import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, ARRAY
from datetime import datetime
from models.base import Base
from constants import Status, Priority

class Task(Base):
    __tablename__ = "tasks"
    task_uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=True, index=True)
    completed_date = Column(DateTime, nullable=True)
    tags = Column(ARRAY(String), nullable=True, index=True)
    status = Column(String, nullable=False, index=True)
    priority = Column(Integer, nullable=False, index=True)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.user_uuid"), nullable=True)
    deleted_date = Column(DateTime, nullable=True, index=True)
