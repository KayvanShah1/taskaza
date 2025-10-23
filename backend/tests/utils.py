from httpx import AsyncClient

from conftest import TestingSessionLocal
from app.crud import user as crud_user
from app.crud import apikey as crud_apikey


async def _signup_and_login(async_client: AsyncClient, username="alice", password="alicepw"):
    # signup
    res = await async_client.post("/signup", json={"username": username, "password": password})
    assert res.status_code == 201, res.text

    # login
    res = await async_client.post("/token", data={"username": username, "password": password})
    assert res.status_code == 200, res.text
    token = res.json()["access_token"]

    # create API key for this user directly in DB
    async with TestingSessionLocal() as db:
        user = await crud_user.get_user_by_username(db, username)
        _, display_key = await crud_apikey.create_api_key(
            db, user_id=user.id, name="test", scopes_json=None, expires_at=None
        )

    headers = {"Authorization": f"Bearer {token}", "X-API-Key": display_key}
    return headers
