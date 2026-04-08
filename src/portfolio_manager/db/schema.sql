-- Portfolio Manager V2 — SQLite Schema
-- All timestamps stored as UTC ISO 8601 strings.
-- Foreign key enforcement must be enabled per-connection: PRAGMA foreign_keys = ON;

PRAGMA journal_mode = WAL;

-- ============================================================
-- SCHEMA_MIGRATION
-- Tracks which migrations have been applied.
-- ============================================================
CREATE TABLE IF NOT EXISTS schema_migration (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    version     TEXT    NOT NULL UNIQUE,
    description TEXT    NOT NULL,
    applied_at  DATETIME NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================
-- PROJECT
-- ============================================================
CREATE TABLE IF NOT EXISTS project (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL,
    slug            TEXT    NOT NULL UNIQUE,
    status          TEXT    NOT NULL DEFAULT 'active'
                            CHECK (status IN ('active', 'backlog', 'archive')),
    priority        INTEGER NOT NULL DEFAULT 3
                            CHECK (priority BETWEEN 1 AND 5),
    started_date    DATE,
    owner           TEXT    NOT NULL DEFAULT 'Matt Briggs',
    review_cadence  TEXT    NOT NULL DEFAULT 'weekly',
    plan_content    TEXT    NOT NULL DEFAULT '',
    description     TEXT    NOT NULL DEFAULT '',
    created_at      DATETIME NOT NULL DEFAULT (datetime('now')),
    updated_at      DATETIME NOT NULL DEFAULT (datetime('now'))
);

-- Auto-update updated_at on every modification.
CREATE TRIGGER IF NOT EXISTS project_updated_at
AFTER UPDATE ON project
FOR EACH ROW
BEGIN
    UPDATE project SET updated_at = datetime('now') WHERE id = NEW.id;
END;

-- ============================================================
-- SESSION
-- ============================================================
CREATE TABLE IF NOT EXISTS session (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id       INTEGER NOT NULL REFERENCES project(id) ON DELETE CASCADE,
    scheduled_date   DATE    NOT NULL,
    week_key         TEXT    NOT NULL,
    duration_minutes INTEGER NOT NULL DEFAULT 60
                             CHECK (duration_minutes BETWEEN 60 AND 180),
    status           TEXT    NOT NULL DEFAULT 'planned'
                             CHECK (status IN ('planned', 'completed', 'cancelled')),
    focus            TEXT    NOT NULL DEFAULT '',
    notes            TEXT    NOT NULL DEFAULT '',
    created_at       DATETIME NOT NULL DEFAULT (datetime('now')),
    completed_at     DATETIME
);

CREATE INDEX IF NOT EXISTS idx_session_project_id  ON session(project_id);
CREATE INDEX IF NOT EXISTS idx_session_week_key    ON session(week_key);
CREATE INDEX IF NOT EXISTS idx_session_status      ON session(status);

-- ============================================================
-- MILESTONE
-- ============================================================
CREATE TABLE IF NOT EXISTS milestone (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id     INTEGER NOT NULL REFERENCES project(id) ON DELETE CASCADE,
    description    TEXT    NOT NULL,
    is_complete    BOOLEAN NOT NULL DEFAULT 0,
    completed_date DATE,
    sort_order     INTEGER NOT NULL DEFAULT 0,
    created_at     DATETIME NOT NULL DEFAULT (datetime('now')),
    updated_at     DATETIME NOT NULL DEFAULT (datetime('now'))
);

CREATE TRIGGER IF NOT EXISTS milestone_updated_at
AFTER UPDATE ON milestone
FOR EACH ROW
BEGIN
    UPDATE milestone SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE INDEX IF NOT EXISTS idx_milestone_project_id ON milestone(project_id);

-- ============================================================
-- PROJECT_SCORE
-- One record per project per week.
-- ============================================================
CREATE TABLE IF NOT EXISTS project_score (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id         INTEGER NOT NULL REFERENCES project(id) ON DELETE CASCADE,
    week_key           TEXT    NOT NULL,
    score              INTEGER CHECK (score BETWEEN 0 AND 100),
    status             TEXT    CHECK (status IN ('green', 'yellow', 'red')),
    status_note        TEXT    NOT NULL DEFAULT '',
    is_manual_override BOOLEAN NOT NULL DEFAULT 0,
    override_reason    TEXT    NOT NULL DEFAULT '',
    created_at         DATETIME NOT NULL DEFAULT (datetime('now')),
    UNIQUE (project_id, week_key)
);

CREATE INDEX IF NOT EXISTS idx_score_week_key ON project_score(week_key);

-- ============================================================
-- WEEKLY_REVIEW
-- One review per week.
-- ============================================================
CREATE TABLE IF NOT EXISTS weekly_review (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    week_key              TEXT    NOT NULL UNIQUE,
    date_from             DATE,
    date_to               DATE,
    hours_invested        REAL,
    sessions_completed    INTEGER,
    what_moved            TEXT    NOT NULL DEFAULT '',
    what_stalled          TEXT    NOT NULL DEFAULT '',
    signals               TEXT    NOT NULL DEFAULT '',
    decision_next_week    TEXT    NOT NULL DEFAULT '',
    primary_focus         TEXT    NOT NULL DEFAULT '',
    project_to_deprioritize TEXT  NOT NULL DEFAULT '',
    risk_to_watch         TEXT    NOT NULL DEFAULT '',
    first_session_target  TEXT    NOT NULL DEFAULT '',
    written_to_repo       BOOLEAN NOT NULL DEFAULT 0,
    created_at            DATETIME NOT NULL DEFAULT (datetime('now')),
    updated_at            DATETIME NOT NULL DEFAULT (datetime('now'))
);

CREATE TRIGGER IF NOT EXISTS weekly_review_updated_at
AFTER UPDATE ON weekly_review
FOR EACH ROW
BEGIN
    UPDATE weekly_review SET updated_at = datetime('now') WHERE id = NEW.id;
END;
