#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"
API_ORIGIN="${API_ORIGIN:-http://localhost:${BACKEND_PORT}}"
WS_ORIGIN="${WS_ORIGIN:-ws://localhost:${BACKEND_PORT}}"

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

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required to start the backend." >&2
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required to start the frontend." >&2
  exit 1
fi

ensure_env_files

echo "Starting backend on ${API_ORIGIN}"
(
  cd "$BACKEND_DIR"
  PORT="$BACKEND_PORT" python3 -m uvicorn app.main:app --host 0.0.0.0 --port "$BACKEND_PORT"
) &
BACKEND_PID=$!

cleanup() {
  echo
  echo "Stopping backend."
  kill "$BACKEND_PID" >/dev/null 2>&1 || true
}

trap cleanup EXIT INT TERM

if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
  echo "Installing frontend dependencies..."
  (cd "$FRONTEND_DIR" && npm install)
fi

echo "Starting frontend on http://localhost:${FRONTEND_PORT}"
(
  cd "$FRONTEND_DIR"
  VITE_API_URL="${VITE_API_URL:-${API_ORIGIN}/api}" \
    VITE_WS_URL="${VITE_WS_URL:-${WS_ORIGIN}/ws}" \
    npm run dev -- --host 0.0.0.0 --port "$FRONTEND_PORT"
)
