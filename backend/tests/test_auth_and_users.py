import pytest
from httpx import AsyncClient
from utils import _signup_and_login


@pytest.mark.asyncio
async def test_login_and_me(async_client: AsyncClient):
    headers = await _signup_and_login(async_client, "kay", "pw")
    res = await async_client.get("/users/me", headers=headers)
    assert res.status_code == 200
    me = res.json()
    assert me["username"] == "kay"
    # email/display_name are optional
    assert "email" in me and "display_name" in me


@pytest.mark.asyncio
async def test_signup_conflicts(async_client: AsyncClient):
    # unique username
    res = await async_client.post("/signup", json={"username": "dup", "password": "pw"})
    assert res.status_code == 201

    res = await async_client.post("/signup", json={"username": "dup", "password": "pw"})
    assert res.status_code == 400
    assert res.json()["detail"] == "Username already taken"

    # unique email
    res = await async_client.post("/signup", json={"username": "e1", "password": "pw", "email": "a@b.com"})
    assert res.status_code == 201

    res = await async_client.post("/signup", json={"username": "e2", "password": "pw", "email": "a@b.com"})
    assert res.status_code == 400
    assert res.json()["detail"] == "Email already taken"


@pytest.mark.asyncio
async def test_update_me_put_and_patch(async_client: AsyncClient):
    headers = await _signup_and_login(async_client, "john", "pw")

    payload_put = {"username": "john_new", "email": "john@example.com", "display_name": "John N"}
    res = await async_client.put("/users/me", json=payload_put, headers=headers)
    assert res.status_code == 200
    assert res.json()["username"] == "john_new"

    # 🔁 refresh JWT because username changed
    tok = await async_client.post("/token", data={"username": "john_new", "password": "pw"})
    token2 = tok.json()["access_token"]
    headers["Authorization"] = f"Bearer {token2}"

    # create conflicting username
    await async_client.post("/signup", json={"username": "taken", "password": "pw"})

    # now conflict should be 400
    res = await async_client.patch("/users/me", json={"username": "taken"}, headers=headers)
    assert res.status_code == 400
    assert res.json()["detail"] == "Username already taken"

    # valid patch
    res = await async_client.patch("/users/me", json={"email": "john2@example.com"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["email"] == "john2@example.com"


@pytest.mark.asyncio
async def test_login_wrong_password(async_client):
    await async_client.post("/signup", json={"username": "x", "password": "right"})
    res = await async_client.post("/token", data={"username": "x", "password": "wrong"})
    assert res.status_code == 401
