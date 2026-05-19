# backend/app/utils/responses.py
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

DataT = TypeVar("DataT")


class ErrorBody(BaseModel):
    """Machine-readable error payload."""

    model_config = ConfigDict(strict=True)

    code: str
    message: str


class MetaBody(BaseModel):
    """Optional response metadata for pagination and diagnostics."""

    model_config = ConfigDict(strict=True)

    page: int | None = None
    per_page: int | None = None
    total: int | None = None
    request_id: str | None = None


class Envelope(BaseModel, Generic[DataT]):
    """Consistent API response envelope."""

    model_config = ConfigDict(strict=True, arbitrary_types_allowed=True)

    success: bool
    data: DataT | None = None
    error: ErrorBody | None = None
    meta: MetaBody | dict[str, Any] | None = Field(default_factory=dict)


def success_response(data: Any = None, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return a successful API envelope."""
    return {"success": True, "data": data, "error": None, "meta": meta or {}}


def error_response(code: str, message: str, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return an error API envelope."""
    return {
        "success": False,
        "data": None,
        "error": {"code": code, "message": message},
        "meta": meta or {},
    }
