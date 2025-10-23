from __future__ import annotations

import json

from app.core.dependencies import get_db, require_verified_user
from app.crud import apikey as crud
from app.models.user import User
from app.schemas.apikey import APIKeyCreate, APIKeyOut, APIKeySecretOut
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/apikeys", tags=["API Keys"])


@router.post("", response_model=APIKeySecretOut, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    payload: APIKeyCreate,
    user: User = Depends(require_verified_user),
    db: AsyncSession = Depends(get_db),
):
    scopes_json = json.dumps(payload.scopes) if payload.scopes else None
    key, display = await crud.create_api_key(
        db, user_id=user.id, name=payload.name, scopes_json=scopes_json, expires_at=payload.expires_at
    )
    return APIKeySecretOut(
        id=key.id,
        name=key.name,
        prefix=key.prefix,
        scopes=payload.scopes or None,
        expires_at=key.expires_at,
        revoked=key.revoked,
        created_at=key.created_at,
        api_key=display,  # show ONCE
    )


@router.get("", response_model=list[APIKeyOut])
async def list_api_keys(
    user: User = Depends(require_verified_user),
    db: AsyncSession = Depends(get_db),
):
    keys = await crud.list_api_keys(db, user.id)
    out = []

    for k in keys:
        scopes = json.loads(k.scopes) if k.scopes else None
        out.append(
            APIKeyOut(
                id=k.id,
                name=k.name,
                prefix=k.prefix,
                scopes=scopes,
                expires_at=k.expires_at,
                revoked=k.revoked,
                created_at=k.created_at,
            )
        )
    return out


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Revoke or delete an API key")
async def delete_or_revoke_api_key(
    key_id: int,
    hard: bool = False,
    user: User = Depends(require_verified_user),
    db: AsyncSession = Depends(get_db),
):
    if hard:
        ok = await crud.delete_api_key(db, user.id, key_id)
    else:
        ok = await crud.revoke_api_key(db, user.id, key_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Key not found or already revoked")
    return Response(status_code=status.HTTP_204_NO_CONTENT, content="API key deleted/revoked")
