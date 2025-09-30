from pydantic import BaseModel, EmailStr


class RequestVerifyEmail(BaseModel):
    email: EmailStr


class RequestPasswordReset(BaseModel):
    email: EmailStr


class CompletePasswordReset(BaseModel):
    token: str
    new_password: str
