from app.db.engine import build_engine_config
from sqlalchemy.engine import make_url


def test_supabase_transaction_pooler_disables_prepared_statement_caches() -> None:
    config = build_engine_config(
        "postgresql+asyncpg://postgres.project:password@aws-0-region.pooler.supabase.com:6543/postgres"
        "?sslmode=require"
    )
    url = make_url(config.database_url)

    assert "sslmode" not in config.database_url
    assert url.password == "password"
    assert url.query["prepared_statement_cache_size"] == "0"
    assert "ssl" in config.connect_args
    assert callable(config.connect_args["prepared_statement_name_func"])
    assert config.connect_args["statement_cache_size"] == 0
    assert config.use_null_pool is True


def test_supabase_transaction_pooler_requires_ssl_without_query_param() -> None:
    config = build_engine_config(
        "postgresql+asyncpg://postgres.project:password@aws-0-region.pooler.supabase.com:6543/postgres"
    )
    url = make_url(config.database_url)

    assert url.query["prepared_statement_cache_size"] == "0"
    assert "ssl" in config.connect_args
    assert callable(config.connect_args["prepared_statement_name_func"])
    assert config.connect_args["statement_cache_size"] == 0
    assert config.use_null_pool is True


def test_supabase_transaction_pooler_overrides_existing_cache_size() -> None:
    config = build_engine_config(
        "postgresql+asyncpg://postgres.project:password@aws-0-region.pooler.supabase.com:6543/postgres"
        "?prepared_statement_cache_size=100&sslmode=require"
    )
    url = make_url(config.database_url)

    assert url.query["prepared_statement_cache_size"] == "0"
    assert callable(config.connect_args["prepared_statement_name_func"])
    assert config.connect_args["statement_cache_size"] == 0
    assert config.use_null_pool is True


def test_supabase_db_host_transaction_pooler_disables_caches() -> None:
    config = build_engine_config(
        "postgresql+asyncpg://postgres:password@db.project.supabase.co:6543/postgres"
    )
    url = make_url(config.database_url)

    assert url.query["prepared_statement_cache_size"] == "0"
    assert callable(config.connect_args["prepared_statement_name_func"])
    assert config.connect_args["statement_cache_size"] == 0
    assert config.use_null_pool is True


def test_supabase_session_pooler_keeps_prepared_statement_cache() -> None:
    config = build_engine_config(
        "postgresql+asyncpg://postgres.project:password@aws-0-region.pooler.supabase.com:5432/postgres"
    )
    url = make_url(config.database_url)

    assert "ssl" in config.connect_args
    assert "statement_cache_size" not in config.connect_args
    assert "prepared_statement_cache_size" not in url.query
    assert config.use_null_pool is False


def test_supabase_direct_keeps_prepared_statement_cache() -> None:
    config = build_engine_config(
        "postgresql+asyncpg://postgres.project:password@db.project.supabase.co:5432/postgres"
    )
    url = make_url(config.database_url)

    assert "ssl" in config.connect_args
    assert "statement_cache_size" not in config.connect_args
    assert "prepared_statement_cache_size" not in url.query
    assert config.use_null_pool is False


def test_non_supabase_sslmode_disable_is_stripped_without_ssl() -> None:
    config = build_engine_config("postgresql+asyncpg://user:password@example.com:5432/app?sslmode=disable")

    assert "sslmode" not in config.database_url
    assert config.connect_args == {}
    assert config.use_null_pool is False
