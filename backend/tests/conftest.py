import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..models.base import Base

TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/taskomatic_test"
engine = create_engine(TEST_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    # Create all tables in one call using shared Base
    # Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    # Base.metadata.drop_all(bind=engine)
