#!/usr/bin/env bash
# launch.sh — Find a Tk-capable Python, create venv if needed, run Portfolio Manager
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SCRIPT_DIR/.venv"

# ---------------------------------------------------------------------------
# Find a Python 3.11+ that has _tkinter (Tk support).
# python.org installers under /Library/Frameworks include Tk; Homebrew usually
# does not. We try common locations in preference order.
# ---------------------------------------------------------------------------
find_tk_python() {
    local candidates=(
        # python.org framework installs (most reliable Tk on macOS)
        "/Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13"
        "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3.12"
        "/Library/Frameworks/Python.framework/Versions/3.11/bin/python3.11"
        # pyenv-managed (may or may not have Tk depending on build flags)
        "$(pyenv which python3 2>/dev/null || true)"
        # Homebrew — newer formula sometimes includes Tk
        "/opt/homebrew/opt/python@3.13/bin/python3.13"
        "/opt/homebrew/opt/python@3.12/bin/python3.12"
        "/opt/homebrew/opt/python@3.11/bin/python3.11"
        "/opt/homebrew/bin/python3.13"
        "/opt/homebrew/bin/python3.12"
        "/opt/homebrew/bin/python3.11"
        # System fallback
        "/usr/bin/python3"
        "python3"
    )

    for py in "${candidates[@]}"; do
        [ -z "$py" ] && continue
        if command -v "$py" &>/dev/null || [ -x "$py" ]; then
            # Check Python >= 3.11 and _tkinter available
            if "$py" -c "
import sys, importlib.util
assert sys.version_info >= (3, 11), 'too old'
assert importlib.util.find_spec('_tkinter') is not None, 'no _tkinter'
" 2>/dev/null; then
                echo "$py"
                return 0
            fi
        fi
    done
    return 1
}

# Only search for a new Python if the venv doesn't exist yet.
if [ ! -d "$VENV" ]; then
    echo "Searching for a Tk-capable Python 3.11+..."
    PYTHON=$(find_tk_python) || {
        echo ""
        echo "Error: No Tk-capable Python 3.11+ found."
        echo "Install Python from https://www.python.org/downloads/ (includes Tk on macOS)"
        echo "or install Tk support for your Python and try again."
        exit 1
    }
    echo "Using: $PYTHON"
    echo "Creating virtual environment..."
    "$PYTHON" -m venv "$VENV"
    "$VENV/bin/pip" install -e "$SCRIPT_DIR[dev]" --quiet
fi

exec "$VENV/bin/python" -m portfolio_manager "$@"
