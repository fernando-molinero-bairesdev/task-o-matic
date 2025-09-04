from models.task import Task, Status
from models.user import User
from sqlalchemy.orm import Session
from datetime import datetime

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

    # Read tasks (with pagination)
    def get_tasks(self, skip=0, limit=10, status=None, due_date=None):
        query = self.db.query(Task).filter(Task.deleted_date == None)
        if status:
            query = query.filter(Task.status == status)
        if due_date:
            query = query.filter(Task.due_date == due_date)
        return query.offset(skip).limit(limit).all()

    # Update a task
    def update_task(self, task_uuid, **kwargs):
        task = self.db.query(Task).filter(Task.task_uuid == task_uuid, Task.deleted_date == None).first()
        if not task:
            return None
        for key, value in kwargs.items():
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
    def assign_task(self, task_uuid, user_uuid):
        task = self.db.query(Task).filter(Task.task_uuid == task_uuid, Task.deleted_date == None).first()
        if not task:
            return None
        task.assigned_to = user_uuid
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
        self.db.commit()
        self.db.refresh(task)
        return task
