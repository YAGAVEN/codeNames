# backend/app/middleware/cors.py
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import Settings


class ForwardingCORSMiddleware(CORSMiddleware):
    """CORS wrapper that keeps FastAPI attributes available to tests and tooling."""

    def __getattr__(self, name: str) -> Any:
        return getattr(self.app, name)


def setup_cors(app: FastAPI, settings: Settings) -> ForwardingCORSMiddleware:
    """Apply environment-configured CORS policy."""
    allowed = []
    for origin in settings.ALLOWED_ORIGINS:
        normalized = origin.strip().rstrip("/")
        if normalized and normalized not in allowed:
            allowed.append(normalized)
    frontend_origin = settings.FRONTEND_URL.strip().rstrip("/")
    if frontend_origin and frontend_origin not in allowed:
        allowed.append(frontend_origin)
    return ForwardingCORSMiddleware(
        app,
        allow_origins=allowed,
        allow_origin_regex=settings.ALLOWED_ORIGIN_REGEX or None,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
