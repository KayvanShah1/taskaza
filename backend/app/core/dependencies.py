import hashlib
from datetime import datetime, timezone
from typing import AsyncGenerator

from app.core.auth import verify_access_token
from app.core.timeutils import as_aware_utc

# from app.core.config import settings
from app.crud.apikey import get_key_by_hash
from app.crud.user import get_user_by_id
from app.db.session import async_session
from app.models.user import User
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

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
# def verify_api_key(x_api_key: str = Depends(api_key_header)):
#     if not x_api_key:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API Key header missing")
#     if x_api_key != settings.HTTP_API_KEY:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API Key")
#     return x_api_key


async def verify_api_key(
    x_api_key: str = Depends(api_key_header),
    db: AsyncSession = Depends(get_db),
):
    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API key")

    # Expect format: "tsk_<prefix>_<secret>"
    try:
        scheme, prefix, secret = x_api_key.split("_", 2)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key format")

    if scheme != "tsk" or not prefix or not secret:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    raw = f"{prefix}.{secret}"
    secret_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    key = await get_key_by_hash(db, secret_hash)
    if not key or key.revoked:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key revoked or not found")

    # expiry check
    if key.expires_at and as_aware_utc(key.expires_at) < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key expired")

    # You can attach scopes or the user to request state if needed
    return key


# ---------------------------- #
# Dependency: Get Current User
# ---------------------------- #
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    token_data = verify_access_token(token)
    user = await get_user_by_id(db, token_data.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


# ---------------------------- #
# Dependency: Require Verified User
# ---------------------------- #
async def require_verified_user(user: User = Depends(get_current_user)) -> User:
    if not user.email_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email not verified")
    return user
