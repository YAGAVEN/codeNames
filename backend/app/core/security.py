# backend/app/core/security.py
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import JWTError, jwt
from redis.asyncio import Redis

from app.core.config import get_settings
from app.utils.exceptions import AuthenticationError

password_hasher = PasswordHasher()


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


async def create_refresh_token(redis: Redis, subject: UUID | str) -> str:
    """Create and persist a rotating refresh token identifier in Redis."""
    settings = get_settings()
    now = datetime.now(UTC)
    jti = str(uuid4())
    payload = {
        "sub": str(subject),
        "jti": jti,
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    ttl = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    await redis.setex(f"refresh:{jti}", ttl, str(subject))
    return token


async def rotate_refresh_token(redis: Redis, token: str) -> tuple[UUID, str]:
    """Validate a refresh token, invalidate it, and issue a replacement."""
    payload = decode_token(token, expected_type="refresh")
    jti = str(payload["jti"])
    subject = UUID(str(payload["sub"]))
    stored_subject = await redis.get(f"refresh:{jti}")
    if stored_subject is None:
        raise AuthenticationError("Refresh token has expired or was already used")
    if stored_subject.decode() != str(subject):
        raise AuthenticationError("Refresh token subject mismatch")
    await redis.delete(f"refresh:{jti}")
    return subject, await create_refresh_token(redis, subject)


async def revoke_refresh_token(redis: Redis, token: str) -> None:
    """Invalidate a refresh token if it is still present."""
    try:
        payload = decode_token(token, expected_type="refresh")
    except AuthenticationError:
        return
    await redis.delete(f"refresh:{payload['jti']}")


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
