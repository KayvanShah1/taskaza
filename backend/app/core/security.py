import hashlib
import hmac
import secrets
from typing import Tuple

from passlib.context import CryptContext
from app.core.config import settings

# ---------------------------- #
# Password Hashing
# ---------------------------- #
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def generate_api_key() -> Tuple[str, str, str]:
    """
    Returns (display_key, prefix, secret_hash).
    display_key is what you show once: "tsk_<prefix>_<secret>"
    Store only secret_hash in DB using SHA256.
    """
    prefix = secrets.token_hex(3)  # short, user-visible fragment
    secret = secrets.token_urlsafe(32)
    raw = f"{prefix}.{secret}"
    secret_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    display_key = f"{settings.API_KEY_PREFIX}_{prefix}_{secret}"
    return display_key, prefix, secret_hash


def hash_email_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def generate_email_token() -> Tuple[str, str]:
    raw = secrets.token_urlsafe(32)
    return raw, hash_email_token(raw)


def constant_time_equals(a: str, b: str) -> bool:
    return hmac.compare_digest(a, b)
