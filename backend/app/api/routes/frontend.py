from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Header
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.db_deps import get_db
from app.core.security import decode_token, extract_bearer_token
from app.db.models.game import Game
from app.db.models.match_history import MatchHistory
from app.db.models.room import Room
from app.db.models.room_player import RoomPlayer
from app.db.models.user import User
from app.repositories.achievement_repository import AchievementRepository
from app.repositories.friendship_repository import FriendshipRepository
from app.repositories.user_repository import UserRepository
from app.utils.constants import FriendshipStatus, RoomStatus
from app.utils.exceptions import AuthenticationError
from app.utils.responses import success_response

router = APIRouter()

ACHIEVEMENT_CATALOG = {
    "chai-master": {
        "id": "chai-master",
        "name": "Chai Master",
        "icon": "tea",
        "description": "Gave five winning clues in one evening queue.",
        "rarity": "Rare",
    },
    "diwali-champion": {
        "id": "diwali-champion",
        "name": "Diwali Champion",
        "icon": "lamp",
        "description": "Won a Diwali theme room without hitting neutral cards.",
        "rarity": "Epic",
    },
    "century-maker": {
        "id": "century-maker",
        "name": "Century Maker",
        "icon": "bat",
        "description": "Crossed 100 total correct guesses.",
        "rarity": "Legend",
    },
    "gully-cricket": {
        "id": "gully-cricket",
        "name": "Gully Cricket",
        "icon": "trophy",
        "description": "Won three cricket-heavy games with public teams.",
        "rarity": "Uncommon",
    },
    "bollywood-director": {
        "id": "bollywood-director",
        "name": "Bollywood Director",
        "icon": "film",
        "description": "Connected four cinema clues in one turn.",
        "rarity": "Epic",
    },
}

ROOM_STATUS_LABELS = {
    RoomStatus.WAITING: "Waiting",
    RoomStatus.IN_PROGRESS: "In Game",
    RoomStatus.FINISHED: "Finished",
}


def _display_name(username: str) -> str:
    """Convert stored usernames into frontend display names."""
    return username.replace("_", " ").replace(".", " ").title()


def _win_rate(user: User) -> int:
    """Calculate a frontend-friendly win percentage."""
    total = user.win_count + user.lose_count
    if total <= 0:
        return 0
    return round((user.win_count / total) * 100)


