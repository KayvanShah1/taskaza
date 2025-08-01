from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    username: str
    password: str

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "username": "john_doe",
                    "password": "securepassword123",
                },
            ]
        }
    )


class UserOut(BaseModel):
    id: int
    username: str

    model_config = {"from_attributes": True}
