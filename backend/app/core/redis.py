# backend/app/core/redis.py
import asyncio
import logging
from typing import Any
from urllib.parse import urlparse

from fastapi import FastAPI
from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import Settings

logger = logging.getLogger(__name__)


def redis_connection_info(url: str) -> dict[str, Any]:
    """Return safe Redis connection metadata for logs and diagnostics."""
    parsed = urlparse(url)
    path_db = parsed.path.lstrip("/")
    try:
        db = int(path_db) if path_db else 0
    except ValueError:
        db = None
    return {
        "scheme": parsed.scheme or "redis",
        "host": parsed.hostname or "localhost",
        "port": parsed.port or 6379,
        "db": db,
        "username_configured": bool(parsed.username),
        "password_configured": bool(parsed.password),
    }


def create_redis_client(settings: Settings) -> Redis:
    """Create an async Redis client with short timeouts and reconnect-friendly settings."""
    return Redis.from_url(
        settings.REDIS_URL,
        decode_responses=False,
        socket_connect_timeout=settings.REDIS_CONNECT_TIMEOUT_SECONDS,
        socket_timeout=settings.REDIS_SOCKET_TIMEOUT_SECONDS,
        health_check_interval=settings.REDIS_HEALTH_CHECK_INTERVAL_SECONDS,
        retry_on_timeout=True,
    )


async def ping_redis(redis: Redis) -> bool:
    """Return whether Redis responds to PING."""
    try:
        await redis.ping()
    except RedisError:
        return False
    return True


async def disconnect_redis_pool(redis: Redis) -> None:
    """Drop stale Redis connections without raising into request handling."""
    pool = getattr(redis, "connection_pool", None)
    if pool is None:
        return
    try:
        await pool.disconnect(inuse_connections=True)
    except Exception:
        logger.debug("redis_pool_disconnect_failed", exc_info=True)


async def check_redis_health(app: FastAPI, settings: Settings, *, log_success: bool = False) -> bool:
    """Ping Redis, update app health state, and log availability transitions."""
    redis: Redis | None = getattr(app.state, "redis", None)
    if redis is None:
        redis = create_redis_client(settings)
        app.state.redis = redis

    info = redis_connection_info(settings.REDIS_URL)
    was_available = bool(getattr(app.state, "redis_available", False))
    failure_logged = bool(getattr(app.state, "redis_failure_logged", False))
    try:
        await redis.ping()
    except RedisError:
        app.state.redis_available = False
        log = logger.warning if was_available or not failure_logged else logger.debug
        log(
            "redis_unavailable",
            extra={**info, "env": settings.APP_ENV, "operation": "ping"},
            exc_info=True,
        )
        app.state.redis_failure_logged = True
        await disconnect_redis_pool(redis)
        return False

    app.state.redis_available = True
    app.state.redis_failure_logged = False
    if log_success or not was_available:
        logger.info("redis_available", extra={**info, "env": settings.APP_ENV})
    return True


async def verify_redis_configuration(settings: Settings) -> None:
    """Log safe Redis configuration details and production misconfiguration warnings."""
    info = redis_connection_info(settings.REDIS_URL)
    logger.info("redis_configuration_loaded", extra={**info, "env": settings.APP_ENV})
    if settings.is_production and info["host"] in {"localhost", "127.0.0.1", "::1"}:
        logger.error(
            "redis_url_points_to_localhost_in_production",
            extra={
                **info,
                "env": settings.APP_ENV,
                "hint": "Set REDIS_URL to the managed Redis host, e.g. redis://:<password>@<host>:<port>/0.",
            },
        )


async def startup_redis_health_check(app: FastAPI, settings: Settings) -> bool:
    """Attempt a bounded startup Redis health check without preventing API startup."""
    await verify_redis_configuration(settings)
    for attempt in range(1, settings.REDIS_STARTUP_RETRIES + 1):
        healthy = await check_redis_health(app, settings, log_success=True)
        if healthy:
            return True
        if attempt < settings.REDIS_STARTUP_RETRIES:
            await asyncio.sleep(settings.REDIS_STARTUP_RETRY_DELAY_SECONDS)
    logger.warning(
        "redis_startup_check_failed_open",
        extra={**redis_connection_info(settings.REDIS_URL), "attempts": settings.REDIS_STARTUP_RETRIES},
    )
    return False


async def redis_health_monitor(app: FastAPI, settings: Settings) -> None:
    """Keep checking Redis so redis-py can reconnect and app state reflects availability."""
    while True:
        await asyncio.sleep(settings.REDIS_RECONNECT_INTERVAL_SECONDS)
        await check_redis_health(app, settings)


async def close_redis(redis: Redis | None) -> None:
    """Close Redis connections during shutdown."""
    if redis is None:
        return
    try:
        await redis.aclose()
    except RedisError:
        logger.warning("redis_close_failed", exc_info=True)
