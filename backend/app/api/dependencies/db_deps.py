# backend/app/api/dependencies/db_deps.py
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency returning an async database session."""
    async for session in get_session():
        yield session