def _user_profile(
    user: User,
    *,
    badges: list[dict[str, Any]] | None = None,
    match_history: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Map backend user fields to the profile shape the React app expects."""
    return {
        "id": str(user.id),
        "name": _display_name(user.username),
        "handle": f"@{user.username}",
        "email": user.email,
        "city": "",
        "level": user.level,
        "xp": user.xp,
        "winRate": _win_rate(user),
        "streak": user.streak,
        "status": user.online_status.value,
        "team": "spectator",
        "role": "Operative",
        "avatar": user.avatar_url or "",
        "badges": badges or [],
        "matchHistory": match_history or [],
    }


def _leaderboard_entry(user: User, rank: int) -> dict[str, Any]:
    """Map a user into the leaderboard row shape used by the frontend."""
    badge = "Maharaja Tier" if rank <= 3 else "Platinum Adda" if rank <= 10 else "Gold Adda"
    return {
        "id": str(user.id),
        "rank": rank,
        "name": _display_name(user.username),
        "country": "India",
        "xp": user.xp,
        "streak": user.streak,
        "winRate": _win_rate(user),
        "badge": badge,
    }


def _room_card(room: Room, host: User, player_count: int) -> dict[str, Any]:
    """Map a backend room into an active-room dashboard card."""
    settings = room.settings or {}
    theme = str(settings.get("theme") or settings.get("festivalTheme") or "Classic")
    is_private = bool(settings.get("password_hash") or settings.get("passwordEnabled"))
    return {
        "id": str(room.id),
        "code": room.room_code,
        "name": str(settings.get("name") or settings.get("roomName") or f"{theme} Room"),
        "host": _user_profile(host),
        "playerCount": player_count,
        "maxPlayers": room.max_players,
        "status": "Private" if is_private else ROOM_STATUS_LABELS.get(room.status, room.status.value),
        "theme": theme,
        "privacy": "Private" if is_private else "Public",
        "settings": settings,
    }


async def _optional_user(authorization: str | None, db: AsyncSession) -> User | None:
    """Load a bearer user when present; ignore missing or stale tokens."""
    if not authorization:
        return None
    try:
        token = extract_bearer_token(authorization)
        payload = decode_token(token)
        return await UserRepository(db).get(UUID(str(payload["sub"])))
    except (AuthenticationError, ValueError):
        return None


async def _dashboard_rooms(db: AsyncSession, limit: int = 12) -> list[dict[str, Any]]:
    """Return active rooms with host and player-count data in one query."""
    counts = (
        select(RoomPlayer.room_id, func.count(RoomPlayer.id).label("player_count"))
        .group_by(RoomPlayer.room_id)
        .subquery()
    )
    statement = (
        select(Room, User, func.coalesce(counts.c.player_count, 0))
        .join(User, Room.host_id == User.id)
        .outerjoin(counts, counts.c.room_id == Room.id)
        .where(Room.status != RoomStatus.FINISHED)
        .order_by(Room.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(statement)
    return [_room_card(room, host, int(player_count)) for room, host, player_count in result.all()]


async def _achievement_badges(db: AsyncSession, user_id: UUID) -> list[dict[str, Any]]:
    """Return badges the user has actually unlocked."""
    rows = await AchievementRepository(db).list_for_user(user_id)
    badges: list[dict[str, Any]] = []
    for row in rows:
        badge = dict(ACHIEVEMENT_CATALOG.get(row.badge_key, {}))
        if not badge:
            badge = {
                "id": row.badge_key,
                "name": _display_name(row.badge_key),
                "icon": "medal",
                "description": "Unlocked through match play.",
                "rarity": "Earned",
            }
        badge["unlockedAt"] = row.unlocked_at.isoformat()
        badges.append(badge)
    return badges


async def _match_history(db: AsyncSession, user_id: UUID, limit: int = 10) -> list[dict[str, Any]]:
    """Return persisted match-history rows for the frontend profile cards."""
    statement = (
        select(MatchHistory, Game, Room)
        .join(Game, MatchHistory.game_id == Game.id)
        .join(Room, Game.room_id == Room.id)
        .where(MatchHistory.user_id == user_id)
        .order_by(MatchHistory.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(statement)
    history: list[dict[str, Any]] = []
    for row, game, room in result.all():
        settings = room.settings or {}
        room_name = str(settings.get("name") or settings.get("roomName") or room.room_code)
        history.append(
            {
                "id": str(row.id),
                "room": room_name,
                "result": "Win" if row.is_winner else "Loss",
                "score": f"{game.red_score}-{game.blue_score}",
                "role": _display_name(row.role.value),
                "team": row.team.value,
                "playedAt": row.created_at.isoformat(),
                "xpEarned": row.xp_earned,
                "cluesGiven": row.clues_given,
                "correctGuesses": row.correct_guesses,
            }
        )
    return history


async def _friends(db: AsyncSession, user_id: UUID) -> list[dict[str, Any]]:
    """Return accepted friends from persisted friendship rows."""
    relationships = await FriendshipRepository(db).list_for_user(user_id, FriendshipStatus.ACCEPTED)
    users = UserRepository(db)
    friends: list[dict[str, Any]] = []
    for relationship in relationships:
        friend_id = relationship.addressee_id if relationship.requester_id == user_id else relationship.requester_id
        friend = await users.get(friend_id)
        if friend is not None:
            friends.append(_user_profile(friend))
    return friends


async def _friend_requests(db: AsyncSession, user_id: UUID) -> list[dict[str, Any]]:
    """Return incoming pending friend requests from persisted data."""
    relationships = await FriendshipRepository(db).list_requests(user_id)
    users = UserRepository(db)
    requests: list[dict[str, Any]] = []
    for relationship in relationships:
        requester = await users.get(relationship.requester_id)
        if requester is not None:
            requests.append({"id": str(relationship.id), "from": _user_profile(requester), "createdAt": relationship.created_at.isoformat()})
    return requests


@router.get("/dashboard", summary="Frontend dashboard data")
async def dashboard(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Return the aggregate data needed by the React dashboard."""
    current_user = await _optional_user(authorization, db)
    current_profile = None
    friends: list[dict[str, Any]] = []
    friend_requests: list[dict[str, Any]] = []
    achievements: list[dict[str, Any]] = []
    if current_user is not None:
        achievements = await _achievement_badges(db, current_user.id)
        current_profile = _user_profile(
            current_user,
            badges=achievements,
            match_history=await _match_history(db, current_user.id),
        )
        friends = await _friends(db, current_user.id)
        friend_requests = await _friend_requests(db, current_user.id)

    return success_response(
        {
            "currentUser": current_profile,
            "rooms": await _dashboard_rooms(db),
            "friends": friends,
            "friendRequests": friend_requests,
            "achievements": achievements,
        }
    )


@router.get("/leaderboard", summary="Frontend leaderboard")
async def leaderboard(limit: int = 50, db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """Return leaderboard rows in the shape consumed by the React page."""
    users = await UserRepository(db).leaderboard(limit)
    return success_response([_leaderboard_entry(user, index + 1) for index, user in enumerate(users)])
