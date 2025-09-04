import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from main import app
from db import get_db
from models.base import Base
from models.user import User
from models.task import Task
from authorization.auth_service import AuthService
from services.user_service import UserService
from datetime import datetime, timedelta
import uuid

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def db_engine():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client():
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    from authorization.auth_service import AuthService
    
    user_service = UserService(db_session)
    auth_service = AuthService(user_service)
    
    user_data = {
        "username": "testuser",
        "name": "Test User", 
        "email": "test@example.com",
        "password": auth_service.get_password_hash("testpassword123")
    }
    
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    return user

@pytest.fixture
def test_user2(db_session):
    """Create a second test user for assignment tests."""
    from authorization.auth_service import AuthService
    
    user_service = UserService(db_session)
    auth_service = AuthService(user_service)
    
    user_data = {
        "username": "testuser2",
        "name": "Test User 2",
        "email": "test2@example.com", 
        "password": auth_service.get_password_hash("testpassword123")
    }
    
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    return user

@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for test user."""
    login_data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def test_task(db_session, test_user):
    """Create a test task."""
    from constants import Status
    
    task_data = {
        "title": "Test Task",
        "description": "Test task description",
        "status": Status.TO_DO,
        "priority": 2,
        "due_date": datetime.utcnow() + timedelta(days=7),
        "assigned_to": None,
        "tags": ["test", "sample"]
    }
    
    task = Task(**task_data)
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    
    return task