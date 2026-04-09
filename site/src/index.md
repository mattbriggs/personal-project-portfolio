# Portfolio Manager

A personal desktop application for managing, scheduling, and executing work across a portfolio of creative and technical projects using time-boxed sessions.

## Overview

Portfolio Manager is a **single-user Tkinter desktop app** backed by SQLite. It gives you one place to:

- Track active projects with traffic-light status indicators and priority 1–5 ordering
- Schedule and log time-boxed work sessions (15–480 min, default 90 min) against a configurable weekly hour budget
- Track milestones with a full five-state lifecycle and per-project plan documents with live Mermaid diagram preview
- Run weekly planning and review cycles, with a browsable history of past reviews
- See a dashboard score for every project, the overall portfolio, and a "This Week" focus panel showing upcoming milestones

The design philosophy is **low-friction and forgiving**: no required save actions, no failure messages for missed sessions, and a dashboard you can understand after four weeks away.

---

## Quick Start

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

---

## First Launch

On first launch with no existing data:

1. `~/.portfolio_manager/config.toml` is written with defaults.
2. The SQLite database is created at `~/.portfolio_manager/portfolio.db`.
3. The full schema (v1 migration) is applied.
4. The app opens on the empty Dashboard.

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

## Updating

```bash
git pull origin main
.venv/bin/pip install -e .[dev] --quiet
```

No rebuild required — the macOS `.app` always calls `launch.sh` from the repo.
