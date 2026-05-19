# backend/app/api/routes/friends.py
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth_deps import get_current_user
from app.api.dependencies.db_deps import get_db
from app.api.dependencies.rate_limit import user_route_rate_limit
from app.db.models.user import User
from app.schemas.common import EnvelopeSchema, MessageResponse
from app.schemas.friends import FriendRequestCreate, FriendshipRead
from app.services.friend_service import FriendService
from app.utils.responses import success_response

router = APIRouter()


@router.post("/request", response_model=EnvelopeSchema[FriendshipRead], summary="Send friend request")
async def request_friend(
    payload: FriendRequestCreate,
    _rate_limit: None = Depends(user_route_rate_limit),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Send a friend request."""
    friendship = await FriendService(db).request(user.id, payload.addressee_id)
    return success_response(friendship)


@router.post("/accept/{id}", response_model=EnvelopeSchema[FriendshipRead], summary="Accept friend request")
async def accept_friend(
    id: UUID,
    _rate_limit: None = Depends(user_route_rate_limit),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Accept an incoming friend request."""
    return success_response(await FriendService(db).accept(user.id, id))


@router.delete("/remove/{id}", response_model=EnvelopeSchema[MessageResponse], summary="Remove friend")
async def remove_friend(
    id: UUID,
    _rate_limit: None = Depends(user_route_rate_limit),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Remove a friendship."""
    await FriendService(db).remove(user.id, id)
    return success_response(MessageResponse(message="Friend removed"))


@router.post("/block/{id}", response_model=EnvelopeSchema[FriendshipRead], summary="Block friend")
async def block_friend(
    id: UUID,
    _rate_limit: None = Depends(user_route_rate_limit),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Block a friendship."""
    return success_response(await FriendService(db).block(user.id, id))


@router.get("/list", response_model=EnvelopeSchema[list[FriendshipRead]], summary="List friends")
async def list_friends(
    _rate_limit: None = Depends(user_route_rate_limit),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """List accepted friends."""
    return success_response(await FriendService(db).list(user.id))


@router.get("/requests", response_model=EnvelopeSchema[list[FriendshipRead]], summary="List friend requests")
async def friend_requests(
    _rate_limit: None = Depends(user_route_rate_limit),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """List incoming friend requests."""
    return success_response(await FriendService(db).requests(user.id))
