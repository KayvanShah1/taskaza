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
@router.post(
    "/",
    response_model=TaskOut,
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

    **Auth**
    - Requires `Authorization: Bearer <JWT>` and `X-API-Key`.

    **Query Parameters**
    - `create_subtree` (bool): If `true`, recursively persists `subtasks` provided in the body.

    **Request Body**
    - `TaskCreate`: Title, optional description, optional parent, optional `subtasks`.

    **Responses**
    - `201`: Returns the created `TaskOut`.
    - `401/403`: Missing/invalid auth or API key.
    - `422`: Validation error.
    """
    payload = task_in.model_dump(exclude_none=True)
    if create_subtree and (payload.get("subtasks") or []):
        return await crud.create_task_with_subtree(db, user_id=user.id, task_data=payload)
    return await crud.create_task(db, user_id=user.id, task_data=payload)


# -----------------------------
# List (filters + pagination)
# -----------------------------
@router.get(
    "/",
    response_model=list[TaskOut],
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

    **Auth**
    - Requires `Authorization: Bearer <JWT>` and `X-API-Key`.

    **Query Parameters**
    - `status` (TaskStatus): Filter by status.
    - `q` (str): Full-text search.
    - `page`/`limit`: Pagination controls.
    - `sort` (`asc|desc`): Created time sort order.
    - `include_tree` (bool): Include subtasks on each item.
    - `roots_only` (bool): Only top-level tasks.

    **Responses**
    - `200`: List of `TaskOut`.
    """
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
@router.get(
    "/{task_id}",
    response_model=TaskOut,
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

    **Auth**
    - Requires `Authorization: Bearer <JWT>` and `X-API-Key`.

    **Path Parameters**
    - `task_id` (int): Identifier of the task.

    **Query Parameters**
    - `include_tree` (bool): Include subtasks in the response.

    **Responses**
    - `200`: `TaskOut`
    - `404`: Task not found (or not owned by user).
    """
    task = await crud.get_task_by_id(db, task_id, user.id, include_tree=include_tree)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


# -----------------------------
# Update (partial). exclude_unset avoids nulling omitted fields.
# -----------------------------
@router.put(
    "/{task_id}",
    response_model=TaskOut,
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

    **Auth**
    - Requires `Authorization: Bearer <JWT>` and `X-API-Key`.

    **Path Parameters**
    - `task_id` (int): Task identifier.

    **Request Body**
    - `TaskUpdate`: Any subset of updatable fields. Omitted fields are not modified.

    **Responses**
    - `200`: Updated `TaskOut`
    - `400`: Invalid re-parenting or business rule violation.
    - `404`: Task not found (or not owned by user).
    """
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
@router.patch(
    "/{task_id}",
    response_model=TaskOut,
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

    **Auth**
    - Requires `Authorization: Bearer <JWT>` and `X-API-Key`.

    **Path Parameters**
    - `task_id` (int): Task identifier.

    **Request Body**
    - `TaskStatusUpdate`: New status (e.g., `todo`, `in_progress`, `completed`, `cancelled`).

    **Responses**
    - `200`: Updated `TaskOut`
    - `404`: Task not found (or not owned by user).
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

    **Auth**
    - Requires `Authorization: Bearer <JWT>` and `X-API-Key`.

    **Path Parameters**
    - `task_id` (int): Task identifier.

    **Responses**
    - `204`: Deleted successfully (no content).
    - `404`: Task not found (or not owned by user).
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

    **Auth**
    - Requires `Authorization: Bearer <JWT>` and `X-API-Key`.

    **Request Body**
    - `TaskBulkRequest`:
      - `create`: List of `TaskCreate` objects (optional).
      - `update_status`: List of `{ id, status }` pairs (optional).

    **Responses**
    - `200`: `TaskBulkResponse` with `created` and `updated` arrays.
    - `401/403`: Missing/invalid auth or API key.
    - `422`: Validation error.
    """
    created = []
    if payload.create:
        created = await crud.create_tasks_bulk(db, user.id, [t.model_dump(exclude_none=True) for t in payload.create])

    updated = []
    if payload.update_status:
        updates = [(u.id, u.status) for u in payload.update_status]
        updated = await crud.update_tasks_status_bulk(db, user.id, updates)

    return TaskBulkResponse(created=created, updated=updated)
