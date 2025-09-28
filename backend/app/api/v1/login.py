from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import authenticate_user, create_access_token
from app.core.dependencies import get_db
from app.schemas.token import Token
from app.schemas.user import UserOut

router = APIRouter(tags=["Login"])


@router.post("/token", response_model=Token)
async def login_with_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    authd_user = UserOut.model_validate(user)
    token = create_access_token(data={"sub": authd_user.username})
    return {"access_token": token, "token_type": "bearer"}
