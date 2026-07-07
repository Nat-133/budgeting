#!/bin/bash

# Start Budget Dashboard - FastAPI + React
# Exits and tears down both servers on any error or interrupt.

set -euo pipefail

echo "Starting Budget Dashboard..."

# Resolve repo root so the script works from any cwd
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

BACKEND_PID=""
FRONTEND_PID=""

# Tear down anything we started. Runs on normal exit, error, or Ctrl+C.
cleanup() {
    # Disable the trap so cleanup can't re-enter itself.
    trap - EXIT INT TERM
    echo ""
    echo "Stopping servers..."
    [ -n "$BACKEND_PID" ] && kill "$BACKEND_PID" 2>/dev/null || true
    [ -n "$FRONTEND_PID" ] && kill "$FRONTEND_PID" 2>/dev/null || true
    # Give them a moment, then force-kill any survivors.
    sleep 1
    [ -n "$BACKEND_PID" ] && kill -9 "$BACKEND_PID" 2>/dev/null || true
    [ -n "$FRONTEND_PID" ] && kill -9 "$FRONTEND_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# Fail early if a required port is already taken.
port_in_use() {
    ss -ltn 2>/dev/null | grep -q "[:.]$1[[:space:]]"
}
for port in 8000 5173; do
    if port_in_use "$port"; then
        echo "ERROR: port $port is already in use." >&2
        echo "Stop whatever is listening on it and try again (e.g. 'ss -ltnp | grep :$port')." >&2
        exit 1
    fi
done

# Activate the project virtualenv (lives at the repo root, not in backend/)
if [ ! -f "$ROOT/.venv/bin/activate" ]; then
    echo "ERROR: virtualenv not found at $ROOT/.venv" >&2
    echo "Create it with: python -m venv .venv && .venv/bin/pip install -r backend/requirements.txt" >&2
    exit 1
fi
source "$ROOT/.venv/bin/activate"

# Start backend in background
echo "Starting FastAPI backend on port 8000..."
cd "$ROOT/backend"
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd "$ROOT"

# Wait for the backend to become healthy; bail out (triggering cleanup) if it never does.
echo "Waiting for backend to become healthy..."
for i in $(seq 1 30); do
    if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
        echo "ERROR: backend process exited during startup." >&2
        exit 1
    fi
    if curl -sf -m 2 http://localhost:8000/api/health >/dev/null 2>&1; then
        echo "Backend is up."
        break
    fi
    if [ "$i" -eq 30 ]; then
        echo "ERROR: backend did not become healthy within 30s." >&2
        exit 1
    fi
    sleep 1
done

# Start frontend in background
echo "Starting React frontend on port 5173..."
cd "$ROOT/frontend"
npm run dev &
FRONTEND_PID=$!
cd "$ROOT"

echo ""
echo "====================================="
echo "Budget Dashboard is now running!"
echo "====================================="
echo ""
echo "Frontend: http://localhost:5173"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# If either server dies, wake up and let cleanup tear down the other.
wait -n
echo "A server process exited; shutting down the other." >&2
exit 1
