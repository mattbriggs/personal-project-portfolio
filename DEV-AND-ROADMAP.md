# Development And Roadmap

Portfolio Manager is a local-first desktop application for managing creative and technical project portfolios. The current state includes a Python application with MVC architecture, SQLite persistence, and various domain models. The roadmap outlines the transition to a Tauri desktop application, with a focus on packaging, distribution, and expanding features like import/export, backup workflows, and dashboard enhancements.

## Current State

Portfolio Manager is a local-first desktop application for managing creative
and technical project portfolios.

The established Python application includes:

- MVC desktop app with Tkinter views.
- SQLite persistence with versioned migrations.
- Project, session, milestone, score, and weekly review domain models.
- Service and repository layers for business logic and data access.
- Markdown project plan rendering with Mermaid diagram support.
- MkDocs/Material documentation generated into `docs/` for GitHub Pages.
- Unit, integration, and e2e tests.

The Tauri target state is a normal desktop application that bundles a frontend
UI with a local backend sidecar. The current repository contains packaging
artifacts for that direction, including:

- `frontend/dist/`: built web UI entry point.
- `src-tauri/binaries/portfolio-sidecar/`: packaged backend sidecar artifact.
- `src-tauri/gen/schemas/`: generated Tauri schemas.
- `portfolio-sidecar.spec` and
  `portfolio-sidecar-aarch64-apple-darwin.spec`: PyInstaller sidecar build
  specs.

## Legacy Python Quick Start

These workflows are useful for development and for running the older Python/Tk
desktop implementation directly from source.

### Requirements

- Python 3.11 or later.
- macOS is the primary desktop target; core logic also runs on Linux.

### Dock Shortcut

```bash
git clone <repo-url> portfolio-manager
cd portfolio-manager
bash create_shortcut.sh
```

The script creates `.venv`, installs dependencies, and writes:

```text
~/Applications/Portfolio Manager.app
```

Drag that app to the Dock for daily use.

### Shell Launcher

```bash
git clone <repo-url> portfolio-manager
cd portfolio-manager
bash launch.sh
```

`launch.sh` creates the virtual environment on first run and launches the app
each time afterward.

### Command Line

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
python -m portfolio_manager
```

### Updating Source Installs

```bash
git pull origin main
.venv/bin/pip install -e .[dev] --quiet
```

The legacy macOS `.app` bundle created by `create_shortcut.sh` calls
`launch.sh`, so it uses the current source checkout without rebuilding the app
bundle.

## Development Commands

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
mkdocs build --config-file site/mkdocs.yml

# Serve docs locally
mkdocs serve --config-file site/mkdocs.yml
```

The MkDocs build writes static output to `docs/` for GitHub Pages.

## Configuration

On first launch, the app writes defaults to:

```text
~/.portfolio_manager/config.toml
```

Default configuration:

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

```text
src/portfolio_manager/   Legacy Python desktop application source
tests/                   Unit, integration, and e2e tests
docs/                    Built MkDocs documentation site
site/                    MkDocs source
backend/                 Tauri sidecar/backend working area
frontend/                Tauri frontend build output
src-tauri/               Tauri packaging artifacts and generated schemas
launch.sh                Legacy daily-use launcher
create_shortcut.sh       Legacy macOS .app bundle creator
pyproject.toml           Python package config and dependencies
```

## Architecture Notes

- **MVC separation**: views are kept separate from business logic.
- **Repository layer**: SQL access is isolated in repositories.
- **Service layer**: project, session, scoring, planning, review, and settings
  behavior is coordinated outside the UI.
- **Strategy pattern**: scoring is injectable and replaceable.
- **Observer pattern**: the event bus decouples services from views.
- **Singleton database connection**: repositories share one connection manager.
- **Transaction context manager**: multi-step writes use explicit transactions.

## Development History

### 2.1.0 - 2026-04-09

Added weekly budget summaries, a dashboard "This Week" focus section, a past
reviews list, and one-click "Today" buttons for date fields.

Refined the data-management views around a consistent table, toolbar, and popup
dialog pattern. Session notes now persist through the service/controller/view
stack. Milestones now use the full backlog/planned/doing/done/cancelled status
lifecycle. The dashboard removed unused status-note UI in favor of weekly focus
information.

Database migration v4 added milestone notes.

### 2.0.0 - 2026-04-08

Introduced the full implemented application: MVC architecture, SQLite
migrations, typed domain models, repositories, services, event bus, six Tkinter
views, custom status and plan editor widgets, settings persistence, launch
scripts, MkDocs documentation, and broad unit/integration test coverage.

### 1.0.0

V1 was a requirements/specification phase. The V2 implementation superseded it.

## Roadmap

### Next Release: Tauri Desktop MVP

- Publish a downloadable macOS desktop build from GitHub Releases.
- Bundle the frontend UI and backend sidecar so end users do not install
  developer toolchains.
- Confirm first-launch database/config creation in packaged builds.
- Document macOS install, update, and Gatekeeper behavior.
- Add a basic smoke test for the packaged app launch path.

### Follow-Up Release: Distribution Polish

- Add code signing and notarization for macOS releases.
- Produce repeatable build scripts for sidecar and Tauri packaging.
- Add release checksums and clear version metadata.
- Decide whether built artifacts should remain in the repository or move fully
  to release assets.
- Add a user-facing migration/backup note for database schema changes.

### Later Releases

- Add Windows and Linux desktop build targets if the sidecar and UI packaging
  path remains stable.
- Add an in-app update check or document a manual update cadence.
- Improve import/export and backup workflows.
- Expand dashboard and review views around weekly planning workflows.
- Add stronger packaged-app tests that cover launch, sidecar health, database
  creation, and one representative create/edit flow.
- Refresh the documentation site so it clearly separates user guides,
  troubleshooting, and contributor/developer material.
