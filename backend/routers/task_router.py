from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from db import get_db
from services.task_service import TaskService
from models.task import Status, Priority
from dto.task_dto import TaskCreate, TaskUpdate, TaskResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/tasks", tags=["tasks"])

    # TaskCreate, TaskUpdate, and TaskResponse are now imported from the DTO module


    # The above classes have been removed as they are now imported

@router.post("/", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    service = TaskService(db)
    created = service.create_task(**task.dict())
    return created

@router.get("/", response_model=List[TaskResponse])
def get_tasks(skip: int = 0, limit: int = 10, status: Optional[str] = None, due_date: Optional[str] = None, db: Session = Depends(get_db)):
    service = TaskService(db)
    return service.get_tasks(skip=skip, limit=limit, status=status, due_date=due_date)

@router.put("/{task_uuid}", response_model=TaskResponse)
def update_task(task_uuid: str, task: TaskUpdate, db: Session = Depends(get_db)):
    service = TaskService(db)
    updated = service.update_task(task_uuid, **task.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated

@router.delete("/{task_uuid}", response_model=TaskResponse)
def delete_task(task_uuid: str, db: Session = Depends(get_db)):
    service = TaskService(db)
    deleted = service.delete_task(task_uuid)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return deleted

@router.post("/{task_uuid}/assign", response_model=TaskResponse)
def assign_task(task_uuid: str, user_uuid: UUID, db: Session = Depends(get_db)):
    service = TaskService(db)
    assigned = service.assign_task(task_uuid, user_uuid)
    if not assigned:
        raise HTTPException(status_code=404, detail="Task not found")
    return assigned

@router.post("/{task_uuid}/complete", response_model=TaskResponse)
def mark_task_completed(task_uuid: UUID, db: Session = Depends(get_db)):
    service = TaskService(db)
    completed = service.mark_task_completed(task_uuid)
    if not completed:
        raise HTTPException(status_code=404, detail="Task not found")
    return completed
