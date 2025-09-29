import os

from httpx import AsyncClient

API_KEY = os.getenv("TSKZ_HTTP_API_KEY") or os.getenv("X_API_KEY") or "123456"


async def _signup_and_login(async_client: AsyncClient, username="alice", password="alicepw"):
    # signup
    res = await async_client.post("/signup", json={"username": username, "password": password})
    assert res.status_code == 201, res.text

    # login
    res = await async_client.post("/token", data={"username": username, "password": password})
    assert res.status_code == 200, res.text
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "X-API-Key": API_KEY}
    return headers
