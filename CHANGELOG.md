# Changelog

All notable changes to Portfolio Manager are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [2.0.0] — 2026-04-08

### Added

- Full MVC architecture with layered Service and Repository pattern
- SQLite database with versioned migration system (`db/migrations.py`)
- Five domain models: `Project`, `Session`, `Milestone`, `ProjectScore`, `WeeklyReview`
- Five repositories with full CRUD and typed domain-object mapping
- `ProjectService` — project lifecycle (create, update, archive, delete)
- `SessionService` — session lifecycle (create, complete, reschedule, cancel, reopen)
- `ScoringService` — pluggable Strategy pattern; default algorithm: 60% sessions + 40% milestones
- `PlanService` — Markdown → HTML rendering with Mermaid.js diagram support
- `WeekService` — ISO 8601 week-key computation and date-range helpers
- `EventBus` — in-process Observer pattern; 11 named domain events
- Six Tkinter views: Dashboard, Sessions, Projects, Milestones, Weekly Review, Settings
- Three custom widgets: `StatusBadge` (traffic-light), `ScoreBar`, `PlanEditor` (split-pane with debounced live preview)
- Settings panel persisting to `~/.portfolio_manager/config.toml`
- `launch.sh` — Tk-capable Python detection and venv auto-creation
- `create_shortcut.sh` — macOS `.app` bundle for Dock placement
- MkDocs/Material documentation site (`site/` source → `docs/` HTML for GitHub Pages)
- 140 unit and integration tests at 94.8% coverage

### Architecture

- MVC separation: views contain no business logic
- Repository layer: no SQL outside `repositories/`
- Strategy pattern: scoring algorithm injectable and replaceable
- Observer pattern: `EventBus` decouples services from views
- Singleton: `DatabaseConnection` shared across all repositories
- Transaction context manager: `with db.transaction():` on all multi-step writes

---

## [1.0.0] — (V1 — not implemented in this repository)

V1 SRS defined behavioural requirements only. V2 supersedes it with a full implementation specification.
