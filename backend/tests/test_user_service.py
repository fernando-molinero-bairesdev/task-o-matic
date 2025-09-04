from ..services.user_service import UserService
from ..models.user import User

def test_create_user(db_session):
    service = UserService(db_session)
    user = service.create_user(username="testuser", name="Test User", email="test@example.com", password="pass")
    assert user.user_uuid is not None
    assert user.username == "testuser"


def test_update_user(db_session):
    service = UserService(db_session)
    user = service.create_user(username="testuser", name="Test User", email="test@example.com", password="pass")
    updated = service.update_user(user.user_uuid, name="Updated Name")
    assert updated.name == "Updated Name"


def test_delete_user(db_session):
    service = UserService(db_session)
    user = service.create_user(username="testuser", name="Test User", email="test@example.com", password="pass")
    deleted = service.delete_user(user.user_uuid)
    assert deleted.deleted_date is not None
