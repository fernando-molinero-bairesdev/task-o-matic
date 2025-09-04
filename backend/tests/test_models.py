from ..models.user import User
from ..models.task import Task, Status, Priority

def test_user_model():
    user = User(username="testuser", name="Test User", email="test@example.com", password="pass")
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.deleted_date is None

def test_task_model():
    task = Task(title="Test Task", status=Status.TO_DO, priority=Priority.HIGH)
    assert task.title == "Test Task"
    assert task.status == Status.TO_DO
    assert task.priority == Priority.HIGH
    assert task.deleted_date is None
