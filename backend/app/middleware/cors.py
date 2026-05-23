# backend/app/middleware/cors.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import Settings


def setup_cors(app: FastAPI, settings: Settings) -> None:
    """Apply environment-configured CORS policy."""
    allowed = [origin.rstrip("/") for origin in settings.ALLOWED_ORIGINS]
    frontend_origin = settings.FRONTEND_URL.rstrip("/")
    if frontend_origin and frontend_origin not in allowed:
        allowed.append(frontend_origin)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    )
