# backend/alembic/versions/202605190001_initial_schema.py
"""initial codenames india schema

Revision ID: 202605190001
Revises:
Create Date: 2026-05-19 00:01:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "202605190001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def uuid_pk() -> sa.Column:
    """Create a Postgres UUID primary key column backed by gen_random_uuid."""
    return sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"))


def timestamps() -> list[sa.Column]:
    """Return created_at/updated_at timestamp columns."""
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    ]


def enable_rls(table: str) -> None:
    """Enable RLS for a user-facing table."""
    op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")


def upgrade() -> None:
    """Create tables, indexes, triggers, and Supabase RLS policies."""
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute("CREATE SCHEMA IF NOT EXISTS auth")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_proc p
                JOIN pg_namespace n ON n.oid = p.pronamespace
                WHERE n.nspname = 'auth' AND p.proname = 'uid'
            ) THEN
                EXECUTE $fn$
                CREATE FUNCTION auth.uid()
                RETURNS uuid
                LANGUAGE sql
                STABLE
                AS $body$ SELECT NULL::uuid $body$;
                $fn$;
            END IF;
        END $$;
        """
    )

    op.create_table(
        "users",
        uuid_pk(),
        sa.Column("username", sa.String(length=24), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("avatar_url", sa.String(length=2048)),
        sa.Column("xp", sa.Integer(), server_default="0", nullable=False),
        sa.Column("level", sa.Integer(), server_default="1", nullable=False),
        sa.Column("win_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("lose_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("streak", sa.Integer(), server_default="0", nullable=False),
        sa.Column("online_status", sa.String(length=16), server_default="offline", nullable=False),
        sa.Column("last_seen", sa.DateTime(timezone=True)),
        sa.Column("role", sa.String(length=16), server_default="player", nullable=False),
        *timestamps(),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_username", "users", ["username"])

    op.create_table(
        "rooms",
        uuid_pk(),
        sa.Column("room_code", sa.String(length=8), nullable=False),
        sa.Column("host_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(length=24), server_default="waiting", nullable=False),
        sa.Column("max_players", sa.Integer(), server_default="10", nullable=False),
        sa.Column("settings", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("game_state", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        *timestamps(),
        sa.UniqueConstraint("room_code"),
    )
    op.create_index("ix_rooms_host_id", "rooms", ["host_id"])
    op.create_index("ix_rooms_room_code", "rooms", ["room_code"])
    op.create_index("ix_rooms_status", "rooms", ["status"])

    op.create_table(
        "room_players",
        uuid_pk(),
        sa.Column("room_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("team", sa.String(length=16), server_default="spectator", nullable=False),
        sa.Column("role", sa.String(length=16), server_default="operative", nullable=False),
        sa.Column("is_ready", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("room_id", "user_id", name="uq_room_players_room_user"),
    )
    op.create_index("ix_room_players_room_id", "room_players", ["room_id"])
    op.create_index("ix_room_players_user_id", "room_players", ["user_id"])

    op.create_table(
        "games",
        uuid_pk(),
        sa.Column("room_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False),
        sa.Column("winner_team", sa.String(length=16)),
        sa.Column("duration_seconds", sa.Integer()),
        sa.Column("red_score", sa.Integer(), server_default="0", nullable=False),
        sa.Column("blue_score", sa.Integer(), server_default="0", nullable=False),
        sa.Column("replay_data", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("word_pack", sa.String(length=64), server_default="default", nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("ended_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_games_room_id", "games", ["room_id"])

    op.create_table(
        "game_moves",
        uuid_pk(),
        sa.Column("game_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("games.id", ondelete="CASCADE"), nullable=False),
        sa.Column("player_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("move_type", sa.String(length=16), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_game_moves_game_id", "game_moves", ["game_id"])
    op.create_index("ix_game_moves_player_id", "game_moves", ["player_id"])
    op.create_index("ix_game_moves_created_at", "game_moves", ["created_at"])

    op.create_table(
        "chats",
        uuid_pk(),
        sa.Column("room_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sender_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("message", sa.String(length=500), nullable=False),
        sa.Column("type", sa.String(length=16), server_default="room", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_chats_room_id", "chats", ["room_id"])
    op.create_index("ix_chats_sender_id", "chats", ["sender_id"])
    op.create_index("ix_chats_created_at", "chats", ["created_at"])

    op.create_table(
        "friendships",
        uuid_pk(),
        sa.Column("requester_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("addressee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(length=16), server_default="pending", nullable=False),
        *timestamps(),
        sa.UniqueConstraint("requester_id", "addressee_id", name="uq_friendships_requester_addressee"),
    )
    op.create_index("ix_friendships_requester_id", "friendships", ["requester_id"])
    op.create_index("ix_friendships_addressee_id", "friendships", ["addressee_id"])
    op.create_index("ix_friendships_status", "friendships", ["status"])

    op.create_table(
        "notifications",
        uuid_pk(),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.String(length=64), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("is_read", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.create_index("ix_notifications_type", "notifications", ["type"])
    op.create_index("ix_notifications_is_read", "notifications", ["is_read"])

    op.create_table(
        "achievements",
        uuid_pk(),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("badge_key", sa.String(length=80), nullable=False),
        sa.Column("unlocked_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("user_id", "badge_key", name="uq_achievements_user_badge"),
    )
    op.create_index("ix_achievements_user_id", "achievements", ["user_id"])
    op.create_index("ix_achievements_badge_key", "achievements", ["badge_key"])

    op.create_table(
        "match_history",
        uuid_pk(),
        sa.Column("game_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("games.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("team", sa.String(length=16), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("is_winner", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("xp_earned", sa.Integer(), server_default="0", nullable=False),
        sa.Column("clues_given", sa.Integer(), server_default="0", nullable=False),
        sa.Column("correct_guesses", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_match_history_game_id", "match_history", ["game_id"])
    op.create_index("ix_match_history_user_id", "match_history", ["user_id"])
    op.create_index("ix_match_history_created_at", "match_history", ["created_at"])

    op.create_table(
        "reports",
        uuid_pk(),
        sa.Column("reporter_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reported_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reason", sa.String(length=1000), nullable=False),
        sa.Column("status", sa.String(length=16), server_default="open", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_reports_reporter_id", "reports", ["reporter_id"])
    op.create_index("ix_reports_reported_id", "reports", ["reported_id"])
    op.create_index("ix_reports_status", "reports", ["status"])
    op.create_index("ix_reports_created_at", "reports", ["created_at"])

    op.create_table(
        "tournaments",
        uuid_pk(),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=16), server_default="draft", nullable=False),
        sa.Column("settings", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True)),
        sa.Column("ends_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_tournaments_name", "tournaments", ["name"])
    op.create_index("ix_tournaments_status", "tournaments", ["status"])

    op.execute(
        """
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS trigger AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    for table in ("users", "rooms", "friendships"):
        op.execute(f"CREATE TRIGGER trg_{table}_updated_at BEFORE UPDATE ON {table} FOR EACH ROW EXECUTE FUNCTION set_updated_at()")

    for table in (
        "users",
        "rooms",
        "room_players",
        "games",
        "game_moves",
        "chats",
        "friendships",
        "notifications",
        "achievements",
        "match_history",
        "reports",
        "tournaments",
    ):
        enable_rls(table)

    # Supabase Auth exposes auth.uid(); service-role API calls bypass RLS.
    op.execute("CREATE POLICY users_self_select ON users FOR SELECT USING (id = auth.uid() OR role IN ('moderator','admin'))")
    op.execute("CREATE POLICY users_self_update ON users FOR UPDATE USING (id = auth.uid()) WITH CHECK (id = auth.uid())")
    op.execute("CREATE POLICY rooms_public_select ON rooms FOR SELECT USING (true)")
    op.execute("CREATE POLICY rooms_host_write ON rooms FOR ALL USING (host_id = auth.uid()) WITH CHECK (host_id = auth.uid())")
    op.execute("CREATE POLICY room_players_member_select ON room_players FOR SELECT USING (user_id = auth.uid())")
    op.execute("CREATE POLICY room_players_self_insert ON room_players FOR INSERT WITH CHECK (user_id = auth.uid())")
    op.execute("CREATE POLICY chats_room_members ON chats FOR SELECT USING (EXISTS (SELECT 1 FROM room_players rp WHERE rp.room_id = chats.room_id AND rp.user_id = auth.uid()))")
    op.execute("CREATE POLICY chats_self_insert ON chats FOR INSERT WITH CHECK (sender_id = auth.uid())")
    op.execute("CREATE POLICY friendships_self ON friendships FOR ALL USING (requester_id = auth.uid() OR addressee_id = auth.uid())")
    op.execute("CREATE POLICY notifications_self ON notifications FOR SELECT USING (user_id = auth.uid())")
    op.execute("CREATE POLICY achievements_self ON achievements FOR SELECT USING (user_id = auth.uid())")
    op.execute("CREATE POLICY history_self ON match_history FOR SELECT USING (user_id = auth.uid())")
    op.execute("CREATE POLICY reports_self_insert ON reports FOR INSERT WITH CHECK (reporter_id = auth.uid())")
    op.execute("CREATE POLICY games_member_select ON games FOR SELECT USING (EXISTS (SELECT 1 FROM room_players rp WHERE rp.room_id = games.room_id AND rp.user_id = auth.uid()))")
    op.execute("CREATE POLICY game_moves_member_select ON game_moves FOR SELECT USING (EXISTS (SELECT 1 FROM games g JOIN room_players rp ON rp.room_id = g.room_id WHERE g.id = game_moves.game_id AND rp.user_id = auth.uid()))")
    op.execute("CREATE POLICY tournaments_public_select ON tournaments FOR SELECT USING (true)")
    op.execute(
        """
        CREATE OR REPLACE FUNCTION public.handle_auth_user_created()
        RETURNS trigger AS $$
        BEGIN
            INSERT INTO public.users (id, email, username)
            VALUES (
                NEW.id,
                NEW.email,
                left(COALESCE(NULLIF(NEW.raw_user_meta_data->>'username', ''), split_part(NEW.email, '@', 1)) || '_' || substr(NEW.id::text, 1, 6), 24)
            )
            ON CONFLICT (id) DO NOTHING;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF to_regclass('auth.users') IS NOT NULL THEN
                EXECUTE $trg$
                CREATE TRIGGER on_auth_user_created
                AFTER INSERT ON auth.users
                FOR EACH ROW EXECUTE FUNCTION public.handle_auth_user_created();
                $trg$;
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    """Drop all schema objects created by this revision."""
    for table in ("users", "rooms", "friendships"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_updated_at ON {table}")
    op.execute("DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users")
    op.execute("DROP FUNCTION IF EXISTS public.handle_auth_user_created")
    op.execute("DROP FUNCTION IF EXISTS set_updated_at")
    for table in (
        "tournaments",
        "reports",
        "match_history",
        "achievements",
        "notifications",
        "friendships",
        "chats",
        "game_moves",
        "games",
        "room_players",
        "rooms",
        "users",
    ):
        op.drop_table(table)
