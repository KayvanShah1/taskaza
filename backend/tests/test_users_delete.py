import pytest
from httpx import AsyncClient

from utils import _signup_and_login
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from conftest import TestingSessionLocal


async def _create_task(client: AsyncClient, headers, title: str):
    payload = {
        "title": title,
        "description": None,
        "status": "todo",
        "priority": "medium",
        "category": "personal",
        "tags": [],
    }
    res = await client.post("/tasks", headers=headers, json=payload)
    assert res.status_code in (200, 201), res.text
    return res.json()["id"]


async def _count_tasks_for_user(db: AsyncSession, uid: int) -> int:
    res = await db.execute(text("SELECT COUNT(*) FROM tasks WHERE user_id = :uid"), {"uid": uid})
    return res.scalar_one()


@pytest.mark.asyncio
async def test_delete_user_cascades_tasks(async_client: AsyncClient):
    """
    Flow:
      - Sign up + login
      - Create a few tasks
      - Verify tasks exist
      - DELETE /users/{id}
      - Verify:
          * 204 No Content
          * /users/me now 404
          * All tasks for that user are gone from DB (CASCADE)
    """
    client: AsyncClient = async_client

    # Arrange: create user + tasks
    headers = await _signup_and_login(client, "del_user", "pw123")
    res = await async_client.get("/users/me", headers=headers)
    assert res.status_code == 200
    user_id = res.json()["id"]

    for i in range(3):
        await _create_task(client, headers, f"T{i + 1}")

    async with TestingSessionLocal() as db:
        assert await _count_tasks_for_user(db, user_id) == 3

    # Sanity: list tasks should show 3
    res = await client.get("/tasks", headers=headers)
    assert res.status_code == 200, res.text
    tasks_before = res.json()
    assert len(tasks_before) == 3

    # Act: delete the user
    res = await client.delete(f"/users/{user_id}", headers=headers)
    assert res.status_code == 204, res.text

    # The token still exists but get_current_user should now 404 "User not found"
    res = await client.get("/users/me", headers=headers)
    assert res.status_code == 404

    # Also any attempt to hit /tasks should fail because the user no longer exists
    res = await client.get("/tasks", headers=headers)
    assert res.status_code in (401, 404)

    async with TestingSessionLocal() as db:
        assert await _count_tasks_for_user(db, user_id) == 0
