# backend/app/main.py
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request, WebSocket
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.api.routes import admin, auth, friends, frontend, matches, rooms, users
from app.core.config import get_settings
from app.core.events import get_app_state, shutdown, startup
from app.middleware.auth import OptionalAuthMiddleware
from app.middleware.cors import setup_cors
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.utils.exceptions import AppError
from app.utils.logging import configure_logging
from app.utils.responses import error_response, success_response
from app.websocket.room_events import websocket_endpoint

settings = get_settings()
logger = logging.getLogger(__name__)

configure_logging(settings.LOG_LEVEL)


def _find_grouped_app_error(exc: BaseException) -> AppError | None:
    """Extract expected app errors wrapped by Starlette/anyio ExceptionGroup."""
    if isinstance(exc, AppError):
        return exc
    if isinstance(exc, BaseExceptionGroup):
        for child in exc.exceptions:
            found = _find_grouped_app_error(child)
            if found is not None:
                return found
    return None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Run async startup/shutdown hooks for Redis and pub/sub."""
    await startup(app)
    try:
        yield
    finally:
        await shutdown(app)


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(OptionalAuthMiddleware)
app.add_middleware(RateLimitMiddleware, settings=settings)

app.include_router(auth.router, prefix=f"{settings.API_PREFIX}/auth", tags=["auth"])
app.include_router(rooms.router, prefix=f"{settings.API_PREFIX}/rooms", tags=["rooms"])
app.include_router(users.router, prefix=f"{settings.API_PREFIX}/users", tags=["users"])
app.include_router(friends.router, prefix=f"{settings.API_PREFIX}/friends", tags=["friends"])
app.include_router(matches.router, prefix=f"{settings.API_PREFIX}/matches", tags=["matches"])
app.include_router(admin.router, prefix=f"{settings.API_PREFIX}/admin", tags=["admin"])
app.include_router(frontend.router, prefix=settings.API_PREFIX, tags=["frontend"])


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> ORJSONResponse:
    """Return expected application errors in envelope form."""
    return ORJSONResponse(
        status_code=exc.status_code,
        content=error_response(exc.code, exc.message, {"request_id": getattr(request.state, "request_id", None)}),
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> ORJSONResponse:
    """Return validation errors without leaking stack traces."""
    return ORJSONResponse(
        status_code=422,
        content=error_response(
            "validation_error",
            "Request validation failed",
            {"details": exc.errors(), "request_id": getattr(request.state, "request_id", None)},
        ),
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception) -> ORJSONResponse:
    """Return unexpected failures as JSON so clients do not see opaque fetch errors."""
    request_id = getattr(request.state, "request_id", None)
    grouped_app_error = _find_grouped_app_error(exc)
    if grouped_app_error is not None:
        return ORJSONResponse(
            status_code=grouped_app_error.status_code,
            content=error_response(grouped_app_error.code, grouped_app_error.message, {"request_id": request_id}),
        )
    logger.exception(
        "unhandled_request_error",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "exception_type": type(exc).__name__,
            "exception_group_size": len(exc.exceptions) if isinstance(exc, BaseExceptionGroup) else None,
        },
    )
    return ORJSONResponse(
        status_code=500,
        content=error_response(
            "internal_server_error",
            "Internal server error",
            {"request_id": request_id},
        ),
    )


@app.get("/health", summary="Health check")
async def health() -> dict[str, object]:
    """Return API liveness information."""
    return success_response({"status": "ok", "env": settings.APP_ENV, **get_app_state(fastapi_app)})


@app.get("/metrics", summary="Prometheus metrics")
async def metrics() -> Response:
    """Expose Prometheus metrics for scraping."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.websocket("/ws/{room_id}")
async def websocket_route(websocket: WebSocket, room_id: str) -> None:
    """Authenticate and delegate room WebSocket traffic."""
    await websocket_endpoint(websocket, room_id)


fastapi_app = app
app = setup_cors(fastapi_app, settings)
