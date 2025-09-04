from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class TaskCreate(BaseModel):
    title: str
    description: Optional[str]
    due_date: Optional[datetime]
    tags: Optional[List[str]]
    status: str
    priority: int
    assigned_to: Optional[UUID]

class TaskUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    due_date: Optional[datetime]
    tags: Optional[List[str]]
    status: Optional[str]
    priority: Optional[int]
    assigned_to: Optional[UUID]
    completed_date: Optional[datetime]

class TaskResponse(BaseModel):
    task_uuid: UUID
    title: str
    description: Optional[str]
    created_date: Optional[datetime]
    due_date: Optional[datetime]
    completed_date: Optional[datetime]
    tags: Optional[List[str]]
    status: str
    priority: int
    assigned_to: Optional[UUID]
    deleted_date: Optional[datetime]
