# backend/app/tests/integration/test_rooms.py
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.core.config import get_settings
from app.db.models.room import Room
from app.repositories.room_repository import RoomRepository
from app.utils.constants import RoomStatus


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


@pytest.mark.asyncio
async def test_inactive_room_cleanup_deletes_only_stale_inactive_rooms(db_session, test_user) -> None:
    """Inactive cleanup should delete stale rooms while preserving active or fresh rooms."""
    now = datetime.now(UTC)
    stale_at = now - timedelta(minutes=11)
    cutoff = now - timedelta(minutes=10)
    stale_room_id = uuid4()
    active_room_id = uuid4()
    fresh_room_id = uuid4()

    db_session.add_all(
        [
            Room(
                id=stale_room_id,
                room_code="STALE1",
                host_id=test_user.id,
                status=RoomStatus.WAITING,
                max_players=8,
                settings={},
                game_state={},
                created_at=stale_at,
                updated_at=stale_at,
            ),
            Room(
                id=active_room_id,
                room_code="ACTIVE1",
                host_id=test_user.id,
                status=RoomStatus.WAITING,
                max_players=8,
                settings={},
                game_state={},
                created_at=stale_at,
                updated_at=stale_at,
            ),
            Room(
                id=fresh_room_id,
                room_code="FRESH1",
                host_id=test_user.id,
                status=RoomStatus.WAITING,
                max_players=8,
                settings={},
                game_state={},
            ),
        ]
    )
    await db_session.commit()

    repo = RoomRepository(db_session)
    deleted = await repo.delete_inactive(cutoff, {"ACTIVE1"})
    await repo.commit()

    assert deleted == 1
    assert await repo.get(stale_room_id) is None
    assert await repo.get(active_room_id) is not None
    assert await repo.get(fresh_room_id) is not None
