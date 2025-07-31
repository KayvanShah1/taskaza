import os

import pytest
from dotenv import load_dotenv

load_dotenv()
VALID_API_KEY = os.getenv("TSKZ_HTTP_API_KEY")
INVALID_API_KEY = "invalid-key"
BAD_TOKEN = "Bearer badtoken.fake.jwt"

TASK_ENDPOINTS = [
    ("get", "/tasks/"),
    ("post", "/tasks/"),
    ("get", "/tasks/999"),
    ("patch", "/tasks/999"),
    ("put", "/tasks/999"),
    ("delete", "/tasks/999"),
]


def requires_body(method: str) -> bool:
    return method in {"post", "put", "patch"}


@pytest.mark.parametrize("method,endpoint", TASK_ENDPOINTS)
@pytest.mark.asyncio
async def test_missing_jwt_token(async_client, method, endpoint):
    headers = {"X-API-Key": VALID_API_KEY}
    kwargs = {"headers": headers}
    if requires_body(method):
        kwargs["json"] = {}
    response = await getattr(async_client, method)(endpoint, **kwargs)
    assert response.status_code == 401


@pytest.mark.parametrize("method,endpoint", TASK_ENDPOINTS)
@pytest.mark.asyncio
async def test_missing_api_key(async_client, auth_headers_only_token, method, endpoint):
    headers = auth_headers_only_token.copy()
    headers.pop("X-API-Key", None)
    kwargs = {"headers": headers}
    if requires_body(method):
        kwargs["json"] = {}
    response = await getattr(async_client, method)(endpoint, **kwargs)
    assert response.status_code == 401


@pytest.mark.parametrize("method,endpoint", TASK_ENDPOINTS)
@pytest.mark.asyncio
async def test_invalid_jwt_token(async_client, method, endpoint):
    headers = {"Authorization": BAD_TOKEN, "X-API-Key": VALID_API_KEY}
    kwargs = {"headers": headers}
    if requires_body(method):
        kwargs["json"] = {}
    response = await getattr(async_client, method)(endpoint, **kwargs)
    assert response.status_code == 401


@pytest.mark.parametrize("method,endpoint", TASK_ENDPOINTS)
@pytest.mark.asyncio
async def test_invalid_api_key(async_client, auth_headers_only_token, method, endpoint):
    headers = auth_headers_only_token.copy()
    headers["X-API-Key"] = INVALID_API_KEY
    kwargs = {"headers": headers}
    if requires_body(method):
        kwargs["json"] = {}
    response = await getattr(async_client, method)(endpoint, **kwargs)
    assert response.status_code == 403
