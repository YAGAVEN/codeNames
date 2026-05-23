# backend/README.md
# Codenames India Backend

Async FastAPI backend for Codenames India with PostgreSQL/Supabase, Redis-backed realtime state, Celery workers, Alembic migrations, and Docker/Nginx deployment assets.

## Quick Start

1. Copy `.env.example` to `.env` and fill Supabase, JWT, database, and Redis values.
   - Ensure `ALLOWED_ORIGINS` includes your frontend origin (for example `https://code-names-theta.vercel.app`).
2. Run `docker compose up --build`.
3. Apply migrations with `docker compose run --rm api alembic upgrade head`.
4. Open `http://localhost:8000/docs`.

## Supabase Database Setup

If you want the tables inside your Supabase project, set `DATABASE_URL` to your Supabase Postgres connection string (use the `postgres` role and include `?ssl=require` for asyncpg), then run:

```bash
alembic upgrade head
```

The migration creates the public tables, RLS policies, and the `auth.users` trigger that keeps `public.users` in sync.
The backend expects the asyncpg driver; plain `postgresql://` URLs are automatically upgraded to `postgresql+asyncpg://` at runtime.

## Production (Docker)

1. Copy `.env.example` to `.env` and replace the placeholders with production values.
2. From the repository root, run `docker compose -f backend/docker-compose.yml up --build`.
3. The Nginx container serves the frontend on `http://localhost` and proxies `/api` and `/ws` to the backend.

## Architecture Notes

- REST responses use `{success, data, error, meta}` envelopes.
- Game state is snapshotted to Redis under `game:state:{room_id}` after each move.
- WebSocket broadcasts use Redis pub/sub channels `pub:room:{room_id}` for multi-worker fanout.
- Supabase Auth owns email/password and Google OAuth; the local `users` table stores game profile data.
- TODO: Configure production email delivery and Supabase webhook/trigger for `auth.users` profile sync.

## Tests

Run from this directory:

```bash
pytest app/tests
```
