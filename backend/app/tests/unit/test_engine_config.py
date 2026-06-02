from app.db.engine import build_engine_config


def test_supabase_pooler_sslmode_is_converted_to_asyncpg_ssl() -> None:
    config = build_engine_config(
        "postgresql+asyncpg://postgres.project:password@aws-0-region.pooler.supabase.com:6543/postgres"
        "?sslmode=require"
    )

    assert "sslmode" not in config.database_url
    assert "ssl" in config.connect_args


def test_supabase_pooler_requires_ssl_without_query_param() -> None:
    config = build_engine_config(
        "postgresql+asyncpg://postgres.project:password@aws-0-region.pooler.supabase.com:6543/postgres"
    )

    assert "ssl" in config.connect_args


def test_non_supabase_sslmode_disable_is_stripped_without_ssl() -> None:
    config = build_engine_config("postgresql+asyncpg://user:password@example.com:5432/app?sslmode=disable")

    assert "sslmode" not in config.database_url
    assert config.connect_args == {}
