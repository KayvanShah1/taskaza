from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from app.core.security import generate_api_key
from app.models.apikey import APIKey
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def create_api_key(
    db: AsyncSession,
    user_id: int,
    name: str,
    scopes_json: Optional[str],
    expires_at: Optional[datetime],
):
    display_key, prefix, secret_hash = generate_api_key()
    key = APIKey(
        user_id=user_id,
        name=name,
        prefix=prefix,
        secret_hash=secret_hash,
        scopes=scopes_json,
        expires_at=expires_at,
        revoked=False,
    )
    db.add(key)
    await db.commit()
    await db.refresh(key)
    return key, display_key


async def list_api_keys(db: AsyncSession, user_id: int):
    q = select(APIKey).where(APIKey.user_id == user_id).order_by(APIKey.created_at.desc())
    res = await db.execute(q)
    return list(res.scalars())


async def revoke_api_key(db: AsyncSession, user_id: int, key_id: int) -> bool:
    q = select(APIKey).where(APIKey.id == key_id, APIKey.user_id == user_id)
    res = await db.execute(q)
    key = res.scalar_one_or_none()
    if not key or key.revoked:
        return False
    key.revoked = True
    key.revoked_at = datetime.now(timezone.utc)
    await db.commit()
    return True


async def get_key_by_hash(db: AsyncSession, secret_hash: str) -> Optional[APIKey]:
    q = select(APIKey).where(APIKey.secret_hash == secret_hash)
    res = await db.execute(q)
    return res.scalar_one_or_none()


async def delete_api_key(db, user_id: int, key_id: int) -> bool:
    res = await db.execute(select(APIKey).where(APIKey.id == key_id, APIKey.user_id == user_id))
    key = res.scalar_one_or_none()
    if not key:
        return False
    await db.delete(key)
    await db.commit()
    return True
