# Portfolio Manager

A personal, **local-first desktop application** for managing, scheduling, and executing work across a portfolio of creative and technical projects using time-boxed sessions.

## Overview

Portfolio Manager is a single-user desktop app backed by SQLite. It gives you one place to:

- Track active projects with traffic-light status indicators and priority 1–5 ordering
- Schedule and log time-boxed work sessions (15–480 min, default 90 min) against a configurable weekly hour budget
- Track milestones with a full five-state lifecycle and per-project plan documents with live Mermaid diagram preview
- Run weekly planning and review cycles, with a browsable history of past reviews
- See a dashboard score for every project, the overall portfolio, and a "This Week" focus panel showing upcoming milestones

The design philosophy is **low-friction and forgiving**: no required save actions, no failure messages for missed sessions, and a dashboard you can understand after four weeks away.

---

## Two applications, one database

The project is mid-migration. Both apps read the same SQLite database and the same domain rules.

| | Legacy app | V2 app |
| --- | --- | --- |
| Stack | Python + Tkinter | Tauri (Rust) + React + FastAPI sidecar |
| Source | `src/portfolio_manager/` | `backend/`, `frontend/`, `src-tauri/` |
| Status | **Working — the one you can run today** | Code complete, not yet packaged |
| Launch | `bash launch.sh` | not yet buildable (see below) |

The V2 stack is fully implemented and unit-tested at every layer, but it has **never been built into a runnable app bundle**. The Tauri CLI is not installed, so `npm run tauri dev` and `npm run tauri build` have not been exercised. Until that is resolved, the Tkinter app in `src/` remains the working application.

See the [design report](https://github.com/mattbriggs/personal-project-portfolio/blob/main/design/Portfolio-Manager-Tauri-React-Python-SRS-Design-Report.md) and [implementation plan](https://github.com/mattbriggs/personal-project-portfolio/blob/main/design/Portfolio-Manager-Tauri-React-Python-Implementation.md) for the migration scope, and the [completion report](release/completion-report.md) for verified status.

---

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

For the V2 stack, see the [Development Guide](development.md).

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

```bash
git pull origin main
.venv/bin/pip install -e .[dev] --quiet
```

No rebuild required — the macOS `.app` always calls `launch.sh` from the repo.
