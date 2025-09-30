from datetime import datetime
from typing import Optional

from app.core.security import hash_password
from app.models.user import User
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalars().first()


async def get_user_by_id(db: AsyncSession, id: int) -> Optional[User]:
    result = await db.execute(select(User).filter(User.id == id))
    return result.scalars().first()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()


async def create_user(
    db: AsyncSession,
    username: str,
    password: str,
    *,
    email: str | None = None,
    display_name: str | None = None,
):
    hashed_pw = hash_password(password)
    new_user = User(
        username=username,
        hashed_password=hashed_pw,
        email=email,
        display_name=display_name,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_user(db: AsyncSession, user: User, updates: dict) -> User:
    for field, value in updates.items():
        setattr(user, field, value)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def set_verification_token(db: AsyncSession, user: User, token: str, expires: datetime) -> User:
    user.verification_token = token
    user.verification_token_expires = expires
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def verify_user_email(db: AsyncSession, token: str) -> Optional[User]:
    result = await db.execute(select(User).filter(User.verification_token == token))
    user = result.scalars().first()
    if not user:
        return None
    if not user.verification_token_expires or user.verification_token_expires < datetime.utcnow():
        return None
    user.email_verified = True
    user.verification_token = None
    user.verification_token_expires = None
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    stmt = delete(User).where(User.id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0
