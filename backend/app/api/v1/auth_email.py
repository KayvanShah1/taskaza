from __future__ import annotations

from app.core.config import settings
from app.core.dependencies import get_db
from app.core.security import hash_password
from app.crud.email_token import consume_email_token, issue_email_token
from app.models.user import User
from app.schemas.email_token import CompletePasswordReset, RequestPasswordReset, RequestVerifyEmail
from app.services.mailer import send_email
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["Auth Email"])


# 1) Send verification email (after signup or on demand)
@router.post("/verify-email/request", status_code=status.HTTP_202_ACCEPTED)
async def request_verify_email(
    body: RequestVerifyEmail,
    db: AsyncSession = Depends(get_db),
):

    res = await db.execute(select(User).where(User.email == body.email))
    user = res.scalar_one_or_none()
    # Always respond 202 to prevent enumeration, but only send if user exists
    if user and not user.email_verified:
        tok, raw = await issue_email_token(db, user_id=user.id, purpose="verify")
        link = f"{settings.FRONTEND_ORIGIN}/auth/verify-email?token={raw}"
        html = f"<p>Verify your Taskaza email by clicking <a href='{link}'>this link</a>. It expires in 24 hours.</p>"
        await send_email(user.email, "Verify your Taskaza email", html)
    return {"message": "If your email exists and is unverified, a link has been sent."}


# 2) Complete verification
@router.post("/verify-email/complete", status_code=status.HTTP_200_OK)
async def complete_verify_email(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    tok = await consume_email_token(db, token, purpose="verify")
    if not tok:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = tok.user
    if not user.email_verified:
        user.email_verified = True
        await db.commit()
    return {"message": "Email verified successfully."}


# 3) Request password reset
@router.post("/password-reset/request", status_code=status.HTTP_202_ACCEPTED)
async def request_password_reset(
    body: RequestPasswordReset,
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(select(User).where(User.email == body.email))
    user = res.scalar_one_or_none()
    if user:
        tok, raw = await issue_email_token(db, user_id=user.id, purpose="reset")
        link = f"{settings.FRONTEND_ORIGIN}/auth/reset-password?token={raw}"
        html = f"<p>Reset your Taskaza password <a href='{link}'>here</a>. Link valid for 1 hour.</p>"
        await send_email(user.email, "Reset your Taskaza password", html)
    return {"message": "If the account exists, a reset link has been sent."}


# 4) Complete password reset
@router.post("/password-reset/complete", status_code=status.HTTP_200_OK)
async def complete_password_reset(
    body: CompletePasswordReset,
    db: AsyncSession = Depends(get_db),
):
    tok = await consume_email_token(db, body.token, purpose="reset")
    if not tok:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = tok.user

    user.hashed_password = hash_password(body.new_password)
    await db.commit()
    return {"message": "Password reset successfully."}
