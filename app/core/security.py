from datetime import UTC, datetime, timedelta
from typing import Any

from jose import jwt

from app.core.config import settings

ALGORITHM = "HS256"


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload: dict[str, Any] = {"sub": subject, "exp": expire}
    token: str = jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)
    return token
