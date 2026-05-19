# backend/app/repositories/chat_repository.py
from uuid import UUID

from sqlalchemy import select

from app.db.models.chat import Chat
from app.repositories.base import BaseRepository
from app.utils.constants import ChatType


class ChatRepository(BaseRepository[Chat]):
    """Database operations for chats."""

    model = Chat

    async def create(self, room_id: UUID, sender_id: UUID, message: str, chat_type: ChatType) -> Chat:
        """Persist a chat message."""
        chat = Chat(room_id=room_id, sender_id=sender_id, message=message, type=chat_type)
        return await self.add(chat)

    async def list_by_room(self, room_id: UUID, limit: int = 500) -> list[Chat]:
        """Return chat history for replay export."""
        result = await self.session.execute(select(Chat).where(Chat.room_id == room_id).order_by(Chat.created_at.asc()).limit(limit))
        return list(result.scalars().all())
