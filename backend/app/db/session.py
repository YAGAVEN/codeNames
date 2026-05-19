# backend/app/db/session.py
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

settings = get_settings()

engine_kwargs = {"pool_pre_ping": True, "future": True}
if not settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs.update({"pool_size": 20, "max_overflow": 40})

engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Yield an async SQLAlchemy session for dependency injection."""
    async with AsyncSessionLocal() as session:
        yield session
