from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from app.core.security import generate_email_token, hash_email_token
from app.core.timeutils import as_aware_utc
from app.models.email_token import EmailToken
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

DEFAULT_VERIFY_TTL = timedelta(hours=24)
DEFAULT_RESET_TTL = timedelta(hours=1)


async def issue_email_token(db: AsyncSession, user_id: int, purpose: str, ttl: Optional[timedelta] = None):
    raw, thash = generate_email_token()
    expires_at = datetime.now(timezone.utc) + (
        ttl or (DEFAULT_VERIFY_TTL if purpose == "verify" else DEFAULT_RESET_TTL)
    )
    tok = EmailToken(user_id=user_id, purpose=purpose, token_hash=thash, expires_at=expires_at)
    db.add(tok)
    await db.commit()
    await db.refresh(tok)
    return tok, raw


async def consume_email_token(db: AsyncSession, raw_token: str, purpose: str) -> Optional[EmailToken]:
    thash = hash_email_token(raw_token)
    q = select(EmailToken).where(EmailToken.token_hash == thash, EmailToken.purpose == purpose)
    res = await db.execute(q)
    tok = res.scalar_one_or_none()

    now = datetime.now(timezone.utc)
    exp = as_aware_utc(tok.expires_at)
    if not tok or tok.consumed_at or exp <= now:
        return None
    tok.consumed_at = now

    await db.commit()
    return tok
