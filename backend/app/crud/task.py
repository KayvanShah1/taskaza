from __future__ import annotations

from collections import deque
from typing import Any, Iterable, Mapping, Sequence

from app.models.task import DBTaskCategory, DBTaskPriority, DBTaskStatus, Task
from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload, selectinload

# ---------- helpers ----------

_ENUM_FIELDS = {
    "status": DBTaskStatus,
    "priority": DBTaskPriority,
    "category": DBTaskCategory,
}


def _normalize_payload(data: Mapping[str, Any]) -> dict:
    """
    Convert Pydantic enums -> their .value (or accept raw strings).
    Ignore keys that are None (for partial updates).
    """
    out: dict[str, Any] = {}
    for k, v in data.items():
        if v is None:
            continue
        if k in _ENUM_FIELDS:
            if isinstance(v, str):
                out[k] = _ENUM_FIELDS[k](v)
            else:
                out[k] = _ENUM_FIELDS[k](getattr(v, "value", v))
        else:
            out[k] = v
    return out


async def _refresh_with_tree(db: AsyncSession, task: Task) -> Task:
    # Explicitly refresh fields we might need; keeps control over IO
    await db.refresh(task, attribute_names=["subtasks", "updated_at"])
    return task


async def _is_descendant(db: AsyncSession, node_id: int, maybe_ancestor_id: int) -> bool:
    stmt = select(Task).where(Task.id == maybe_ancestor_id).options(selectinload(Task.subtasks))
    res = await db.execute(stmt)
    root = res.scalar_one_or_none()
    if not root:
        return False

    stack = list(root.subtasks)
    while stack:
        n = stack.pop()
        if n.id == node_id:
            return True
        await db.refresh(n, attribute_names=["subtasks"])
        stack.extend(n.subtasks)
    return False


async def _eager_load_full_tree(db: AsyncSession, root: Task) -> Task:
    """
    Breadth-first: ensure `subtasks` is loaded for all descendants.
    Prevents async lazy loads during Pydantic serialization.
    """
    q = deque([root])
    while q:
        node = q.popleft()
        # ensure children loaded
        await db.refresh(node, attribute_names=["subtasks"])
        # extend downwards
        for child in node.subtasks:
            q.append(child)
    return root


# ---------- create ----------


async def create_task(db: AsyncSession, user_id: int, task_data: Mapping[str, Any]) -> Task:
    """
    Create a single task (optionally with parent_id). Does not create nested subtasks.
    Returns the row re-selected with `noload(Task.subtasks)` to avoid lazy IO on serialize.
    """
    payload = _normalize_payload(task_data)
    task = Task(**payload, user_id=user_id)
    db.add(task)
    await db.commit()

    # Re-select with noload to prevent Pydantic from triggering a lazy load
    stmt = select(Task).where(Task.id == task.id, Task.user_id == user_id).options(noload(Task.subtasks))
    res = await db.execute(stmt)
    return res.scalar_one()


async def create_task_with_subtree(
    db: AsyncSession,
    user_id: int,
    task_data: Mapping[str, Any],
) -> Task:
    """
    Create a task and all of its nested subtasks (recursive).
    Expects `subtasks` in `task_data` as list[dict].
    """

    def build_node(data: Mapping[str, Any], parent: Task | None) -> Task:
        payload = _normalize_payload({k: v for k, v in data.items() if k != "subtasks"})
        node = Task(**payload, user_id=user_id, parent=parent)
        for child in data.get("subtasks") or []:
            build_node(child, node)
        return node

    root = build_node(task_data, None)
    db.add(root)
    await db.commit()

    # Load the tree for safe serialization (2 levels; extend if you need deeper)
    stmt = (
        select(Task)
        .where(Task.id == root.id, Task.user_id == user_id)
        .options(selectinload(Task.subtasks).selectinload(Task.subtasks))
    )
    result = await db.execute(stmt)
    return result.scalar_one()


async def create_tasks_bulk(db: AsyncSession, user_id: int, tasks_data: Iterable[Mapping[str, Any]]) -> list[Task]:
    tasks = [Task(**_normalize_payload(data), user_id=user_id) for data in tasks_data]
    db.add_all(tasks)
    await db.commit()

    ids = [t.id for t in tasks]
    if not ids:
        return []

    stmt = (
        select(Task)
        .where(Task.user_id == user_id, Task.id.in_(ids))
        .options(noload(Task.subtasks))  # no implicit loads during serialization
    )
    res = await db.execute(stmt)
    return res.scalars().all()


# ---------- read ----------


