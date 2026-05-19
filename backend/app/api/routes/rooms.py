# backend/app/api/routes/rooms.py
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth_deps import get_current_user
from app.api.dependencies.db_deps import get_db
from app.api.dependencies.rate_limit import user_route_rate_limit
from app.db.models.user import User
from app.schemas.common import EnvelopeSchema, MessageResponse
from app.schemas.rooms import KickPlayerRequest, PublicRoomRead, RoomCreateRequest, RoomJoinRequest, RoomRead
from app.services.room_service import RoomService
from app.utils.responses import success_response

router = APIRouter()


@router.post("/create", response_model=EnvelopeSchema[RoomRead], summary="Create room")
async def create_room(
    payload: RoomCreateRequest,
    request: Request,
    _rate_limit: None = Depends(user_route_rate_limit),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Create a new waiting room."""
    room = await RoomService(db, request.app.state.redis).create_room(user.id, payload)
    return success_response(room)


@router.post("/join", response_model=EnvelopeSchema[RoomRead], summary="Join room")
async def join_room(
    payload: RoomJoinRequest,
    request: Request,
    _rate_limit: None = Depends(user_route_rate_limit),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Join a room by code."""
    room = await RoomService(db, request.app.state.redis).join_room(user.id, payload)
    return success_response(room)


@router.get("/public", response_model=EnvelopeSchema[list[PublicRoomRead]], summary="List public rooms")
async def public_rooms(page: int = 1, per_page: int = 20, db: AsyncSession = Depends(get_db)) -> dict:
    """List waiting rooms."""
    rooms = await RoomService(db).list_public(page, per_page)
    return success_response(rooms, {"page": page, "per_page": per_page})


@router.get("/{room_id}", response_model=EnvelopeSchema[RoomRead], summary="Get room")
async def get_room(room_id: UUID, db: AsyncSession = Depends(get_db)) -> dict:
    """Return room details."""
    return success_response(await RoomService(db).describe_room(room_id))


@router.delete("/{room_id}", response_model=EnvelopeSchema[MessageResponse], summary="Delete room")
async def delete_room(
    room_id: UUID,
    _rate_limit: None = Depends(user_route_rate_limit),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Delete a room as host."""
    await RoomService(db).delete_room(room_id, user.id)
    return success_response(MessageResponse(message="Room deleted"))


@router.post("/{room_id}/kick", response_model=EnvelopeSchema[MessageResponse], summary="Kick player")
async def kick_player(
    room_id: UUID,
    payload: KickPlayerRequest,
    _rate_limit: None = Depends(user_route_rate_limit),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Kick a player from a hosted room."""
    await RoomService(db).kick_player(room_id, user.id, payload.user_id)
    return success_response(MessageResponse(message="Player kicked"))
