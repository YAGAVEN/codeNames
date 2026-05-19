# backend/app/repositories/base.py
from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Small async repository base for common CRUD operations."""

    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, entity_id: UUID) -> ModelT | None:
        """Fetch a model by UUID primary key."""
        return await self.session.get(self.model, entity_id)

    async def list(self, limit: int = 50, offset: int = 0) -> list[ModelT]:
        """List models with offset pagination."""
        result = await self.session.execute(select(self.model).limit(limit).offset(offset))
        return list(result.scalars().all())

    async def add(self, entity: ModelT) -> ModelT:
        """Persist a new entity and flush generated values."""
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def delete(self, entity: ModelT) -> None:
        """Delete an entity."""
        await self.session.delete(entity)
        await self.session.flush()

    async def commit(self) -> None:
        """Commit the current unit of work."""
        await self.session.commit()

    async def refresh(self, entity: ModelT) -> ModelT:
        """Refresh an entity after commit."""
        await self.session.refresh(entity)
        return entity
