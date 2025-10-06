from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from app.db.session import Base
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class APIKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    # Store only a hash of the secret part; never the raw key
    secret_hash: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    # Showable prefix to help users identify which key (e.g., "tsk_live_2f9a")
    prefix: Mapped[str] = mapped_column(String(32), index=True)
    scopes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON-encoded list if you want
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=False), index=True)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.now(timezone.utc))
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=False), nullable=True)

    user = relationship("User", back_populates="api_keys")


Index("ix_api_keys_user_active", APIKey.user_id, APIKey.revoked)
