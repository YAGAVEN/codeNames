# backend/app/tests/integration/test_rate_limit.py
import pytest
from httpx import AsyncClient

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
