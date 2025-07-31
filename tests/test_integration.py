import os

import dotenv
import pytest

dotenv.load_dotenv()


@pytest.mark.asyncio
async def test_full_flow(async_client):
    # 1. Signup
    res = await async_client.post("/signup", json={"username": "alice", "password": "alicepw"})
    assert res.status_code == 201

    # 2. Login
    res = await async_client.post("/token", data={"username": "alice", "password": "alicepw"})
    assert res.status_code == 200
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "X-API-Key": "123456"}

    # 3. Create multiple tasks
    for i in range(3):
        await async_client.post(
            "/tasks/", json={"title": f"Task {i}", "description": "X", "status": "pending"}, headers=headers
        )

    # 4. List tasks
    res = await async_client.get("/tasks/", headers=headers)
    tasks = res.json()
    assert len(tasks) == 3

    # 5. Update first one fully
    task_id = tasks[0]["id"]
    res = await async_client.put(
        f"/tasks/{task_id}", json={"title": "New", "description": "Updated", "status": "completed"}, headers=headers
    )
    assert res.status_code == 200
    assert res.json()["status"] == "completed"

    # 6. Delete one
    res = await async_client.delete(f"/tasks/{tasks[1]['id']}", headers=headers)
    assert res.status_code == 204

    # 7. Verify task count = 2
    res = await async_client.get("/tasks/", headers=headers)
    assert len(res.json()) == 2


@pytest.mark.asyncio
async def test_task_crud_lifecycle(async_client):
    API_KEY = os.getenv("TSKZ_HTTP_API_KEY", "sample_key")

    # Setup user
    await async_client.post("/signup", json={"username": "john", "password": "pass"})
    token_res = await async_client.post("/token", data={"username": "john", "password": "pass"})
    token = token_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "X-API-Key": API_KEY}

    # Create task
    task_data = {"title": "Task 1", "description": "Test it", "status": "pending"}
    res = await async_client.post("/tasks/", json=task_data, headers=headers)
    assert res.status_code == 201
    task = res.json()
    task_id = task["id"]

    # List tasks
    res = await async_client.get("/tasks/", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 1

    # Get by ID
    res = await async_client.get(f"/tasks/{task_id}", headers=headers)
    assert res.status_code == 200
    assert res.json()["title"] == "Task 1"

    # Patch status
    res = await async_client.patch(f"/tasks/{task_id}", json={"status": "completed"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["status"] == "completed"

    # PUT full update
    full_update = {"title": "Updated", "description": "New desc", "status": "pending"}
    res = await async_client.put(f"/tasks/{task_id}", json=full_update, headers=headers)
    assert res.status_code == 200
    assert res.json()["title"] == "Updated"

    # Delete
    res = await async_client.delete(f"/tasks/{task_id}", headers=headers)
    assert res.status_code == 204

    # Verify deletion
    res = await async_client.get(f"/tasks/{task_id}", headers=headers)
    assert res.status_code == 404
