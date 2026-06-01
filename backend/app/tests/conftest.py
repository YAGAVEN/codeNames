# backend/app/tests/conftest.py
import os
from collections.abc import AsyncIterator, Iterator
from types import SimpleNamespace

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

os.environ["APP_ENV"] = "test"
os.environ["DEBUG"] = "false"
os.environ["SECRET_KEY"] = "test-secret-key-with-at-least-thirty-two-chars"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["COOKIE_SECURE"] = "false"
os.environ["ALLOWED_ORIGINS"] = "http://test"

from app.api.dependencies.db_deps import get_db
from app.api.dependencies.rate_limit import _rate_windows
from app.core.config import get_settings
from app.core.security import _refresh_tokens, create_access_token
from app.db import models  # noqa: F401
from app.db.base import Base
from app.db.models.user import User
from app.game.game_manager import _game_states
from app.game.word_service import _word_pack_cache
from app.main import app
from app.middleware.rate_limit import _ip_windows
from app.utils.constants import UserRole


@pytest.fixture(autouse=True)
def clear_in_memory_state() -> Iterator[None]:
    """Keep process-memory stores isolated between tests."""
    _refresh_tokens.clear()
    _game_states.clear()
    _word_pack_cache.clear()
    _rate_windows.clear()
    _ip_windows.clear()
    yield
    _refresh_tokens.clear()
    _game_states.clear()
    _word_pack_cache.clear()
    _rate_windows.clear()
    _ip_windows.clear()


@pytest_asyncio.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    """Create an isolated SQLite database per test."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        yield session
    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    """HTTP client with DB dependencies overridden."""

    async def override_get_db() -> AsyncIterator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.state.websocket_manager = SimpleNamespace(settings=get_settings())
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as async_client:
        yield async_client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a normal test user."""
    user = User(username="tester", email="tester@example.com")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Create an admin test user."""
    user = User(username="admin", email="admin@example.com", role=UserRole.ADMIN)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers(test_user: User) -> dict[str, str]:
    """Bearer auth headers for a test user."""
    token = create_access_token(test_user.id, test_user.role.value)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_headers(admin_user: User) -> dict[str, str]:
    """Bearer auth headers for an admin user."""
    token = create_access_token(admin_user.id, admin_user.role.value)
    return {"Authorization": f"Bearer {token}"}
