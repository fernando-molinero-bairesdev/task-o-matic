from models.task import Task, Status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from uuid import UUID


class TaskService:
    def __init__(self, db: Session):
        self.db = db

    # Create a task
    def create_task(self, **kwargs):
        task = Task(**kwargs)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    # Read a specific task by ID
    def get_task(self, task_uuid):
        return self.db.query(Task).filter(Task.task_uuid == task_uuid, Task.deleted_date == None).first()

    # Read tasks (with pagination)
    def get_tasks(self, skip=0, limit=10, status=None, due_date=None):
        query = self.db.query(Task).filter(Task.deleted_date == None)
        
        if status:
            query = query.filter(Task.status == status)
        if due_date:
            query = query.filter(Task.due_date == due_date)
            
        return query.offset(skip).limit(limit).all()

    # Enhanced filtering method for tasks
    def get_tasks_filtered(self, skip=0, limit=10, **filters):
        """Enhanced filtering method for tasks."""
        query = self.db.query(Task).filter(Task.deleted_date == None)
        
        # Status filter
        if 'status' in filters and filters['status']:
            query = query.filter(Task.status == filters['status'])
        
        # Date range filters
        if 'due_date_from' in filters and filters['due_date_from']:
            due_date_from = datetime.fromisoformat(filters['due_date_from'])
            query = query.filter(Task.due_date >= due_date_from)
            
        if 'due_date_to' in filters and filters['due_date_to']:
            due_date_to = datetime.fromisoformat(filters['due_date_to'])
            query = query.filter(Task.due_date <= due_date_to)
        
        # Assigned to filter
        if 'assigned_to' in filters and filters['assigned_to']:
            query = query.filter(Task.assigned_to == filters['assigned_to'])
        
        # Priority filter
        if 'priority' in filters and filters['priority']:
            query = query.filter(Task.priority == filters['priority'])
        
        # Order by due date and created date
        query = query.order_by(Task.due_date.asc(), Task.created_date.desc())
        
        return query.offset(skip).limit(limit).all()

    # Update a task
    def update_task(self, task_uuid, **kwargs):
        task = self.db.query(Task).filter(Task.task_uuid == task_uuid, Task.deleted_date == None).first()
        if not task:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(task, key, value)
        self.db.commit()
        self.db.refresh(task)
        return task

    # Soft delete a task
    def delete_task(self, task_uuid):
        task = self.db.query(Task).filter(Task.task_uuid == task_uuid, Task.deleted_date == None).first()
        if not task:
            return None
        task.deleted_date = datetime.utcnow()
        self.db.commit()
        return task

    # Assign task to user
    def assign_task(self, task_uuid, user_id):
        task = self.db.query(Task).filter(Task.task_uuid == task_uuid, Task.deleted_date == None).first()
        if not task:
            return None
        
        # Set assigned_to to user_id (can be None for unassignment)
        task.assigned_to = user_id
        
        # Update the modified date
        task.modified_date = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(task)
        return task

    # Mark task as completed
    def mark_task_completed(self, task_uuid):
        task = self.db.query(Task).filter(Task.task_uuid == task_uuid, Task.deleted_date == None).first()
        if not task:
            return None
        task.status = Status.DONE
        task.completed_date = datetime.utcnow()
        task.modified_date = datetime.utcnow()
        self.db.commit()
        self.db.refresh(task)
        return task
