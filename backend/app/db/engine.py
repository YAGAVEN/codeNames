from __future__ import annotations

from dataclasses import dataclass
import ssl
from typing import Mapping

from sqlalchemy.engine import make_url

@dataclass(frozen=True)
class EngineConfig:
    """Resolved engine URL and asyncpg connection arguments."""

    database_url: str
    connect_args: dict[str, object]


def _ssl_required_from_query(query: Mapping[str, str | None]) -> bool:
    sslmode = (query.get("sslmode") or "").lower()
    if sslmode:
        return sslmode not in {"disable", "allow", "prefer"}

    ssl_value = (query.get("ssl") or "").lower()
    if ssl_value:
        return ssl_value in {"1", "true", "require", "verify-ca", "verify-full"}

    return False


def _is_supabase_host(host: str) -> bool:
    return (
        host.endswith(".supabase.co")
        or host.endswith(".pooler.supabase.com")
    )


def _is_supabase_pooler_host(host: str) -> bool:
    return host.endswith(".pooler.supabase.com")


def _is_supabase_transaction_pooler(host: str, port: int | None) -> bool:
    return port == 6543 and (
        _is_supabase_pooler_host(host)
        or host.endswith(".supabase.co")
    )


def build_engine_config(database_url: str) -> EngineConfig:
    """
    Return a sanitized URL and asyncpg connection arguments.
    Handles:
    - SSL for Supabase
    - Supabase transaction-pooler compatibility
    """

    if database_url.startswith("sqlite"):
        return EngineConfig(
            database_url=database_url,
            connect_args={},
        )

    url = make_url(database_url)
    query = dict(url.query)

    ssl_required = _ssl_required_from_query(query)

    query.pop("sslmode", None)
    query.pop("ssl", None)

    host = url.host or ""

    connect_args: dict[str, object] = {}

    if _is_supabase_host(host):
        ssl_required = True

    if _is_supabase_transaction_pooler(host, url.port):
        # Supabase's transaction pooler is incompatible with cached prepared
        # statements. These are two separate caches:
        # - asyncpg's driver-level automatic statement cache
        # - SQLAlchemy's asyncpg prepared-statement cache
        connect_args["statement_cache_size"] = 0
        query["prepared_statement_cache_size"] = "0"

    if ssl_required:
        ssl_context = ssl.create_default_context()

        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        connect_args["ssl"] = ssl_context

    sanitized_url = url.set(query=query)

    return EngineConfig(
        database_url=sanitized_url.render_as_string(
            hide_password=False
        ),
        connect_args=connect_args,
    )
