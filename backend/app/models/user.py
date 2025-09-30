from app.db.session import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base):
    __tablename__ = "users"

    # --- columns ---
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

    # store a password hash (e.g., bcrypt) — never raw passwords
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # optional fields
    email: Mapped[str | None] = mapped_column(String(320), unique=True, index=True, nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # verification flag
    email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0")

    # timestamps (helpful for auditing)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    verification_token = Column(String, unique=True, index=True, nullable=True)
    verification_token_expires = Column(DateTime, nullable=True)

    # relationships
    tasks = relationship(
        "Task",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
        single_parent=True,
    )

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r}, email={self.email!r})"
