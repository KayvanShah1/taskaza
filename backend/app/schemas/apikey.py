from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class APIKeyCreate(BaseModel):
    name: str = Field(..., max_length=100)
    scopes: Optional[List[str]] = None
    expires_at: Optional[datetime] = None  # UTC naive in your project


class APIKeyOut(BaseModel):
    id: int
    name: str
    prefix: str
    scopes: Optional[list[str]]
    expires_at: Optional[datetime]
    revoked: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class APIKeySecretOut(APIKeyOut):
    # Returned once on create
    api_key: str
