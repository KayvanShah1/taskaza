from datetime import datetime
from enum import Enum

from pydantic import BaseModel


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
