from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[EmailStr] = None
    display_name: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"username": "string", "password": "string", "email": "string@example.com", "display_name": "string"},
            ]
        }
    )


class UserOut(BaseModel):
    id: int
    username: str
    email: Optional[EmailStr] = None
    display_name: Optional[str] = None
    email_verified: bool = False

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    display_name: Optional[str] = None
