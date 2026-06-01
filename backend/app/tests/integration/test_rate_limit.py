# backend/app/tests/integration/test_rate_limit.py
import pytest
from httpx import AsyncClient
from redis.exceptions import ConnectionError

from app.main import app


@pytest.mark.asyncio
async def test_user_rate_limit_enforced(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    """User-route rate limit should reject requests over the configured window."""
    original_limit = app.state.websocket_manager.settings.RATE_LIMIT_REQUESTS
    app.state.websocket_manager.settings.RATE_LIMIT_REQUESTS = 1
    first = await client.get("/api/users/me", headers=auth_headers)
    second = await client.get("/api/users/me", headers=auth_headers)
    app.state.websocket_manager.settings.RATE_LIMIT_REQUESTS = original_limit
    assert first.status_code == 200
    assert second.status_code == 429


@pytest.mark.asyncio
async def test_user_rate_limit_fails_open_when_redis_unavailable(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    """Authenticated routes should remain available during Redis outages."""

    class FailingRedis:
        async def incr(self, key: str) -> int:
            raise ConnectionError("redis unavailable")

        async def zremrangebyscore(self, key: str, min_score: int, max_score: int) -> int:
            raise ConnectionError("redis unavailable")

    original_redis = app.state.redis
    original_available = app.state.redis_available
    app.state.redis = FailingRedis()
    app.state.redis_available = True

    try:
        response = await client.get("/api/users/me", headers=auth_headers)
    finally:
        app.state.redis = original_redis
        app.state.redis_available = original_available

    assert response.status_code == 200
