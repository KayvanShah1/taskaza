from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

engine = create_engine(settings.SQLITE_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base(name="BaseModel")


def get_db():
    db = SessionLocal()
    try:
        db.autoflush = True
        db.expire_on_commit = True
        yield db
    finally:
        db.close()
