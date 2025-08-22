import os

import pytest
import pytest_asyncio
from dotenv import load_dotenv

load_dotenv()


@pytest_asyncio.fixture
async def auth_headers(async_client):
    API_KEY = os.getenv("TSKZ_HTTP_API_KEY", "sample_key")
    username = "john"
    password = "pass"

    await async_client.post("/signup", json={"username": username, "password": password})
    token_res = await async_client.post("/token", data={"username": username, "password": password})
    token = token_res.json()["access_token"]

    return {"Authorization": f"Bearer {token}", "X-API-Key": API_KEY}


@pytest_asyncio.fixture
async def created_task(async_client, auth_headers):
    task_data = {"title": "Task 1", "description": "Test it", "status": "pending"}
    res = await async_client.post("/tasks/", json=task_data, headers=auth_headers)
    return res.json()  # contains the task with id, etc.


@pytest.mark.asyncio
async def test_create_task(async_client, auth_headers):
    task_data = {"title": "My Task", "description": "Do stuff", "status": "pending"}
    res = await async_client.post("/tasks/", json=task_data, headers=auth_headers)
    assert res.status_code == 201
    json = res.json()
    assert json["title"] == "My Task"
    assert json["status"] == "pending"


@pytest.mark.asyncio
async def test_list_tasks(async_client, auth_headers):
    # Create 2 tasks
    for i in range(2):
        await async_client.post(
            "/tasks/", json={"title": f"Task {i}", "description": "Sample", "status": "pending"}, headers=auth_headers
        )

    res = await async_client.get("/tasks/", headers=auth_headers)
    assert res.status_code == 200
    assert len(res.json()) >= 2


@pytest.mark.asyncio
async def test_get_task_by_id(async_client, auth_headers, created_task):
    task_id = created_task["id"]
    res = await async_client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["id"] == task_id


@pytest.mark.asyncio
async def test_patch_task_status(async_client, auth_headers, created_task):
    task_id = created_task["id"]
    res = await async_client.patch(f"/tasks/{task_id}", json={"status": "completed"}, headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["status"] == "completed"


@pytest.mark.asyncio
async def test_put_update_task(async_client, auth_headers, created_task):
    task_id = created_task["id"]
    update = {"title": "Updated", "description": "New", "status": "pending"}
    res = await async_client.put(f"/tasks/{task_id}", json=update, headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["title"] == "Updated"
    assert res.json()["description"] == "New"


@pytest.mark.asyncio
async def test_delete_task(async_client, auth_headers, created_task):
    task_id = created_task["id"]
    res = await async_client.delete(f"/tasks/{task_id}", headers=auth_headers)
    assert res.status_code == 204

    # Ensure task is gone
    res = await async_client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert res.status_code == 404
