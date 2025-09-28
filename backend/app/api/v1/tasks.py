from __future__ import annotations

from typing import Literal, Optional

from app.core.dependencies import get_current_user, get_db, verify_api_key
from app.crud import task as crud
from app.models.user import User
from app.schemas.task import (
    TaskBulkRequest,
    TaskBulkResponse,
    TaskCreate,
    TaskOut,
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
@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    create_subtree: bool = Query(
        True,
        description="If true, create nested subtasks recursively when provided.",
    ),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    payload = task_in.model_dump(exclude_none=True)
    if create_subtree and (payload.get("subtasks") or []):
        return await crud.create_task_with_subtree(db, user_id=user.id, task_data=payload)
    return await crud.create_task(db, user_id=user.id, task_data=payload)


# -----------------------------
# List (filters + pagination)
# -----------------------------
@router.get("/", response_model=list[TaskOut], status_code=status.HTTP_200_OK)
async def list_tasks(
    status_: Optional[TaskStatus] = Query(default=None, alias="status"),
    q: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort: Literal["asc", "desc"] = Query("desc"),
    include_tree: bool = Query(False, description="Eager-load subtasks"),
    roots_only: bool = Query(False, description="Only return parent_id IS NULL"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await crud.get_tasks_for_user(
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


# -----------------------------
# Read
# -----------------------------
@router.get("/{task_id}", response_model=TaskOut, status_code=status.HTTP_200_OK)
async def get_task(
    task_id: int,
    include_tree: bool = Query(True, description="Eager-load subtasks"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await crud.get_task_by_id(db, task_id, user.id, include_tree=include_tree)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


# -----------------------------
# Update (partial). exclude_unset avoids nulling omitted fields.
# -----------------------------
@router.put("/{task_id}", response_model=TaskOut, status_code=status.HTTP_200_OK)
async def update_task(
    task_id: int,
    update: TaskUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await crud.get_task_by_id(db, task_id, user.id, include_tree=False)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    payload = update.model_dump(exclude_unset=True)
    try:
        return await crud.update_task(db, task, payload)
    except ValueError as e:
        # e.g. invalid re-parenting (cycle, parent from another user, etc.)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# -----------------------------
# Update status (PATCH)
# -----------------------------
@router.patch("/{task_id}", response_model=TaskOut, status_code=status.HTTP_200_OK)
async def update_task_status(
    task_id: int,
    update: TaskStatusUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await crud.get_task_by_id(db, task_id, user.id, include_tree=False)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return await crud.update_task_status(db, task, update.status)


# -----------------------------
# Delete
# -----------------------------
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await crud.get_task_by_id(db, task_id, user.id, include_tree=False)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    await crud.delete_task(db, task)


# -----------------------------
# Bulk (create + status updates)
# -----------------------------
@router.post("/bulk", response_model=TaskBulkResponse, status_code=status.HTTP_200_OK)
async def bulk_tasks(
    payload: TaskBulkRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    created = []
    if payload.create:
        created = await crud.create_tasks_bulk(db, user.id, [t.model_dump(exclude_none=True) for t in payload.create])

    updated = []
    if payload.update_status:
        updates = [(u.id, u.status) for u in payload.update_status]
        updated = await crud.update_tasks_status_bulk(db, user.id, updates)

    return TaskBulkResponse(created=created, updated=updated)
