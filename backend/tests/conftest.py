import os
import sys

import pytest_asyncio
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

# Allow "app." imports when running tests directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from app.core.dependencies import get_db
from app.db.session import Base
from app.main import app

# ---------------------------------------------------------------------
# Test database: single shared in-memory SQLite connection
# ---------------------------------------------------------------------
# Use URI + shared cache for stable in-memory behavior with aiosqlite.
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:?cache=shared"

engine_test = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
    poolclass=StaticPool,  # single shared connection for the whole test session
    connect_args={"check_same_thread": False, "uri": True},
)
TestingSessionLocal = async_sessionmaker(bind=engine_test, class_=AsyncSession, expire_on_commit=False)


# ---------------------------------------------------------------------
# Enable SQLite foreign key cascades on EVERY pooled connection
# (with aiosqlite the dbapi_connection may not be an instance of sqlite3.Connection,
# so don't guard with isinstance—just execute the PRAGMA.)
# ---------------------------------------------------------------------
@event.listens_for(engine_test.sync_engine, "connect")
def _enable_sqlite_fks_for_tests(dbapi_connection, _):
    dbapi_connection.execute("PRAGMA foreign_keys=ON")


# ---------------------------------------------------------------------
# Auto-check once per test session that FKs are really ON
# ---------------------------------------------------------------------
@pytest_asyncio.fixture(scope="session", autouse=True)
async def verify_sqlite_fk_enabled():
    """Fail fast if PRAGMA foreign_keys is not active on test engine."""
    async with TestingSessionLocal() as s:
        val = (await s.execute(text("PRAGMA foreign_keys"))).scalar_one()
        assert val == 1, "SQLite foreign_keys PRAGMA is not enabled on test engine!"


# ---------------------------------------------------------------------
# Override the app DB dependency to use the test session
# ---------------------------------------------------------------------
async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


# ---------------------------------------------------------------------
# Async HTTP client against ASGI app + per-test DB setup/teardown
# ---------------------------------------------------------------------
@pytest_asyncio.fixture
async def async_client():
    # Ensure FKs are ON for the single shared connection and (re)create schema
    async with engine_test.begin() as conn:
        # Redundant but harmless: explicitly set PRAGMA on this connection too
        await conn.exec_driver_sql("PRAGMA foreign_keys=ON")
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    # Drop all tables after each test for isolation
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ---------------------------------------------------------------------
# Auth header helpers
# ---------------------------------------------------------------------
def _api_key() -> str:
    # match your verify_api_key default; fall back to 123456
    return os.getenv("TSKZ_HTTP_API_KEY") or os.getenv("X_API_KEY") or "123456"


@pytest_asyncio.fixture
async def auth_headers_only_token(async_client):
    # For negative tests where API key is intentionally omitted
    await async_client.post("/signup", json={"username": "badtester", "password": "badpass"})
    res = await async_client.post("/token", data={"username": "badtester", "password": "badpass"})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def auth_headers(async_client):
    # Full headers (JWT + API key) for protected routes
    await async_client.post("/signup", json={"username": "user", "password": "pw"})
    tok = await async_client.post("/token", data={"username": "user", "password": "pw"})
    token = tok.json()["access_token"]
    return {"Authorization": f"Bearer {token}", "X-API-Key": _api_key()}
