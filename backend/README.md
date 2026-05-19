# backend/README.md
# Codenames India Backend

Async FastAPI backend for Codenames India with PostgreSQL/Supabase, Redis-backed realtime state, Celery workers, Alembic migrations, and Docker/Nginx deployment assets.

## Quick Start

1. Copy `.env.example` to `.env` and fill Supabase, JWT, database, and Redis values.
2. Run `docker compose up --build`.
3. Apply migrations with `docker compose run --rm api alembic upgrade head`.
4. Open `http://localhost:8000/docs`.

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
