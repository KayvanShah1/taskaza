from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------- #
# Token Schema
# ---------------------------- #
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


# ---------------------------- #
# API Key Schema
# ---------------------------- #
class APIKeyHeader(BaseModel):
    api_key: str = Field(..., alias="X-API-Key")
