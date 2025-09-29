from __future__ import annotations

from typing import Literal, Optional

from app.core.dependencies import get_current_user, get_db, verify_api_key
from app.crud import task as crud
from app.models.user import User
from app.schemas.task import (
    TaskBulkRequest,
    TaskBulkResponse,
    TaskCreate,
    TaskOutShallow,
    TaskOutTree,
    TaskStatus,
    TaskStatusUpdate,
    TaskUpdate,
)
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
    dependencies=[Depends(verify_api_key)],
)


# -----------------------------
# Create (supports nested subtasks via ?create_subtree)
# -----------------------------
@router.post(
    "",
    response_model=TaskOutShallow,
    response_model_exclude={"subtasks"},  # avoid touching relationship on plain create
    status_code=status.HTTP_201_CREATED,
    summary="Create a task",
    description=(
        "Create a new task for the authenticated user. Optionally create nested subtasks when provided on the payload."
    ),
)
async def create_task(
    task_in: TaskCreate,
    create_subtree: bool = Query(
        True,
        description="If true, create nested subtasks recursively when provided.",
    ),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create Task
    """
    payload = task_in.model_dump(exclude_none=True)
    if create_subtree and (payload.get("subtasks") or []):
        # This returns an eager-loaded tree; but we still exclude subtasks via response_model_exclude.
        # If you want to return the full tree on create-with-subtree, remove response_model_exclude above.
        return await crud.create_task_with_subtree(db, user_id=user.id, task_data=payload)
    return await crud.create_task(db, user_id=user.id, task_data=payload)


# -----------------------------
# List (filters + pagination)
# -----------------------------
@router.get(
    "",
    # response_model=list[TaskOutTree],
    status_code=status.HTTP_200_OK,
    summary="List tasks",
    description=(
        "Fetch the current user's tasks with optional status filtering, search, sorting, "
        "pagination, and eager-loading of subtasks."
    ),
)
async def list_tasks(
    status_: Optional[TaskStatus] = Query(default=None, alias="status", description="Filter by task status"),
    q: Optional[str] = Query(default=None, description="Free-text search over title/description"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(20, ge=1, le=100, description="Page size"),
    sort: Literal["asc", "desc"] = Query("desc", description="Sort by created time"),
    include_tree: bool = Query(False, description="If true, eagerly load subtasks"),
    roots_only: bool = Query(False, description="If true, only return root tasks (parent_id is NULL)"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List Tasks
    """
    items = await crud.get_tasks_for_user(
        db,
        user.id,
        status=status_,
        q=q,
        page=page,
        limit=limit,
        sort=sort,
        include_tree=include_tree,
        roots_only=roots_only,
    )

    if include_tree:
        return [TaskOutTree.model_validate(t, from_attributes=True) for t in items]
    return [TaskOutShallow.model_validate(t, from_attributes=True) for t in items]


# -----------------------------
# Read
# -----------------------------
@router.get(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    summary="Get a task by ID",
    description="Retrieve a single task that belongs to the authenticated user.",
)
async def get_task(
    task_id: int,
    include_tree: bool = Query(True, description="If true, eagerly load subtasks"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get Task
    """
    task = await crud.get_task_by_id(db, task_id, user.id, include_tree=include_tree)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if include_tree:
        return TaskOutTree.model_validate(task, from_attributes=True).model_dump()
    return TaskOutShallow.model_validate(task, from_attributes=True).model_dump()


# -----------------------------
# Update (partial). exclude_unset avoids nulling omitted fields.
# -----------------------------
@router.put(
    "/{task_id}",
    response_model=TaskOutShallow,
    response_model_exclude={"subtasks"},  # prevent accidental lazy access
    status_code=status.HTTP_200_OK,
    summary="Update a task (partial)",
    description="Partially update fields on a task. Fields omitted are left unchanged.",
)
async def update_task(
    task_id: int,
    update: TaskUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update Task (Partial)
    """
    task = await crud.get_task_by_id(db, task_id, user.id, include_tree=False)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    payload = update.model_dump(exclude_unset=True)
    try:
        return await crud.update_task(db, task, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# -----------------------------
# Update status (PATCH)
# -----------------------------
@router.patch(
    "/{task_id}",
    response_model=TaskOutShallow,
    response_model_exclude={"subtasks"},  # status-only; don't touch children
    status_code=status.HTTP_200_OK,
    summary="Update only the status of a task",
    description="Convenience endpoint to change the status without touching other fields.",
)
async def update_task_status(
    task_id: int,
    update: TaskStatusUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update Task Status
    """
    task = await crud.get_task_by_id(db, task_id, user.id, include_tree=False)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return await crud.update_task_status(db, task, update.status)


# -----------------------------
# Delete
# -----------------------------
@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description="Delete a task owned by the authenticated user.",
)
async def delete_task(
    task_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete Task
    """
    task = await crud.get_task_by_id(db, task_id, user.id, include_tree=False)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    await crud.delete_task(db, task)


# -----------------------------
# Bulk (create + status updates)
# -----------------------------
@router.post(
    "/bulk",
    response_model=TaskBulkResponse,
    status_code=status.HTTP_200_OK,
    summary="Bulk operations",
    description="Create multiple tasks in one call and/or update statuses of existing tasks.",
)
async def bulk_tasks(
    payload: TaskBulkRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Bulk Tasks
    """
    created = []
    if payload.create:
        created = await crud.create_tasks_bulk(db, user.id, [t.model_dump(exclude_none=True) for t in payload.create])

    updated = []
    if payload.update_status:
        updates = [(u.id, u.status) for u in payload.update_status]
        updated = await crud.update_tasks_status_bulk(db, user.id, updates)

    return TaskBulkResponse(created=created, updated=updated)
