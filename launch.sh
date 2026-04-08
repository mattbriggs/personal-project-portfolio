#!/usr/bin/env bash
# launch.sh — Activate venv and run Portfolio Manager
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SCRIPT_DIR/.venv"

if [ ! -d "$VENV" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV"
    "$VENV/bin/pip" install -e "$SCRIPT_DIR[dev]" --quiet
fi

exec "$VENV/bin/python" -m portfolio_manager "$@"
