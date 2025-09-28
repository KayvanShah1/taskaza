# app/models/task.py
from __future__ import annotations

import enum
from datetime import datetime
from typing import List, Optional

from app.db.session import Base
from sqlalchemy import JSON, DateTime, Enum, Float, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.ext.mutable import MutableList  # <-- important for JSON list mutability
from sqlalchemy.orm import Mapped, mapped_column, relationship


# --- DB Enums (values match your Pydantic enums) ---
class DBTaskStatus(str, enum.Enum):
    todo = "todo"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class DBTaskPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class DBTaskCategory(str, enum.Enum):
    work = "work"
    personal = "personal"
    shopping = "shopping"
    health = "health"
    learning = "learning"
    finance = "finance"
    family = "family"
    travel = "travel"


class Task(Base):
    __tablename__ = "tasks"

    # --- Identity / ownership ---
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)

    # self-referential parent (for subtasks)
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), index=True, nullable=True
    )

    # --- Core fields ---
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    status: Mapped[DBTaskStatus] = mapped_column(
        Enum(
            DBTaskStatus,
            name="task_status",
            native_enum=False,  # <-- SQLite: use CHECK constraint
            create_constraint=True,
            validate_strings=True,
        ),
        nullable=False,
        default=DBTaskStatus.todo,
    )
    priority: Mapped[DBTaskPriority] = mapped_column(
        Enum(DBTaskPriority, name="task_priority", native_enum=False, create_constraint=True, validate_strings=True),
        nullable=False,
        default=DBTaskPriority.medium,
    )
    category: Mapped[DBTaskCategory] = mapped_column(
        Enum(DBTaskCategory, name="task_category", native_enum=False, create_constraint=True, validate_strings=True),
        nullable=False,
        default=DBTaskCategory.personal,
    )

    # JSON works on SQLite as TEXT; MutableList makes in-place edits trackable
    tags: Mapped[List[str]] = mapped_column(MutableList.as_mutable(JSON), default=list)

    # Keep as datetime to match your Pydantic model; store UTC consistently
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    estimated_hours: Mapped[Optional[float]] = mapped_column(Float)
    actual_hours: Mapped[Optional[float]] = mapped_column(Float)

    # --- Timestamps ---
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        server_onupdate=func.now(),
    )

    # --- Relationships ---
    user = relationship("User", back_populates="tasks")

    subtasks = relationship(
        "Task",
        cascade="all, delete-orphan",
        back_populates="parent",
        passive_deletes=True,  # rely on DB cascade (ensure PRAGMA on)
        foreign_keys="Task.parent_id",
    )
    parent = relationship(
        "Task",
        back_populates="subtasks",
        remote_side="Task.id",
        foreign_keys=[parent_id],
    )

    __table_args__ = (Index("ix_tasks_user_status_due", "user_id", "status", "due_date"),)

    @property
    def progress(self) -> float:
        if self.subtasks:
            total = len(self.subtasks)
            done = sum(1 for t in self.subtasks if t.status == DBTaskStatus.completed)
            return round(done / total, 4)
        return 1.0 if self.status == DBTaskStatus.completed else 0.0

    __mapper_args__ = {"eager_defaults": True}
