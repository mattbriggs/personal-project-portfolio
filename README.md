# Portfolio Manager

A personal desktop application for managing, scheduling, and executing work across a portfolio of creative and technical projects using time-boxed sessions.

## Features

- **Portfolio dashboard** — traffic-light status indicators, scores, weekly session totals, and upcoming milestones at a glance
- **Project management** — active / backlog / archive lifecycle with priority 1–5 ordering
- **Session scheduling** — time-boxed work units (15–480 min, default 90 min) linked to projects, milestones, and weeks
- **Weekly budget tracking** — configurable weekly hour budget with a live planned/done/remaining summary in the Sessions tab
- **Milestone tracking** — outcome-based milestones with full status lifecycle (backlog → planned → doing → done / cancelled)
- **Plan documents** — per-project Markdown editor with live Mermaid diagram preview
- **Weekly review** — structured reflection form with a browsable history of past reviews
- **Scoring** — configurable algorithm (session completion + milestone ratio)
- **Auto-save** — all changes commit immediately; no explicit save required
- **macOS Dock shortcut** — one-click launch via a native `.app` bundle

## Requirements

- Python 3.11 or later
- macOS (primary) — core logic runs on Linux too

## Quick Start

### Option 1 — Dock shortcut (recommended for daily use)

```bash
git clone <repo-url> portfolio-manager
cd portfolio-manager
bash create_shortcut.sh
```

The script creates `.venv`, installs dependencies, and writes
`~/Applications/Portfolio Manager.app`. Drag it to the Dock.

### Option 2 — Shell script

```bash
git clone <repo-url> portfolio-manager
cd portfolio-manager
bash launch.sh
```

`launch.sh` creates the venv on first run and launches the app every time.

### Option 3 — Command line (development)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
python -m portfolio_manager
```

## Updating

```bash
git pull origin main
.venv/bin/pip install -e .[dev] --quiet
```

No rebuild of the `.app` bundle is required — it calls `launch.sh` which always uses the current source.

## Development

```bash
# Install with dev dependencies
pip install -e .[dev]

# Run tests
pytest

# Lint
ruff check src/ tests/

# Format
black src/ tests/

# Build docs
mkdocs build --config-file site/mkdocs.yml       # output → docs/ (GitHub Pages)
mkdocs serve --config-file site/mkdocs.yml       # live preview at http://127.0.0.1:8000
```

## Configuration

On first launch the application writes defaults to `~/.portfolio_manager/config.toml`.
Edit that file to override settings:

```toml
[app]
log_level = "INFO"
theme = "light"

[session]
default_duration_minutes = 90
weekly_budget_hours = 12

[database]
path = "~/.portfolio_manager/portfolio.db"
```

## Project Structure

```
src/portfolio_manager/   # Application source
tests/                   # Unit, integration, and e2e tests
docs/                    # MkDocs documentation site
launch.sh                # Daily-use launcher
create_shortcut.sh       # macOS .app bundle creator
pyproject.toml           # Build config and dependencies
```

## License

See [LICENSE](LICENSE).
