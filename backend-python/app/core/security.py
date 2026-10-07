from datetime import datetime, timedelta, timezone
import hashlib

import jwt
import bcrypt

from app.core.config import settings

def _password_digest(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def hash_password(password: str) -> str:
    digest = _password_digest(password).encode("utf-8")
    return bcrypt.hashpw(digest, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        digest = _password_digest(plain_password).encode("utf-8")
        if bcrypt.checkpw(digest, hashed_password.encode("utf-8")):
            return True
    except (ValueError, TypeError):
        return False

    try:
        # Keep existing accounts created before the password normalization change working.
        if len(plain_password.encode("utf-8")) <= 72 and bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        ):
            return True
    except (ValueError, TypeError):
        return False

    return False


def create_access_token(payload: dict) -> str:
    data = payload.copy()
    expire = datetime.now(timezone.utc) + timedelta(seconds=settings.JWT_EXPIRE_SECONDS)
    data.update({"exp": expire})
    return jwt.encode(data, settings.JWT_SECRET, algorithm="HS256")


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
