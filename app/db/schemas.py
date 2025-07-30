from pydantic import BaseModel
from enum import Enum
from typing import Optional
from datetime import datetime


class TaskStatus(str, Enum):
    pending = "pending"
    completed = "completed"


class TaskBase(BaseModel):
    title: str
    description: str
    status: TaskStatus = TaskStatus.pending


class TaskCreate(TaskBase):
    pass


class TaskOut(TaskBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