async def get_tasks_for_user(
    db: AsyncSession,
    user_id: int,
    *,
    status: DBTaskStatus | str | None = None,
    q: str | None = None,
    page: int = 1,
    limit: int = 20,
    sort: str = "desc",
    include_tree: bool = False,
    roots_only: bool = False,
) -> list[Task]:
    """
    List tasks for a user, optionally filtering and including subtasks.
    - include_tree: eager-load subtasks to avoid N+1 queries
    - roots_only: only return tasks with parent_id IS NULL
    """
    stmt = select(Task).where(Task.user_id == user_id)

    if isinstance(status, str):
        status = DBTaskStatus(status)
    if status:
        stmt = stmt.where(Task.status == status)

    if q:
        stmt = stmt.where(Task.title.ilike(f"%{q}%"))

    if roots_only:
        stmt = stmt.where(Task.parent_id.is_(None))

    order = desc(Task.created_at) if str(sort).lower() == "desc" else asc(Task.created_at)
    stmt = stmt.order_by(order).offset(max(page - 1, 0) * max(limit, 1)).limit(max(limit, 1))

    if include_tree:
        stmt = stmt.options(selectinload(Task.subtasks).selectinload(Task.subtasks))  # 2 levels
    else:
        stmt = stmt.options(noload(Task.subtasks))

    result = await db.execute(stmt)
    rows = result.scalars().all()

    if include_tree:
        # fully load each tree root so Pydantic never triggers lazy IO
        for r in rows:
            await _eager_load_full_tree(db, r)
    return rows


async def get_task_by_id(
    db: AsyncSession,
    task_id: int,
    user_id: int,
    *,
    include_tree: bool = True,
) -> Task | None:
    stmt = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    if include_tree:
        stmt = stmt.options(selectinload(Task.subtasks).selectinload(Task.subtasks))
    else:
        stmt = stmt.options(noload(Task.subtasks))
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()

    if include_tree and task:
        task = await _eager_load_full_tree(db, task)
    return task


# ---------- update ----------


async def update_task(db: AsyncSession, task: Task, updated_data: Mapping[str, Any]) -> Task:
    payload = _normalize_payload(updated_data)

    if "parent_id" in updated_data:
        new_parent_id = updated_data.get("parent_id")

        if new_parent_id == task.id:
            raise ValueError("A task cannot be its own parent.")

        if new_parent_id is not None:
            parent = await db.get(Task, new_parent_id)
            if not parent or parent.user_id != task.user_id:
                raise ValueError("Parent task not found or not owned by the user.")

            if await _is_descendant(db, task.id, new_parent_id):
                raise ValueError("Cannot set a descendant as the parent (cycle).")

        setattr(task, "parent_id", new_parent_id)

    for key, value in payload.items():
        if key == "parent_id":
            continue
        setattr(task, key, value)

    await db.commit()
    stmt = select(Task).where(Task.id == task.id, Task.user_id == task.user_id).options(noload(Task.subtasks))
    return (await db.execute(stmt)).scalar_one()


async def update_task_status(db: AsyncSession, task: Task, new_status: DBTaskStatus | str) -> Task:
    if isinstance(new_status, str):
        new_status = DBTaskStatus(new_status)
    task.status = new_status
    await db.commit()
    stmt = select(Task).where(Task.id == task.id, Task.user_id == task.user_id).options(noload(Task.subtasks))
    return (await db.execute(stmt)).scalar_one()


async def update_tasks_status_bulk(
    db: AsyncSession,
    user_id: int,
    updates: Iterable[tuple[int, DBTaskStatus | str]],
) -> list[Task]:
    ids: list[int] = []
    desired: dict[int, DBTaskStatus] = {}
    for task_id, status in updates:
        ids.append(task_id)
        desired[task_id] = DBTaskStatus(status) if isinstance(status, str) else status

    if not ids:
        return []

    # Fetch rows to update (children not needed)
    stmt = select(Task).where(Task.user_id == user_id, Task.id.in_(ids))
    res = await db.execute(stmt)
    rows: Sequence[Task] = res.scalars().all()

    for t in rows:
        t.status = desired[t.id]

    await db.commit()

    # Re-fetch for safe serialization with subtasks disabled
    stmt2 = select(Task).where(Task.user_id == user_id, Task.id.in_(ids)).options(noload(Task.subtasks))
    res2 = await db.execute(stmt2)
    return res2.scalars().all()


# ---------- delete ----------


async def delete_task(db: AsyncSession, task: Task) -> None:
    """Delete a task (DB is configured with cascade delete for children)."""
    await db.delete(task)
    await db.commit()
