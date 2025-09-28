from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import authenticate_user, create_access_token
from app.core.dependencies import get_db
from app.schemas.token import Token
from app.schemas.user import UserOut

router = APIRouter(tags=["Login"])


@router.post(
    "/token",
    response_model=Token,
    summary="Login with username and password",
    description="""
Obtain a **JWT access token** using the OAuth2 password flow.

### Authentication
- Requires valid username and password.

### Usage
- Use the returned `access_token` in the `Authorization` header for all protected endpoints:
    `Authorization: Bearer <access_token>`

### Notes
- This endpoint does **not** require API Key.
- Token expiration and lifetime are configured in `create_access_token`.
  """,
)
async def login_with_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    **Login with Access Token**

    **Request Body (form-data)**
    - `username` (str): Registered username
    - `password` (str): Corresponding password

    **Responses**
    - `200`: Returns a `Token` object
      ```json
      {
        "access_token": "jwt.token.here",
        "token_type": "bearer"
      }
      ```
    - `401`: Incorrect username or password
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    authd_user = UserOut.model_validate(user)
    token = create_access_token(data={"sub": authd_user.username})
    return {"access_token": token, "token_type": "bearer"}
