# backend/app/schemas/common.py
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from app.utils.responses import ErrorBody, MetaBody

DataT = TypeVar("DataT")


class StrictSchema(BaseModel):
    """Base schema using strict validation and forbidding unknown fields."""

    model_config = ConfigDict(strict=True, extra="forbid", from_attributes=True)


class EnvelopeSchema(BaseModel, Generic[DataT]):
    """OpenAPI schema for the standard API envelope."""

    model_config = ConfigDict(strict=True, from_attributes=True)

    success: bool
    data: DataT | None = None
    error: ErrorBody | None = None
    meta: MetaBody | dict = Field(default_factory=dict)


class PaginationParams(StrictSchema):
    """Common pagination parameters."""

    page: int = 1
    per_page: int = 20


class MessageResponse(StrictSchema):
    """Simple message response payload."""

    message: str
