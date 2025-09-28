from app.core.dependencies import get_current_user, get_db, verify_api_key
from app.crud import user as crud_user
from app.schemas.user import UserCreate, UserOut, UserUpdate
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User

router = APIRouter(tags=["Users"])


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
    if user_in.email:
        email_existing = await crud_user.get_user_by_email(db, user_in.email)
        if email_existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already taken")
    user = await crud_user.create_user(
        db,
        user_in.username,
        user_in.password,
        email=user_in.email,
        display_name=user_in.display_name,
    )
    return user


@router.get(
    "/users/me",
    response_model=UserOut,
    dependencies=[Depends(verify_api_key)],
    status_code=status.HTTP_200_OK,
)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put(
    "/users/me",
    response_model=UserOut,
    dependencies=[Depends(verify_api_key)],
    status_code=status.HTTP_200_OK,
)
async def update_me(
    update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    data = update.model_dump(exclude_unset=True)
    if "username" in data:
        existing = await crud_user.get_user_by_username(db, data["username"])
        if existing and existing.id != current_user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
    if "email" in data:
        existing = await crud_user.get_user_by_email(db, data["email"])
        if existing and existing.id != current_user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already taken")
    return await crud_user.update_user(db, current_user, data)


@router.patch(
    "/users/me",
    response_model=UserOut,
    dependencies=[Depends(verify_api_key)],
    status_code=status.HTTP_200_OK,
)
async def patch_me(
    update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    data = update.model_dump(exclude_unset=True)
    if "username" in data:
        existing = await crud_user.get_user_by_username(db, data["username"])
        if existing and existing.id != current_user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
    if "email" in data:
        existing = await crud_user.get_user_by_email(db, data["email"])
        if existing and existing.id != current_user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already taken")
    return await crud_user.update_user(db, current_user, data)
