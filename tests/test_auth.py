import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_signup_and_login(async_client: AsyncClient):
    # Signup
    res = await async_client.post("/signup", json={"username": "testuser", "password": "secret"})
    assert res.status_code == 201
    assert res.json()["username"] == "testuser"

    # Login
    res = await async_client.post("/token", data={"username": "testuser", "password": "secret"})
    assert res.status_code == 200
    token = res.json()["access_token"]
    assert token
