from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------- #
# Token Schema
# ---------------------------- #
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
                    "token_type": "bearer",
                }
            ]
        }
    )


class TokenData(BaseModel):
    id: Optional[int] = None
    username: Optional[str] = None


# ---------------------------- #
# API Key Schema
# ---------------------------- #
class APIKeyHeader(BaseModel):
    api_key: str = Field(..., alias="X-API-Key")
