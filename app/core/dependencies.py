from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_access_token
from app.crud.user import get_user_by_username
from app.core.config import settings
from app.db import async_session
from app.models import User

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


# ---------------------------- #
# Dependency: DB Session
# ---------------------------- #
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


# ---------------------------- #
# Dependency: API Key Check
# ---------------------------- #
def verify_api_key(x_api_key: str = Depends(api_key_header)):
    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API Key header missing")
    if x_api_key != settings.HTTP_API_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API Key")
    return x_api_key


# ---------------------------- #
# Dependency: Get Current User
# ---------------------------- #
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    token_data = verify_access_token(token)
    user = await get_user_by_username(db, token_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user
