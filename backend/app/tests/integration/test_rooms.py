# backend/app/tests/integration/test_rooms.py
import pytest
from httpx import AsyncClient

from app.core.config import get_settings


@pytest.mark.asyncio
async def test_room_create_and_public_listing(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    """Room creation should add host membership and appear in public listing."""
    created = await client.post("/api/rooms/create", json={"max_players": 8, "settings": {}}, headers=auth_headers)
    assert created.status_code == 200
    room = created.json()["data"]
    assert room["room_code"]
    assert len(room["players"]) == 1

    listed = await client.get("/api/rooms/public")
    assert listed.status_code == 200
    assert listed.json()["data"][0]["room_code"] == room["room_code"]


@pytest.mark.asyncio
async def test_rate_limited_response_keeps_cors_headers(client: AsyncClient) -> None:
    """CORS should wrap middleware-generated error responses."""
    settings = get_settings()
    original_limit = settings.RATE_LIMIT_REQUESTS
    settings.RATE_LIMIT_REQUESTS = 0

    try:
        response = await client.get("/api/rooms/public", headers={"Origin": "http://test"})
    finally:
        settings.RATE_LIMIT_REQUESTS = original_limit

    assert response.status_code == 429
    assert response.headers["access-control-allow-origin"] == "http://test"
