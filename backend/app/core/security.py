# backend/app/core/security.py
import time
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import JWTError, jwt

from app.core.config import get_settings
from app.utils.exceptions import AuthenticationError

password_hasher = PasswordHasher()
_refresh_tokens: dict[str, tuple[str, float]] = {}


def hash_password(password: str) -> str:
    """Hash a password with Argon2id for custom-auth fallback flows."""
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify an Argon2id password hash without leaking mismatch details."""
    try:
        return password_hasher.verify(password_hash, password)
    except VerifyMismatchError:
        return False


def create_access_token(subject: UUID | str, role: str, extra: dict[str, Any] | None = None) -> str:
    """Create a short-lived signed access token."""
    settings = get_settings()
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "role": role,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


async def create_refresh_token(subject: UUID | str) -> str:
    """Create and persist a rotating refresh token identifier in memory."""
    settings = get_settings()
    _purge_expired_tokens()
    now = datetime.now(UTC)
    jti = str(uuid4())
    expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(subject),
        "jti": jti,
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": expires_at,
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    _refresh_tokens[jti] = (str(subject), expires_at.timestamp())
    return token


async def rotate_refresh_token(token: str) -> tuple[UUID, str]:
    """Validate a refresh token, invalidate it, and issue a replacement."""
    payload = decode_token(token, expected_type="refresh")
    jti = str(payload["jti"])
    subject = UUID(str(payload["sub"]))
    _purge_expired_tokens()
    stored = _refresh_tokens.get(jti)
    if stored is None:
        raise AuthenticationError("Refresh token has expired or was already used")
    stored_subject, expires_at = stored
    if expires_at < time.time():
        _refresh_tokens.pop(jti, None)
        raise AuthenticationError("Refresh token has expired or was already used")
    if stored_subject != str(subject):
        raise AuthenticationError("Refresh token subject mismatch")
    _refresh_tokens.pop(jti, None)
    return subject, await create_refresh_token(subject)


async def revoke_refresh_token(token: str) -> None:
    """Invalidate a refresh token if it is still present."""
    try:
        payload = decode_token(token, expected_type="refresh")
    except AuthenticationError:
        return
    _refresh_tokens.pop(str(payload["jti"]), None)


def create_password_reset_token(subject: UUID | str) -> str:
    """Create a short-lived signed password-reset token."""
    settings = get_settings()
    now = datetime.now(UTC)
    payload = {
        "sub": str(subject),
        "type": "password_reset",
        "iat": int(now.timestamp()),
        "exp": now + timedelta(minutes=settings.PASSWORD_RESET_TOKEN_MINUTES),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str, expected_type: str = "access") -> dict[str, Any]:
    """Decode and verify a JWT payload for a specific token purpose."""
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as exc:
        raise AuthenticationError("Invalid or expired token") from exc
    if payload.get("type") != expected_type:
        raise AuthenticationError("Invalid token type")
    return payload


def extract_bearer_token(authorization: str | None) -> str:
    """Extract a Bearer token from an Authorization header."""
    if not authorization:
        raise AuthenticationError("Missing Authorization header")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise AuthenticationError("Authorization header must use Bearer token")
    return token


def _purge_expired_tokens() -> None:
    """Remove expired in-memory refresh tokens."""
    now = time.time()
    expired = [jti for jti, (_, expires_at) in _refresh_tokens.items() if expires_at < now]
    for jti in expired:
        _refresh_tokens.pop(jti, None)
