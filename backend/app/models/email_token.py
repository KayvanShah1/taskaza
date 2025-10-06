from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal, Optional

from app.db.session import Base
from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

EmailPurpose = Literal["verify", "reset"]


class EmailToken(Base):
    __tablename__ = "email_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    purpose: Mapped[str] = mapped_column(Enum("verify", "reset", name="email_token_purpose"))
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), index=True)
    consumed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=False), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.now(timezone.utc))

    user = relationship("User", back_populates="email_tokens", lazy="selectin")


Index("ix_email_tokens_user_purpose", EmailToken.user_id, EmailToken.purpose)
