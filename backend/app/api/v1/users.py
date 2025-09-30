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
    summary="Register a new user",
    description=(
        "Create a new user account with a unique username and password. "
        "Optionally provide an email and display name. "
        "Passwords are securely hashed before storage."
    ),
)
async def signup(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    **Sign Up**

    **Request Body**
    - `username` (str, required): Must be unique
    - `password` (str, required): Plaintext input, stored as hash
    - `email` (str, optional): Must be unique if provided
    - `display_name` (str, optional)

    **Responses**
    - `201`: Returns the created `UserOut` (without password)
    - `400`: Username or email already taken
    - `422`: Validation error
    """
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
    summary="Get current user profile",
    description="Retrieve details of the authenticated user (requires JWT + API key).",
)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    **Get Current User**

    **Auth**
    - Requires `Authorization: Bearer <JWT>` and `X-API-Key`.

    **Responses**
    - `200`: Returns current user's `UserOut`
    - `401/403`: Invalid or missing authentication
    """
    return current_user


@router.put(
    "/users/me",
    response_model=UserOut,
    dependencies=[Depends(verify_api_key)],
    status_code=status.HTTP_200_OK,
    summary="Update current user profile",
    description=(
        "Replace the authenticated user's profile fields with the provided values. "
        "Fields not included will be set to null."
    ),
)
async def update_me(
    update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    **Update User (PUT)**

    Completely replace user attributes with the given payload.

    **Auth**
    - Requires `Authorization: Bearer <JWT>` and `X-API-Key`.

    **Request Body**
    - `UserUpdate`: `username`, `email`, and/or `display_name`.

    **Responses**
    - `200`: Updated `UserOut`
    - `400`: Username or email already taken
    - `401/403`: Unauthorized
    """
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
    summary="Update current user profile (partial)",
    description=(
        "Partially update the authenticated user's profile. "
        "Only fields provided will be changed; others remain unchanged."
    ),
)
async def patch_me(
    update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    **Update User (PATCH)**

    Modify one or more attributes of the user without replacing the whole record.

    **Auth**
    - Requires `Authorization: Bearer <JWT>` and `X-API-Key`.

    **Request Body**
    - `UserUpdate`: Any subset of `username`, `email`, `display_name`.

    **Responses**
    - `200`: Updated `UserOut`
    - `400`: Username or email already taken
    - `401/403`: Unauthorized
    """
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


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
    description="Delete a user by ID. Only the user themself can delete their account.",
)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own account.",
        )

    deleted = await crud_user.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return None  # 204 has no response body
