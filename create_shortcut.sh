#!/usr/bin/env bash
# create_shortcut.sh — Create a macOS .app bundle for Portfolio Manager
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SCRIPT_DIR/.venv"
APP_NAME="Portfolio Manager"
APP_DIR="$HOME/Applications/$APP_NAME.app"

# --- 1. Verify Python 3.11+ ---
PYTHON=$(command -v python3 || true)
if [ -z "$PYTHON" ]; then
    echo "Error: python3 not found. Install Python 3.11+ and try again." >&2
    exit 1
fi

PY_VERSION=$("$PYTHON" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)

if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 11 ]; }; then
    echo "Error: Python 3.11+ required (found $PY_VERSION)." >&2
    exit 1
fi

echo "Using Python $PY_VERSION"

# --- 2. Create venv if missing ---
if [ ! -d "$VENV" ]; then
    echo "Creating virtual environment..."
    "$PYTHON" -m venv "$VENV"
fi

echo "Installing dependencies..."
"$VENV/bin/pip" install -e "$SCRIPT_DIR[dev]" --quiet

# --- 3. Create .app bundle ---
echo "Creating $APP_DIR ..."
mkdir -p "$APP_DIR/Contents/MacOS"
mkdir -p "$APP_DIR/Contents/Resources"

# Executable wrapper
cat > "$APP_DIR/Contents/MacOS/portfolio-manager" <<EOF
#!/usr/bin/env bash
exec "$SCRIPT_DIR/launch.sh" "\$@"
EOF
chmod +x "$APP_DIR/Contents/MacOS/portfolio-manager"

# Info.plist
cat > "$APP_DIR/Contents/Info.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
    "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>Portfolio Manager</string>
    <key>CFBundleIdentifier</key>
    <string>com.mattbriggs.portfolio-manager</string>
    <key>CFBundleExecutable</key>
    <string>portfolio-manager</string>
    <key>CFBundleVersion</key>
    <string>2.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>2.0.0</string>
    <key>LSUIElement</key>
    <false/>
</dict>
</plist>
EOF

echo ""
echo "Done! App bundle created at: $APP_DIR"
echo ""
echo "To add to the Dock: open ~/Applications in Finder and drag"
echo "  '$APP_NAME.app' to the right side of your Dock."
