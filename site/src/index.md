# Portfolio Manager

A personal, **local-first desktop application** for managing, scheduling, and
executing work across a portfolio of creative and technical projects using
time-boxed sessions.

## Overview

Portfolio Manager is a single-user desktop app backed by SQLite. The current
desktop application is the Tauri stack: a React renderer, Rust shell, and local
FastAPI sidecar packaged into a macOS app. It gives you one place to:

- Track active projects with traffic-light status indicators and priority 1–5 ordering
- Schedule and log time-boxed work sessions (15–480 min, default 90 min) against a configurable weekly hour budget
- Track milestones with a full five-state lifecycle and per-project plan documents with live Mermaid diagram preview
- Run weekly planning and review cycles, with a browsable history of past reviews
- See a dashboard score for every project, the overall portfolio, and a "This Week" focus panel showing upcoming milestones

The design philosophy is **low-friction and forgiving**: no required save actions, no failure messages for missed sessions, and a dashboard you can understand after four weeks away.

---

## Current App And Legacy App

The repository still contains the legacy Tkinter app for compatibility and
comparison, but the current desktop target is the Tauri app. Both apps read the
same SQLite database and use the same core domain rules.

| | Current desktop app | Legacy app |
| --- | --- | --- |
| Stack | Tauri (Rust) + React + FastAPI sidecar | Python + Tkinter |
| Source | `backend/`, `frontend/`, `src-tauri/` | `src/portfolio_manager/` |
| Status | Current app; builds to `.app` and DMG | Maintained as legacy/developer path |
| Launch | `/Applications/Portfolio Manager.app` or a local Tauri build | `bash launch.sh` |

The Tauri app builds to a macOS application bundle and DMG, supervises the
FastAPI sidecar automatically, and reads the same database as the Tkinter app.
The Tkinter app remains useful for legacy troubleshooting and domain
comparison, but new desktop work should target the Tauri stack.

See the [design report](https://github.com/mattbriggs/personal-project-portfolio/blob/main/design/Portfolio-Manager-Tauri-React-Python-SRS-Design-Report.md) and [implementation plan](https://github.com/mattbriggs/personal-project-portfolio/blob/main/design/Portfolio-Manager-Tauri-React-Python-Implementation.md) for the migration scope, and the [completion report](release/completion-report.md) for verified status.

---

## Quick Start (current desktop app)

For a local developer build:

```bash
cd /Users/mattbriggs/Git/personal-project-portfolio
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e "backend[dev,package]"
npm install
.venv/bin/python scripts/build_sidecar.py
npm run tauri build
scripts/install_macos_app.sh
```

For detailed build instructions, see the
[Development Guide](development.md#packaging-macos) and the developer local
build runbook in
[`design/2026.08-07-Build-Local-App-Dev.md`](https://github.com/mattbriggs/personal-project-portfolio/blob/main/design/2026.08-07-Build-Local-App-Dev.md).

## Quick Start (legacy app)

### Option 1 — macOS Dock shortcut

```bash
git clone <repo-url> portfolio-manager
cd portfolio-manager
bash create_shortcut.sh
```

Drag `~/Applications/Portfolio Manager.app` to the Dock.

### Option 2 — Shell script

```bash
bash launch.sh
```

`launch.sh` creates a `.venv` on first run and launches the app every time.

### Option 3 — Development

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
python -m portfolio_manager
```

Use the legacy app when you specifically need the old Tkinter launcher or are
debugging behavior shared with earlier databases.

---

## First Launch

On first launch with no existing data:

1. `~/.portfolio_manager/config.toml` is written with defaults.
2. The SQLite database is created at `~/.portfolio_manager/portfolio.db`.
3. The full schema (v1 migration) is applied.
4. The app opens on the empty Dashboard.

Databases created by the Tkinter app (schema v1–v4) open in the V2 app without manual conversion. A backup is written before any pending migration runs.

---

## Configuration

Edit `~/.portfolio_manager/config.toml` to change defaults:

```toml
[app]
log_level = "INFO"   # DEBUG | INFO | WARNING | ERROR
theme = "light"      # light | dark (coming in future release)

[session]
default_duration_minutes = 90
weekly_budget_hours = 12

[database]
path = "~/.portfolio_manager/portfolio.db"
```

---

## Default local paths

| Purpose | Path |
| --- | --- |
| Config | `~/.portfolio_manager/config.toml` |
| Database | `~/.portfolio_manager/portfolio.db` |
| Backups | `~/.portfolio_manager/portfolio.db.bak` |
| Logs | `~/.portfolio_manager/logs/` |

---

## Updating

For the current Tauri app, rebuild after pulling source changes:

```bash
git pull --rebase origin main
.venv/bin/python -m pip install -e "backend[dev,package]"
npm install
.venv/bin/python scripts/build_sidecar.py
npm run tauri build
scripts/install_macos_app.sh
```

For the legacy app, `git pull` plus `.venv/bin/pip install -e .[dev]` is enough
because the Dock wrapper calls `launch.sh` from the checkout.
