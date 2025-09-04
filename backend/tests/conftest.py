import pytest
from ..db import get_db


@pytest.fixture()
def db_session():
    db = get_db()
    yield db
    db.close()
