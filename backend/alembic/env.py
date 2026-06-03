# backend/alembic/env.py
from asyncio import run
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import get_settings
from app.db.base import Base
from app.db.engine import build_engine_config
from app.db import models
from sqlalchemy.engine import make_url

config = context.config
settings = get_settings()
engine_config = build_engine_config(settings.DATABASE_URL)
database_url = engine_config.database_url


u = make_url(database_url)
print("USER =", u.username)
print("HOST =", u.host)
print("PORT =", u.port)
print("PASS_LEN =", len(u.password) if u.password else 0)
print("PASS_FIRST3 =", u.password[:3] if u.password else "NONE")

config.set_main_option("sqlalchemy.url", database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations without a live database connection."""
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Configure Alembic for a connected migration run."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations through SQLAlchemy's async engine."""
    engine_kwargs: dict[str, object] = {"poolclass": pool.NullPool}
    if engine_config.connect_args:
        engine_kwargs["connect_args"] = engine_config.connect_args
    connectable = create_async_engine(database_url, **engine_kwargs)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run(run_migrations_online())
