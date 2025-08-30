from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.engine import make_url

from app.core.config import settings

url = make_url(settings.DATABASE_URL)
is_sqlite = url.drivername.startswith("sqlite")

engine = create_async_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False} if is_sqlite else {}, pool_pre_ping=True
)
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

Base = declarative_base(name="BaseModel")
