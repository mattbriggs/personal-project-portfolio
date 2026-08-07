#!/usr/bin/env bash
# Smoke test: start the sidecar on a loopback port with a token and verify
# health, auth enforcement, and a minimal create/read workflow over HTTP.
#
# Usage: BACKEND_PY=/path/to/venv/bin/python bash tests/smoke/sidecar_smoke.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PY="${BACKEND_PY:-python3}"
PORT="${PORT:-8765}"
TOKEN="smoke-$(date +%s)"
HOME_DIR="$(mktemp -d)"

export PORTFOLIO_SIDECAR_TOKEN="$TOKEN"
export HOME="$HOME_DIR"

PYTHONPATH="$REPO_ROOT/backend/src" "$PY" -m portfolio_manager.cli.sidecar --port "$PORT" &
SIDE=$!
trap 'kill $SIDE 2>/dev/null || true; rm -rf "$HOME_DIR"' EXIT

# Wait for readiness.
for _ in $(seq 1 40); do
  if curl -sf "127.0.0.1:$PORT/health" >/dev/null; then break; fi
  sleep 0.25
done

echo "health:        $(curl -s -o /dev/null -w '%{http_code}' 127.0.0.1:$PORT/health)"
echo "no-token 401:  $(curl -s -o /dev/null -w '%{http_code}' 127.0.0.1:$PORT/api/v1/projects)"
echo "create 201:    $(curl -s -o /dev/null -w '%{http_code}' -H "X-API-Key: $TOKEN" \
  -H 'Content-Type: application/json' -d '{"name":"Smoke"}' 127.0.0.1:$PORT/api/v1/projects)"
echo "list w/ token: $(curl -s -H "X-API-Key: $TOKEN" 127.0.0.1:$PORT/api/v1/projects)"
