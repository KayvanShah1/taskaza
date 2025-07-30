import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String

from app.db.database import Base


class TaskStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    description = Column(String)
    status = Column(Enum(TaskStatus), default=TaskStatus.pending)
    created_at = Column(DateTime, default=datetime.utcnow)
