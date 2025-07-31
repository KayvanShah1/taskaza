import os

import pytest
from dotenv import load_dotenv

load_dotenv()


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
