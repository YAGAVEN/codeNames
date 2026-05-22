#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"
API_ORIGIN="${API_ORIGIN:-http://localhost:${BACKEND_PORT}}"
WS_ORIGIN="${WS_ORIGIN:-ws://localhost:${BACKEND_PORT}}"
KEEP_BACKEND_RUNNING="${KEEP_BACKEND_RUNNING:-0}"
export BACKEND_PORT FRONTEND_PORT API_ORIGIN WS_ORIGIN

if docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD=(docker-compose)
else
  echo "Docker Compose is required to start the backend services." >&2
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required to start the frontend." >&2
  exit 1
fi

compose() {
  (cd "$BACKEND_DIR" && "${COMPOSE_CMD[@]}" "$@")
}

ensure_env_files() {
  if [ ! -f "$BACKEND_DIR/.env" ]; then
    cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
    echo "Created backend/.env from backend/.env.example"
  fi

  if [ ! -f "$FRONTEND_DIR/.env" ] && [ -f "$FRONTEND_DIR/.env.example" ]; then
    cp "$FRONTEND_DIR/.env.example" "$FRONTEND_DIR/.env"
    echo "Created frontend/.env from frontend/.env.example"
  fi
}

cleanup() {
  if [ "$KEEP_BACKEND_RUNNING" != "1" ]; then
    echo
    echo "Stopping backend app containers. Database and Redis containers are left running."
    compose stop api worker beat >/dev/null 2>&1 || true
  fi
}

trap cleanup EXIT INT TERM

ensure_env_files

echo "Building backend containers..."
compose build api worker beat

echo "Starting backend dependencies..."
compose up -d db redis

echo "Applying database migrations..."
compose run --rm api alembic upgrade head

echo "Starting backend API and workers..."
BACKEND_PORT="$BACKEND_PORT" compose up -d api worker beat

echo "Backend:  ${API_ORIGIN}"
echo "API docs: ${API_ORIGIN}/docs"

if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
  echo "Installing frontend dependencies..."
  (cd "$FRONTEND_DIR" && npm install)
fi

echo "Starting frontend on http://localhost:${FRONTEND_PORT}"
echo "Press Ctrl+C to stop the frontend and backend app containers."

(
  cd "$FRONTEND_DIR"
  VITE_API_URL="${VITE_API_URL:-${API_ORIGIN}/api}" \
    VITE_WS_URL="${VITE_WS_URL:-${WS_ORIGIN}/ws}" \
    npm run dev -- --host 0.0.0.0 --port "$FRONTEND_PORT"
)
