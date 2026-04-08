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
mkdocs serve --config-file docs/mkdocs.yml

# Static build (output in site/)
mkdocs build --config-file docs/mkdocs.yml --strict
```
