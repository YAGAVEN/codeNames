# backend/app/services/room_service.py
import logging
import secrets
import string
from uuid import UUID

from redis.asyncio import Redis
from redis.exceptions import RedisError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import disconnect_redis_pool
from app.core.security import verify_password
from app.repositories.room_player_repository import RoomPlayerRepository
from app.repositories.room_repository import RoomRepository
from app.schemas.rooms import PublicRoomRead, RoomCreateRequest, RoomJoinRequest, RoomPlayerRead, RoomRead
from app.utils.constants import PlayerRole, RoomStatus, Team
from app.utils.exceptions import AuthorizationError, ConflictError, NotFoundError

logger = logging.getLogger(__name__)


class RoomService:
    """Room lifecycle and membership business logic."""

    def __init__(self, session: AsyncSession, redis: Redis | None = None) -> None:
        self.rooms = RoomRepository(session)
        self.players = RoomPlayerRepository(session)
        self.redis = redis

    async def create_room(self, host_id: UUID, payload: RoomCreateRequest) -> RoomRead:
        """Create a room and add the host as the first player."""
        room_code = await self._unique_room_code()
        room = await self.rooms.create(room_code, host_id, payload.max_players, payload.settings)
        membership = await self.players.add_player(room.id, host_id, Team.RED, PlayerRole.SPYMASTER)
        await self._cache_membership(room.id, host_id, membership.team, membership.role)
        await self.rooms.commit()
        await self.rooms.refresh(room)
        return await self.describe_room(room.id)

    async def join_room(self, user_id: UUID, payload: RoomJoinRequest) -> RoomRead:
        """Validate and join a room by code."""
        room = await self.rooms.get_by_code(payload.room_code)
        if room is None:
            raise NotFoundError("Room not found")
        if room.status != RoomStatus.WAITING:
            raise ConflictError("Room is not accepting players")
        banned_user_ids = {str(item) for item in room.settings.get("banned_user_ids", [])}
        if str(user_id) in banned_user_ids:
            raise AuthorizationError("User is banned from this room")
        password_hash = room.settings.get("password_hash")
        if password_hash and (payload.password is None or not verify_password(payload.password, str(password_hash))):
            raise AuthorizationError("Incorrect room password")
        count = await self.players.count_by_room(room.id)
        if count >= room.max_players:
            raise ConflictError("Room is full")
        existing = await self.players.get_membership(room.id, user_id)
        if existing is None:
            team, role = await self._assign_team_role(room.id, payload.team)
            membership = await self.players.add_player(room.id, user_id, team, role)
            await self._cache_membership(room.id, user_id, membership.team, membership.role)
            await self.rooms.commit()
        return await self.describe_room(room.id)

    async def describe_room_by_code(self, room_code: str) -> RoomRead:
        """Return room details by public room code."""
        room = await self.rooms.get_by_code(room_code)
        if room is None:
            raise NotFoundError("Room not found")
        return await self.describe_room(room.id)

    async def describe_room(self, room_id: UUID) -> RoomRead:
        """Return room details with players."""
        room = await self.rooms.get(room_id)
        if room is None:
            raise NotFoundError("Room not found")
        players = await self.players.list_by_room(room_id)
        return RoomRead(
            id=room.id,
            room_code=room.room_code,
            host_id=room.host_id,
            status=room.status,
            max_players=room.max_players,
            settings=room.settings,
            game_state=room.game_state,
            created_at=room.created_at,
            updated_at=room.updated_at,
            players=[
                RoomPlayerRead(
                    user_id=membership.user_id,
                    username=user.username if user else None,
                    team=membership.team,
                    role=membership.role,
                    is_ready=membership.is_ready,
                    joined_at=membership.joined_at,
                )
                for membership, user in players
            ],
        )

    async def delete_room(self, room_id: UUID, requester_id: UUID, is_admin: bool = False) -> None:
        """Delete a room when requested by its host or an admin."""
        room = await self.rooms.get(room_id)
        if room is None:
            raise NotFoundError("Room not found")
        if room.host_id != requester_id and not is_admin:
            raise AuthorizationError("Only the host can delete this room")
        await self.rooms.delete(room)
        await self.rooms.commit()

    async def list_public(self, page: int, per_page: int) -> list[PublicRoomRead]:
        """List waiting public rooms."""
        rows = await self.rooms.list_public(limit=per_page, offset=(page - 1) * per_page)
        return [
            PublicRoomRead(
                id=room.id,
                room_code=room.room_code,
                host_id=room.host_id,
                status=room.status,
                max_players=room.max_players,
                player_count=count,
                created_at=room.created_at,
            )
            for room, count in rows
        ]

    async def kick_player(self, room_id: UUID, host_id: UUID, target_id: UUID) -> None:
        """Remove a player from a room by host action."""
        room = await self.rooms.get(room_id)
        if room is None:
            raise NotFoundError("Room not found")
        if room.host_id != host_id:
            raise AuthorizationError("Only the host can kick players")
        if target_id == host_id:
            raise ConflictError("Host cannot kick themselves")
        await self.players.remove_player(room_id, target_id)
        await self.rooms.commit()

    async def _unique_room_code(self) -> str:
        """Generate a unique short room code."""
        alphabet = string.ascii_uppercase + string.digits
        for _ in range(10):
            code = "".join(secrets.choice(alphabet) for _ in range(6))
            if await self.rooms.get_by_code(code) is None:
                return code
        raise ConflictError("Could not allocate a unique room code")

    async def _assign_team_role(self, room_id: UUID, requested_team: Team) -> tuple[Team, PlayerRole]:
        """Balance new players across teams and ensure each team gets a spymaster."""
        if requested_team != Team.SPECTATOR:
            team = requested_team
        else:
            rows = await self.players.list_by_room(room_id)
            counts = {
                Team.RED: sum(1 for membership, _ in rows if membership.team == Team.RED),
                Team.BLUE: sum(1 for membership, _ in rows if membership.team == Team.BLUE),
            }
            team = Team.BLUE if counts[Team.BLUE] <= counts[Team.RED] else Team.RED

        rows = await self.players.list_by_room(room_id)
        has_spymaster = any(membership.team == team and membership.role == PlayerRole.SPYMASTER for membership, _ in rows)
        return team, PlayerRole.OPERATIVE if has_spymaster else PlayerRole.SPYMASTER

    async def _cache_membership(self, room_id: UUID, user_id: UUID, team: Team, role: PlayerRole) -> None:
        """Cache trusted team/role membership for WebSocket anti-cheat checks."""
        if self.redis is not None:
            try:
                await self.redis.hset(f"room:membership:{room_id}", str(user_id), f"{team.value}:{role.value}")
            except RedisError:
                logger.warning(
                    "room_membership_cache_failed",
                    extra={"room_id": str(room_id), "user_id": str(user_id)},
                    exc_info=True,
                )
                await disconnect_redis_pool(self.redis)
