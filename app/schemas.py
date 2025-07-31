from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------- #
# Task Schema
# ---------------------------- #
class TaskStatus(str, Enum):
    pending = "pending"
    completed = "completed"


class TaskBase(BaseModel):
    title: str
    description: str
    status: TaskStatus = TaskStatus.pending


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    pass


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class TaskOut(TaskBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------- #
# User Schema
# ---------------------------- #
class UserCreate(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str

    model_config = {"from_attributes": True}


# ---------------------------- #
# Token Schema
# ---------------------------- #
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


# ---------------------------- #
# API Key Schema
# ---------------------------- #
class APIKeyHeader(BaseModel):
    api_key: str = Field(..., alias="X-API-Key")
