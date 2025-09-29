from __future__ import annotations

from app.core.config import settings
from sqlalchemy import event
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

url = make_url(settings.DATABASE_URL)
IS_SQLITE = url.get_backend_name() == "sqlite"  # robust check

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)

# Enable SQLite FKs (and optionally WAL) on every new pooled connection
if IS_SQLITE:

    @event.listens_for(engine.sync_engine, "connect")
    def _enable_sqlite_pragmas(dbapi_connection, _):
        cursor = dbapi_connection.cursor()
        # Always enable FK cascades
        cursor.execute("PRAGMA foreign_keys=ON")
        # If file-based (not :memory:), WAL improves concurrency
        if url.database and url.database not in (":memory:", ""):
            cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()


async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

Base = declarative_base(name="BaseModel")
