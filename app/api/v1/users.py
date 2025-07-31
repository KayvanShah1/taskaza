from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db
from app.schemas import UserCreate, UserOut
from app.crud import user as crud_user

router = APIRouter()


@router.post(
    "/signup",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    response_description="Successfully registered a new user",
)
async def signup(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await crud_user.get_user_by_username(db, user_in.username)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
    user = await crud_user.create_user(db, user_in.username, user_in.password)
    return user
