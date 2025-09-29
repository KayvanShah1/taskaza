import pytest
from utils import _signup_and_login


@pytest.mark.asyncio
async def test_auth_required(async_client):
    # No JWT or API key
    r = await async_client.get("/tasks")
    assert r.status_code in (401, 403)

    # With JWT but missing/invalid API key
    await async_client.post("/signup", json={"username": "a1", "password": "pw"})
    tok = await async_client.post("/token", data={"username": "a1", "password": "pw"})
    token = tok.json()["access_token"]
    r = await async_client.get("/tasks", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code in (401, 403)


@pytest.mark.asyncio
async def test_create_list_get_update_patch_delete(async_client):
    headers = await _signup_and_login(async_client, "basic1", "pw")

    # Create
    payload = {"title": "TaskA", "description": "alpha", "status": "todo"}
    r = await async_client.post("/tasks", json=payload, headers=headers)
    assert r.status_code == 201, r.text
    created = r.json()
    tid = created["id"]
    assert created["title"] == "TaskA"
    assert created["status"] == "todo"
    assert created.get("parent_id") is None

    # List (no nested usage yet)
    r = await async_client.get("/tasks", headers=headers)
    assert r.status_code == 200
    items = r.json()
    assert any(t["id"] == tid for t in items)

    # Read
    r = await async_client.get(f"/tasks/{tid}", headers=headers)
    assert r.status_code == 200
    assert r.json()["title"] == "TaskA"

    # PATCH status only
    r = await async_client.patch(f"/tasks/{tid}", json={"status": "completed"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["status"] == "completed"

    # PUT partial model (TaskUpdate) — other fields left unchanged if omitted
    r = await async_client.put(f"/tasks/{tid}", json={"title": "TaskA-2"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["title"] == "TaskA-2"
    assert r.json()["status"] == "completed"

    # Delete
    r = await async_client.delete(f"/tasks/{tid}", headers=headers)
    assert r.status_code == 204

    # Not found post-delete
    r = await async_client.get(f"/tasks/{tid}", headers=headers)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_filters_pagination_and_sort(async_client):
    headers = await _signup_and_login(async_client, "pager", "pw")

    # Create 5 tasks with different titles/status
    statuses = ["todo", "in_progress", "completed", "todo", "cancelled"]
    for i, st in enumerate(statuses):
        r = await async_client.post("/tasks", json={"title": f"T{i}", "status": st}, headers=headers)
        assert r.status_code == 201

    # Filter by status
    r = await async_client.get("/tasks?status=todo", headers=headers)
    assert r.status_code == 200
    todos = r.json()
    assert len(todos) >= 2
    assert all(t["status"] == "todo" for t in todos)

    # Search by query (title/description)
    r = await async_client.get("/tasks?q=T1", headers=headers)
    assert r.status_code == 200
    q_items = r.json()
    assert any("T1" in t["title"] for t in q_items)

    # Pagination (limit=2, page=2)
    r = await async_client.get("/tasks?limit=2&page=2&sort=desc", headers=headers)
    assert r.status_code == 200
    page2 = r.json()
    assert len(page2) <= 2  # must not exceed page size


@pytest.mark.asyncio
async def test_bulk_create_and_status_update(async_client):
    headers = await _signup_and_login(async_client, "bulk", "pw")

    # Bulk create 3 tasks
    payload = {
        "create": [
            {"title": "B1", "status": "todo"},
            {"title": "B2", "status": "todo"},
            {"title": "B3", "status": "in_progress"},
        ]
    }
    r = await async_client.post("/tasks/bulk", json=payload, headers=headers)
    assert r.status_code == 200, r.text
    body = r.json()
    created = body["created"]
    assert len(created) == 3

    # Bulk status update for two of them
    ids = [created[0]["id"], created[1]["id"]]
    r = await async_client.post(
        "/tasks/bulk",
        json={"update_status": [{"id": ids[0], "status": "completed"}, {"id": ids[1], "status": "cancelled"}]},
        headers=headers,
    )
    assert r.status_code == 200
    updated = r.json()["updated"]
    assert sorted([u["id"] for u in updated]) == sorted(ids)

    # Verify updates
    for tid, expected in zip(ids, ["completed", "cancelled"]):
        r = await async_client.get(f"/tasks/{tid}", headers=headers)
        assert r.status_code == 200
        assert r.json()["status"] == expected


@pytest.mark.asyncio
async def test_isolation_across_users(async_client):
    # User 1 creates a task
    headers1 = await _signup_and_login(async_client, "u_iso_1", "pw")
    r = await async_client.post("/tasks", json={"title": "Private", "status": "todo"}, headers=headers1)
    assert r.status_code == 201
    tid = r.json()["id"]

    # User 2 cannot read it
    headers2 = await _signup_and_login(async_client, "u_iso_2", "pw")
    r = await async_client.get(f"/tasks/{tid}", headers=headers2)
    assert r.status_code == 404

    # Nor update it
    r = await async_client.patch(f"/tasks/{tid}", json={"status": "completed"}, headers=headers2)
    assert r.status_code == 404

    # Nor delete it
    r = await async_client.delete(f"/tasks/{tid}", headers=headers2)
    assert r.status_code == 404
