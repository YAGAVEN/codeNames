# backend/app/core/config.py
from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from supabase import Client, create_client


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
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173"]
    DATABASE_URL: str
    TEST_DATABASE_URL: str = "sqlite+aiosqlite:///:memory:"
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    SUPABASE_URL: AnyHttpUrl | None = None
    SUPABASE_ANON_KEY: str | None = None
    SUPABASE_SERVICE_KEY: str | None = None
    SUPABASE_JWT_SECRET: str | None = None
    SUPABASE_REDIRECT_URL: str = "http://localhost:8000/api/auth/google/callback"
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
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
        # TODO: Configure SUPABASE_URL and SUPABASE_SERVICE_KEY in production.
        return None
    return create_client(str(settings.SUPABASE_URL), settings.SUPABASE_SERVICE_KEY)


@lru_cache
def get_supabase_anon_client() -> Client | None:
    """Create an anon Supabase client for OAuth redirect and public auth calls."""
    settings = get_settings()
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        # TODO: Configure SUPABASE_URL and SUPABASE_ANON_KEY in production.
        return None
    return create_client(str(settings.SUPABASE_URL), settings.SUPABASE_ANON_KEY)
