from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field


# ===== Enums =====
class TaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class TaskCategory(str, Enum):
    work = "work"
    personal = "personal"
    shopping = "shopping"
    health = "health"
    learning = "learning"
    finance = "finance"
    family = "family"
    travel = "travel"


# ===== Base shared by all task shapes =====
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.todo
    priority: TaskPriority = TaskPriority.medium
    category: TaskCategory = TaskCategory.personal
    tags: List[str] = Field(default_factory=list)
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    notes: Optional[str] = None
    completed_date: Optional[datetime] = None


# ===== Create / Update =====
class TaskCreate(TaskBase):
    # attach to an existing parent; omit for root tasks
    parent_id: Optional[int] = None
    subtasks: List[TaskCreate] = Field(
        default_factory=list,
        validation_alias="subtasks",
        serialization_alias="subtasks",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "due_date": "2025-12-25",
                    "estimated_hours": 8,
                    "priority": "high",
                    "subtasks": [
                        {
                            "status": "completed",
                            "title": "Outline",
                            "subtasks": [
                                {
                                    "status": "completed",
                                    "title": "Outline",
                                    "subtasks": [
                                        {
                                            "status": "completed",
                                            "title": "Outline",
                                            "subtasks": [
                                                {"status": "completed", "title": "Outline"},
                                                {"status": "todo", "title": "Draft content"},
                                                {"status": "todo", "title": "Design slides"},
                                            ],
                                        },
                                        {"status": "todo", "title": "Draft content"},
                                        {"status": "todo", "title": "Design slides"},
                                    ],
                                },
                                {"status": "todo", "title": "Draft content"},
                                {"status": "todo", "title": "Design slides"},
                            ],
                        },
                        {"status": "todo", "title": "Draft content"},
                        {"status": "todo", "title": "Design slides"},
                    ],
                    "tags": ["proposal", "marketing", "Q4", "work"],
                    "title": "Complete project proposal",
                },
                {
                    "title": "Complete project proposal",
                    "priority": "high",
                    "tags": ["proposal", "marketing", "Q4", "work"],
                    "due_date": "2025-12-25",
                    "estimated_hours": 8,
                    "subtasks": [
                        {"title": "Outline", "status": "completed"},
                        {"title": "Draft content", "status": "todo"},
                        {"title": "Design slides", "status": "todo"},
                    ],
                },
            ]
        }
    )


class TaskUpdate(BaseModel):
    # partial update; can also move in the tree
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    category: Optional[TaskCategory] = None
    tags: Optional[List[str]] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    notes: Optional[str] = None
    completed_date: Optional[datetime] = None
    parent_id: Optional[int] = None  # set to None to re-root

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "title": "Finalize project proposal",
                    "description": "Update proposal with new budget numbers",
                    "priority": "high",
                    "tags": ["proposal", "Q4"],
                },
                {
                    "status": "in_progress",
                    "estimated_hours": 5.0,
                    "notes": "Started work, waiting on data from client",
                },
                {
                    "status": "completed",
                    "completed_date": "2025-09-27T18:30:00Z",
                    "actual_hours": 3.75,
                },
                {
                    "parent_id": 42,
                    "category": "research",
                    "tags": ["nested", "dependency"],
                },
            ]
        }
    )


# ===== Status-only Update (PATCH) =====
class TaskStatusUpdate(BaseModel):
    status: TaskStatus

    model_config = ConfigDict(
        json_schema_extra={"example": {"status": "completed"}}, extra="forbid"  # reject extra keys
    )


# ===== Response (SHALLOW, no subtasks) =====
class TaskOutShallow(TaskBase):
    id: int
    user_id: int
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    @computed_field(return_type=float)
    @property
    def progress(self) -> float:
        return 1.0 if self.status == TaskStatus.completed else 0.0

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


# ===== Response (TREE, recursive subtasks) =====
class TaskOutTree(TaskOutShallow):
    # recursive children; exposed as "subtasks" in JSON
    subtasks: List["TaskOutTree"] = Field(
        default_factory=list,
        validation_alias="subtasks",
        serialization_alias="subtasks",
    )

    @computed_field(return_type=float)
    @property
    def progress(self) -> float:
        # Tree: progress from children if present; otherwise fall back to own status
        if self.subtasks:
            total = len(self.subtasks)
            done = sum(1 for c in self.subtasks if c.status == TaskStatus.completed)
            return round(done / total, 4)
        return 1.0 if self.status == TaskStatus.completed else 0.0

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


# ===== Bulk =====
class TaskStatusBulkUpdate(TaskStatusUpdate):
    id: int


class TaskBulkRequest(BaseModel):
    create: List[TaskCreate] = Field(default_factory=list)
    update_status: List[TaskStatusBulkUpdate] = Field(default_factory=list)

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "create": [
                        {
                            "title": "Draft project proposal",
                            "description": "Outline scope and milestones",
                            "priority": "high",
                            "category": "work",
                            "tags": ["proposal", "Q4"],
                            "due_date": "2025-10-15T17:00:00Z",
                            "estimated_hours": 5.5,
                        },
                        {
                            "title": "Grocery run",
                            "category": "personal",
                            "priority": "low",
                            "status": "todo",
                            "tags": ["errands"],
                        },
                    ],
                    "update_status": [{"id": 1, "status": "completed"}],
                },
            ]
        },
    )


class TaskBulkResponse(BaseModel):
    # Use shallow outputs to avoid touching relationships in bulk responses
    created: List[TaskOutShallow] = Field(default_factory=list)
    updated: List[TaskOutShallow] = Field(default_factory=list)

    model_config = ConfigDict(extra="ignore")
