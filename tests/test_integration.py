import pytest


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
