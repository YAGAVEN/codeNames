# backend/README.md
# Codenames India Backend

Async FastAPI backend for Codenames India with PostgreSQL/Supabase, Alembic migrations, in-memory realtime state, and single-process WebSocket gameplay.

## Quick Start

1. Copy `.env.example` to `.env` and fill Supabase, JWT, and database values.
   - Ensure `ALLOWED_ORIGINS` includes your frontend origin (for example `https://code-names-theta.vercel.app`).
   - On Render, set `ALLOWED_ORIGINS` and `FRONTEND_URL` in the service environment; the local `.env` file is not applied unless you explicitly configure it.
2. Install dependencies with `pip install -r requirements.txt`.
3. Apply migrations with `alembic upgrade head`.
4. Run `gunicorn app.main:app -k uvicorn.workers.UvicornWorker --workers 1 --bind 0.0.0.0:8000`.
5. Open `http://localhost:8000/docs`.

## Supabase Database Setup

If you want the tables inside your Supabase project, set `DATABASE_URL` to your Supabase Postgres connection string (use the `postgres` role and include `?ssl=require` for asyncpg), then run:

```bash
alembic upgrade head
```

The migration creates the public tables, RLS policies, and the `auth.users` trigger that keeps `public.users` in sync.
The backend expects the asyncpg driver; plain `postgresql://` URLs are automatically upgraded to `postgresql+asyncpg://` at runtime.

## Production (Render)

Use the repository-level `render.yaml`. The backend intentionally runs with one Gunicorn worker because realtime game state and WebSocket connections are in process memory.

## Architecture Notes

- REST responses use `{success, data, error, meta}` envelopes.
- Game state, refresh tokens, word-pack cache, timers, and rate-limit windows are held in process memory.
- WebSocket broadcasts are local to the single backend worker.
- Supabase Auth owns email/password and Google OAuth; the local `users` table stores game profile data.
- TODO: Configure production email delivery and Supabase webhook/trigger for `auth.users` profile sync.

## Tests

Run from this directory:

```bash
pytest app/tests
```
