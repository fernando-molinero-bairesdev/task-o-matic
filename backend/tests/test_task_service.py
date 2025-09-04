from ..services.task_service import TaskService
from ..models.task import Status, Priority



def test_create_task(db_session):
    service = TaskService(db_session)
    task = service.create_task(title="Test Task", status=Status.TO_DO, priority=Priority.HIGH)
    assert task.task_uuid is not None
    assert task.title == "Test Task"


def test_update_task(db_session):
    service = TaskService(db_session)
    task = service.create_task(title="Test Task", status=Status.TO_DO, priority=Priority.HIGH)
    updated = service.update_task(task.task_uuid, title="Updated Task")
    assert updated.title == "Updated Task"


def test_delete_task(db_session):
    service = TaskService(db_session)
    task = service.create_task(title="Test Task", status=Status.TO_DO, priority=Priority.HIGH)
    deleted = service.delete_task(task.task_uuid)
    assert deleted.deleted_date is not None
