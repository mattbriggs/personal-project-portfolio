# Changelog

All notable changes to Portfolio Manager are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [2.1.0] — 2026-04-09

### Added

- **Weekly budget bar** — Sessions tab now shows a summary bar with planned minutes, done minutes, budget (from settings), and remaining time for the displayed week
- **Dashboard "This Week" section** — new focus panel below Portfolio Summary shows this week's session totals and the next upcoming (non-done) milestone per active project, sorted by target date
- **Past reviews list** — Weekly Review tab now shows a left-panel listbox of all saved reviews; click any entry to load it directly, removing the need to type week keys manually
- **"Today" button** on all date entry fields — session date, milestone target date, and project start/end dates now have a one-click "Today" shortcut next to the entry

### Changed

- **Consistent data-view pattern** — Sessions, Projects, and Milestones tabs now all use a full-width table + toolbar + popup dialog layout with double-click to edit
- **Session popup** — fields: Project, Milestone, Session name, Date, Status, Min, Description (notes); notes are now correctly persisted on create (previously silently dropped)
- **Project popup** — non-modal 900×680 window with metadata (name, description, status, priority, start, end) and embedded Plan document editor with preview-first toggle
- **Milestone popup** — fields: Milestone name, Target date (with live Week derivation), Status, Total Min (read-only), Description (notes)
- **Week navigator** — selecting a week in the left panel now syncs Sessions and Review silently without forcing a tab switch
- **Project priority** — dropdown now offers 1–5 (matching the data model and SRS), not the previous 1–3
- **Milestone status** — replaced binary `is_complete` toggle with a full five-state status (backlog / planned / doing / done / cancelled)
- **Session notes** — `create_session()` now accepts and persists a `notes` parameter through the full service/controller/view stack

### Removed

- `score_bar.py` widget — was never imported or used anywhere; dead code removed
- **Dashboard Status Notes panel** — removed because `status_note` was always an empty string (no entry point existed); replaced by the new "This Week" focus section
- **Left panel project list** — replaced by a week navigator (12 past + current + 4 future weeks, current week highlighted)

### Database

- Migration v4: `ALTER TABLE milestone ADD COLUMN notes TEXT NOT NULL DEFAULT ''`

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
- Two custom widgets: `StatusBadge` (traffic-light + text for accessibility), `PlanEditor` (split-pane Markdown editor with debounced live Mermaid preview)
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
