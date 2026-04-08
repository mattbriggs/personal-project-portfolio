# Development Guide

## Setup

```bash
# Clone and enter the repo
git clone <repo-url> portfolio-manager
cd portfolio-manager

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows

# Install with all dev dependencies
pip install -e .[dev]
```

---

## Running the Application

```bash
python -m portfolio_manager
```

Or use the launcher script which handles venv activation automatically:

```bash
bash launch.sh
```

---

## macOS App Icon

The `create_shortcut.sh` script creates a `.app` bundle for Dock placement. You can give it a custom icon two ways.

### Option 1 — Drag-and-drop (quickest)

1. Find an image you want to use (PNG, ideally 512×512 or 1024×1024).
2. Open it in Preview, then **Edit → Copy** (`⌘C`).
3. Right-click the `.app` → **Get Info** (`⌘I`).
4. Click the small icon in the top-left of the Get Info window (it highlights blue).
5. Paste (`⌘V`).

!!! note
    This change lives on the `.app` bundle only. If you regenerate the bundle by running `create_shortcut.sh` again, you will need to repeat these steps.

### Option 2 — Bake it into the bundle permanently

Convert your image to `.icns` format (macOS native icon format) and place it in the repo root:

```bash
# From a 1024×1024 PNG called icon.png:
mkdir icon.iconset
sips -z 512 512 icon.png --out icon.iconset/icon_512x512.png
iconutil -c icns icon.iconset -o portfolio_manager.icns
rm -r icon.iconset
```

Then update `create_shortcut.sh` to copy the file into the bundle:

```bash
# Add this line inside create_shortcut.sh, after the .app directory is created:
cp "$SCRIPT_DIR/portfolio_manager.icns" "$APP/Contents/Resources/AppIcon.icns"
```

Re-run `bash create_shortcut.sh` — the Dock icon will update on next launch.

---

## Code Style

| Tool | Purpose | Config location |
|------|---------|----------------|
| `black` | Auto-formatter (line length 88) | `pyproject.toml [tool.black]` |
| `ruff` | Fast linter (PEP 8 + more) | `pyproject.toml [tool.ruff]` |
| `mypy` | Static type checker | `pyproject.toml [tool.mypy]` |

Run all checks:

```bash
black src/ tests/
ruff check src/ tests/
mypy src/
```

### Docstring Format

All public classes and functions use **reStructuredText** (Sphinx-compatible):

```python
def complete_session(self, session_id: int, notes: str = "") -> Session:
    """Mark a session as completed and record the completion timestamp.

    :param session_id: Primary key of the session to complete.
    :type session_id: int
    :param notes: Optional session notes.
    :type notes: str
    :returns: The updated Session domain object.
    :rtype: Session
    :raises SessionStateError: If the session is already completed or cancelled.
    """
```

---

## Adding a Migration

1. Open `src/portfolio_manager/db/migrations.py`.
2. Append a new tuple to `_build_migrations()`:

```python
("v2", "Add color column to project", "ALTER TABLE project ADD COLUMN color TEXT;"),
```

3. Run the app — the migration will be applied automatically on next startup.
4. The database is backed up to `<name>.db.bak` before any migration is applied.

---

## Adding a New Repository

1. Create `src/portfolio_manager/repositories/my_entity_repo.py`.
2. Extend `BaseRepository`.
3. Write a `_row_to_entity()` private function for the column→dataclass mapping.
4. Add CRUD methods; use `with self.transaction():` for all writes.
5. Wire the repo into `app.py`.

---

## Adding a New Service

1. Create `src/portfolio_manager/services/my_service.py`.
2. Accept repository(ies) and `EventBus` via `__init__`.
3. Emit domain events (from `events/event_bus.py`) after state changes.
4. Write unit tests using fake repositories.
5. Wire into `app.py` and the relevant controller.

---

## Logging

The application uses Python's standard `logging` module exclusively — no `print()` for diagnostics.

```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Detailed trace")
logger.info("Normal event")
logger.warning("Unexpected but recoverable")
logger.error("Action failed")
logger.critical("Requires restart")
```

Logs are written to `~/.portfolio_manager/logs/app.log` (rotating, max 5 MB, 2 backups).

---

## Pre-commit Hooks (optional)

```bash
pip install pre-commit
pre-commit install
```

On each commit, `black` and `ruff` run automatically. The configuration lives in `.pre-commit-config.yaml` (add to repo root if desired).

---

## Building the Docs

```bash
# Live preview
mkdocs serve

# Static build — output goes to docs/ (GitHub Pages root)
mkdocs build --strict
```
