from uuid import uuid4

from app.api.routes.frontend import _leaderboard_entry, _room_card, _user_profile
from app.db.models.room import Room
from app.db.models.user import User
from app.utils.constants import OnlineStatus, RoomStatus, UserRole


def test_user_profile_returns_frontend_shape() -> None:
    """User mapper should expose the fields consumed by React profile cards."""
    user = User(
        id=uuid4(),
        username="test_player",
        email="tester@example.com",
        xp=1234,
        level=12,
        win_count=3,
        lose_count=1,
        streak=4,
        online_status=OnlineStatus.ONLINE,
        role=UserRole.PLAYER,
    )

    profile = _user_profile(user)
    assert profile["name"] == "Test Player"
    assert profile["winRate"] == 75
    assert profile["matchHistory"] == []


def test_room_card_returns_frontend_shape() -> None:
    """Room mapper should expose the dashboard card fields used by React."""
    host = User(
        id=uuid4(),
        username="host_user",
        email="host@example.com",
        xp=0,
        level=1,
        win_count=0,
        lose_count=0,
        streak=0,
        online_status=OnlineStatus.ONLINE,
        role=UserRole.PLAYER,
    )
    room = Room(
        id=uuid4(),
        room_code="TEST01",
        host_id=host.id,
        status=RoomStatus.WAITING,
        max_players=8,
        settings={"name": "Test Adda", "theme": "Diwali"},
        game_state={},
    )

    card = _room_card(room, host, 1)
    assert card["name"] == "Test Adda"
    assert card["code"] == "TEST01"
    assert card["status"] == "Waiting"
    assert card["playerCount"] == 1


def test_leaderboard_entry_returns_frontend_shape() -> None:
    """Leaderboard mapper should expose display names and rank metadata."""
    user = User(
        id=uuid4(),
        username="tester",
        email="tester@example.com",
        xp=1234,
        level=1,
        win_count=3,
        lose_count=1,
        streak=2,
        online_status=OnlineStatus.ONLINE,
        role=UserRole.PLAYER,
    )

    row = _leaderboard_entry(user, 1)
    assert row["rank"] == 1
    assert row["name"] == "Tester"
    assert row["winRate"] == 75
