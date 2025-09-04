import tomli
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

with open(os.path.join(os.path.dirname(__file__), "config.toml"), "rb") as f:
    config = tomli.load(f)

DATABASE_URL = config["database"]["url"]

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
