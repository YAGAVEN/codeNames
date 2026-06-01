# backend/app/core/config.py
import logging
from functools import lru_cache
from typing import Annotated, Literal
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from pydantic import AliasChoices, AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict
from supabase import Client, create_client

logger = logging.getLogger(__name__)


def _redact_database_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme.startswith("sqlite"):
        return value
    netloc = parsed.hostname or ""
    if parsed.port:
        netloc = f"{netloc}:{parsed.port}"
    return urlunparse((parsed.scheme, netloc, parsed.path, "", parsed.query, ""))


class Settings(BaseSettings):
    """Typed application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "Codenames India API"
    APP_ENV: Literal["development", "staging", "production", "test"] = "development"
    DEBUG: bool = False
    API_PREFIX: str = "/api"
    SECRET_KEY: str = Field(min_length=32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_RESET_TOKEN_MINUTES: int = 30
    ALLOWED_ORIGINS: Annotated[list[str], NoDecode] = [
        "http://localhost:5173",
        "https://code-names-theta.vercel.app",
    ]
    ALLOWED_ORIGIN_REGEX: str | None = None
    DATABASE_URL: str = Field(
        validation_alias=AliasChoices("DATABASE_URL", "RENDER_DATABASE_URL", "RENDER_DB_URL", "POSTGRES_URL"),
    )
    TEST_DATABASE_URL: str = "sqlite+aiosqlite:///:memory:"
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CONNECT_TIMEOUT_SECONDS: float = 2.0
    REDIS_SOCKET_TIMEOUT_SECONDS: float = 2.0
    REDIS_HEALTH_CHECK_INTERVAL_SECONDS: int = 30
    REDIS_RECONNECT_INTERVAL_SECONDS: int = 5
    REDIS_STARTUP_RETRIES: int = 3
    REDIS_STARTUP_RETRY_DELAY_SECONDS: float = 1.0
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    SUPABASE_URL: AnyHttpUrl | None = None
    SUPABASE_ANON_KEY: str | None = None
    SUPABASE_SERVICE_KEY: str | None = None
    SUPABASE_JWT_SECRET: str | None = None
    SUPABASE_REDIRECT_URL: str = "http://localhost:8000/api/auth/google/callback"
    FRONTEND_URL: str = "http://localhost:5173"
    AVATARS_BUCKET: str = "avatars"
    WORD_PACKS_BUCKET: str = "word_packs"
    COOKIE_SECURE: bool = True
    COOKIE_DOMAIN: str | None = None
    RATE_LIMIT_REQUESTS: int = 120
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    WS_HEARTBEAT_SECONDS: int = 30
    WS_DEAD_SECONDS: int = 90
    ROOM_RECONNECT_GRACE_SECONDS: int = 30
    DEFAULT_TURN_SECONDS: int = 90
    LOG_LEVEL: str = "INFO"

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: str | list[str]) -> list[str]:
        """Accept comma-separated origins from env files."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str | None) -> str:
        """Normalize database URLs to asyncpg and enforce Supabase SSL."""
        if not value:
            raise ValueError("DATABASE_URL is required")
        raw = str(value).strip()
        normalized = raw
        if raw.startswith("postgresql+asyncpg://"):
            normalized = raw
        elif raw.startswith(("postgresql+psycopg2://", "postgresql+psycopg://")):
            raise ValueError("DATABASE_URL must use asyncpg (postgresql+asyncpg://)")
        elif raw.startswith("postgres://"):
            normalized = "postgresql+asyncpg://" + raw[len("postgres://") :]
        elif raw.startswith("postgresql://"):
            normalized = "postgresql+asyncpg://" + raw[len("postgresql://") :]
        elif raw.startswith(("sqlite+aiosqlite://", "sqlite://")):
            return raw
        else:
            raise ValueError("DATABASE_URL must start with postgresql or sqlite")

        parsed = urlparse(normalized)
        if not parsed.hostname:
            raise ValueError("DATABASE_URL must include a hostname")
        qs = dict(parse_qsl(parsed.query, keep_blank_values=True))
        ssl_enforced = False
        if parsed.hostname.endswith("supabase.co") and "ssl" not in qs and "sslmode" not in qs:
            qs["ssl"] = "require"
            ssl_enforced = True
            normalized = urlunparse(parsed._replace(query=urlencode(qs)))
        if normalized != raw:
            logger.info(
                "database_url_normalized",
                extra={"database_url": _redact_database_url(normalized), "ssl_enforced": ssl_enforced},
            )
        return normalized

    @property
    def is_production(self) -> bool:
        """Return whether the app is running with production defaults."""
        return self.APP_ENV == "production"


@lru_cache
def get_settings() -> Settings:
    """Return cached settings so imports do not repeatedly parse the env file."""
    return Settings()  # type: ignore[call-arg]


@lru_cache
def get_supabase_admin_client() -> Client | None:
    """Create a Supabase service-role client when credentials are configured."""
    settings = get_settings()
    if settings.APP_ENV == "test":
        return None
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
        # TODO: Configure SUPABASE_URL and SUPABASE_SERVICE_KEY in production.
        return None
    return create_client(str(settings.SUPABASE_URL), settings.SUPABASE_SERVICE_KEY)


@lru_cache
def get_supabase_anon_client() -> Client | None:
    """Create an anon Supabase client for OAuth redirect and public auth calls."""
    settings = get_settings()
    if settings.APP_ENV == "test":
        return None
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        # TODO: Configure SUPABASE_URL and SUPABASE_ANON_KEY in production.
        return None
    return create_client(str(settings.SUPABASE_URL), settings.SUPABASE_ANON_KEY)
