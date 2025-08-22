from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class TaskStatus(str, Enum):
    pending = "pending"
    completed = "completed"


class TaskBase(BaseModel):
    title: str
    description: str
    status: TaskStatus = TaskStatus.pending


class TaskCreate(TaskBase):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"title": "Grocery Run", "description": "Buy fruits and vegetables", "status": "pending"},
                {"title": "Finish Assignment", "description": "Complete the FastAPI project", "status": "completed"},
            ]
        }
    )


class TaskUpdate(TaskBase):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "title": "Grocery Run",
                    "description": "Buy fruits and vegetables, dairy products",
                    "status": "pending",
                },
                {
                    "title": "Finish Assignment",
                    "description": "Complete the FastAPI project. Deploy it on Render.",
                    "status": "completed",
                },
            ]
        }
    )


class TaskStatusUpdate(BaseModel):
    status: TaskStatus

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"status": "completed"},
                {"status": "pending"},
            ]
        }
    )


class TaskOut(TaskBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
