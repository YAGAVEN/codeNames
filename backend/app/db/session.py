# backend/app/db/session.py
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.db.engine import build_engine_config

settings = get_settings()
engine_config = build_engine_config(settings.DATABASE_URL)
database_url = engine_config.database_url

if database_url.startswith("postgresql") and "+asyncpg" not in database_url:
    raise RuntimeError("DATABASE_URL must use asyncpg (postgresql+asyncpg://)")

engine_kwargs = {"pool_pre_ping": True, "future": True}
if engine_config.connect_args:
    engine_kwargs["connect_args"] = engine_config.connect_args
if not database_url.startswith("sqlite"):
    engine_kwargs.update(
        {
            "pool_size": settings.DB_POOL_SIZE,
            "max_overflow": settings.DB_MAX_OVERFLOW,
            "pool_timeout": settings.DB_POOL_TIMEOUT_SECONDS,
            "pool_recycle": settings.DB_POOL_RECYCLE_SECONDS,
        }
    )

engine = create_async_engine(database_url, **engine_kwargs)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Yield an async SQLAlchemy session for dependency injection."""
    async with AsyncSessionLocal() as session:
        yield session
