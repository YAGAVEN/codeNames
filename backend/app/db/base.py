# backend/app/db/base.py
from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, MetaData, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import JSON, CHAR, String, TypeDecorator, TypeEngine

naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

JSONBType: TypeEngine[dict] = JSON().with_variant(JSONB, "postgresql")


class GUID(TypeDecorator[UUID]):
    """Platform-independent UUID type for Postgres and SQLite tests."""

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect: object) -> TypeEngine[UUID]:
        """Use native UUID on Postgres and CHAR(36) elsewhere."""
        if getattr(dialect, "name", "") == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))  # type: ignore[attr-defined]
        return dialect.type_descriptor(CHAR(36))  # type: ignore[attr-defined]

    def process_bind_param(self, value: UUID | str | None, dialect: object) -> UUID | str | None:
        """Coerce UUID bind values for the active dialect."""
        if value is None:
            return None
        if getattr(dialect, "name", "") == "postgresql":
            return value if isinstance(value, UUID) else UUID(str(value))
        return str(value)

    def process_result_value(self, value: UUID | str | None, dialect: object) -> UUID | None:
        """Return UUID objects consistently."""
        if value is None:
            return None
        if isinstance(value, UUID):
            return value
        return UUID(str(value))


UUIDType: TypeEngine[UUID] = GUID()


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""

    metadata = MetaData(naming_convention=naming_convention)


class TimestampMixin:
    """Common created/updated timestamp columns for mutable tables."""

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
