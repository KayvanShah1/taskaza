from fastapi import HTTPException, Header
from app.core.config import settings


def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=403, detail="Invalid API Key")
