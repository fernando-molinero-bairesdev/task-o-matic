from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from db import get_db
from services.task_service import TaskService
from models.task import Status, Priority
from models.user import User
from authorization.dependencies import get_current_active_user
from dto.task_dto import TaskCreate, TaskUpdate, TaskResponse
from constants import Status as TaskStatus
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from dependencies.rate_limit_dependencies import (
    check_tasks_read_rate_limit,
    check_tasks_write_rate_limit, 
    check_tasks_delete_rate_limit
)

# Remove the prefix here since it's set in main.py
router = APIRouter(tags=["tasks"])

# DTO for task assignment
class TaskAssignmentRequest(BaseModel):
    user_uuid: Optional[UUID] = None

@router.get("/statuses", response_model=Dict[str, str])
def get_task_statuses(
    request: Request,
    rate_limit: dict = Depends(check_tasks_read_rate_limit)
):
    """Get all available task statuses for filtering."""
    return {
        "TO_DO": TaskStatus.TO_DO,
        "IN_PROGRESS": TaskStatus.IN_PROGRESS,
        "DONE": TaskStatus.DONE
    }

@router.post("/", response_model=TaskResponse)
def create_task(
    task: TaskCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    rate_limit: dict = Depends(check_tasks_write_rate_limit)
):
    """Create a new task with rate limiting."""
    service = TaskService(db)
    created = service.create_task(**task.dict())
    return created

@router.get("/", response_model=List[TaskResponse])
def get_tasks(
    request: Request,
    skip: int = 0, 
    limit: int = 10, 
    status: Optional[str] = None, 
    due_date_from: Optional[str] = None,
    due_date_to: Optional[str] = None,
    assigned_to_me: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    rate_limit: dict = Depends(check_tasks_read_rate_limit)
):
    """Get tasks with filtering options and rate limiting."""
    service = TaskService(db)
    filters = {}
    
    if status:
        filters['status'] = status
    if due_date_from:
        filters['due_date_from'] = due_date_from
    if due_date_to:
        filters['due_date_to'] = due_date_to
    if assigned_to_me:
        filters['assigned_to'] = current_user.user_uuid
    
    return service.get_tasks_filtered(
        skip=skip, 
        limit=limit, 
        **filters
    )

@router.get("/{task_uuid}", response_model=TaskResponse)
def get_task(
    task_uuid: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    rate_limit: dict = Depends(check_tasks_read_rate_limit)
):
    """Get a specific task with rate limiting."""
    service = TaskService(db)
    task = service.get_task(task_uuid)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_uuid}", response_model=TaskResponse)
def update_task(
    task_uuid: UUID,
    task: TaskUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    rate_limit: dict = Depends(check_tasks_write_rate_limit)
):
    """Update a task with rate limiting."""
    service = TaskService(db)
    updated = service.update_task(task_uuid, **task.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated

@router.delete("/{task_uuid}", response_model=TaskResponse)
def delete_task(
    task_uuid: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    rate_limit: dict = Depends(check_tasks_delete_rate_limit)
):
    """Delete a task with rate limiting."""
    service = TaskService(db)
    deleted = service.delete_task(task_uuid)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return deleted

@router.post("/{task_uuid}/assign", response_model=TaskResponse)
def assign_task(
    task_uuid: UUID,
    assignment_data: TaskAssignmentRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    rate_limit: dict = Depends(check_tasks_write_rate_limit)
):
    """Assign or unassign a task to/from a user with rate limiting."""
    service = TaskService(db)
    
    # Get the user_uuid from the request body
    user_uuid = assignment_data.user_uuid
    
    # Validate that the user exists if user_uuid is provided
    if user_uuid:
        from services.user_service import UserService
        user_service = UserService(db)
        user = user_service.get_user(user_uuid)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
    
    assigned = service.assign_task(task_uuid, user_uuid)
    if not assigned:
        raise HTTPException(status_code=404, detail="Task not found")
    return assigned

@router.post("/{task_uuid}/complete", response_model=TaskResponse)
def mark_task_completed(
    task_uuid: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    rate_limit: dict = Depends(check_tasks_write_rate_limit)
):
    """Mark a task as completed with rate limiting."""
    service = TaskService(db)
    completed = service.mark_task_completed(task_uuid)
    if not completed:
        raise HTTPException(status_code=404, detail="Task not found")
    return completed

# Rate limiting information endpoints
@router.get("/rate-limit/status")
async def get_task_rate_limit_status(
    request: Request,
    limit_type: str = "tasks_read"
):
    """Get current rate limit status for task operations."""
    from services.rate_limiter import rate_limiter
    info = await rate_limiter.get_rate_limit_info(request, limit_type)
    return info
