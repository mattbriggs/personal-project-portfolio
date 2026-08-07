"""Ordered migration registry.

Each entry is ``(version, description, sql)``. Ported verbatim from the original
``db/migrations.py`` so existing Tkinter-created databases (v1–v4) upgrade with
identical semantics. Add future migrations with incrementing version strings.
"""

from pathlib import Path

_SCHEMA_SQL_PATH = Path(__file__).resolve().parents[1] / "schema.sql"


def _load_schema() -> str:
    """Read the baseline (v1) schema SQL from disk.

    :rtype: str
    """
    return _SCHEMA_SQL_PATH.read_text(encoding="utf-8")


def build_migrations() -> list[tuple[str, str, str]]:
    """Return the ordered list of ``(version, description, sql)`` migrations.

    :rtype: list[tuple[str, str, str]]
    """
    return [
        (
            "v1",
            "Initial schema: project, session, milestone, project_score, weekly_review",
            _load_schema(),
        ),
        (
            "v2",
            "Add target_date column to milestone",
            "ALTER TABLE milestone ADD COLUMN target_date DATE;",
        ),
        (
            "v3",
            "Rework session and milestone models: new statuses, milestone_id on "
            "session, project end_date",
            """\
PRAGMA foreign_keys = OFF;

CREATE TABLE session_v3 (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id       INTEGER NOT NULL REFERENCES project(id) ON DELETE CASCADE,
    milestone_id     INTEGER REFERENCES milestone(id) ON DELETE SET NULL,
    scheduled_date   DATE    NOT NULL,
    week_key         TEXT    NOT NULL,
    duration_minutes INTEGER NOT NULL DEFAULT 90
                             CHECK (duration_minutes BETWEEN 15 AND 480),
    status           TEXT    NOT NULL DEFAULT 'backlog'
                             CHECK (status IN ('backlog', 'cancelled', 'planned', 'doing', 'done')),
    description      TEXT    NOT NULL DEFAULT '',
    notes            TEXT    NOT NULL DEFAULT '',
    created_at       DATETIME NOT NULL DEFAULT (datetime('now')),
    completed_at     DATETIME
);

INSERT INTO session_v3
    (id, project_id, scheduled_date, week_key, duration_minutes,
     status, description, notes, created_at, completed_at)
SELECT
    id, project_id, scheduled_date, week_key, duration_minutes,
    CASE status
        WHEN 'planned'   THEN 'planned'
        WHEN 'completed' THEN 'done'
        WHEN 'cancelled' THEN 'cancelled'
        ELSE 'backlog'
    END,
    focus, notes, created_at, completed_at
FROM session;

DROP TABLE session;
ALTER TABLE session_v3 RENAME TO session;

CREATE INDEX IF NOT EXISTS idx_session_project_id   ON session(project_id);
CREATE INDEX IF NOT EXISTS idx_session_week_key     ON session(week_key);
CREATE INDEX IF NOT EXISTS idx_session_status       ON session(status);
CREATE INDEX IF NOT EXISTS idx_session_milestone_id ON session(milestone_id);

CREATE TABLE milestone_v3 (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id     INTEGER NOT NULL REFERENCES project(id) ON DELETE CASCADE,
    description    TEXT    NOT NULL,
    status         TEXT    NOT NULL DEFAULT 'backlog'
                           CHECK (status IN ('backlog', 'cancelled', 'planned', 'doing', 'done')),
    completed_date DATE,
    target_date    DATE,
    sort_order     INTEGER NOT NULL DEFAULT 0,
    created_at     DATETIME NOT NULL DEFAULT (datetime('now')),
    updated_at     DATETIME NOT NULL DEFAULT (datetime('now'))
);

INSERT INTO milestone_v3
    (id, project_id, description, status, completed_date, target_date,
     sort_order, created_at, updated_at)
SELECT
    id, project_id, description,
    CASE WHEN is_complete = 1 THEN 'done' ELSE 'backlog' END,
    completed_date, target_date, sort_order, created_at, updated_at
FROM milestone;

DROP TABLE milestone;
ALTER TABLE milestone_v3 RENAME TO milestone;

CREATE TRIGGER IF NOT EXISTS milestone_updated_at
AFTER UPDATE ON milestone
FOR EACH ROW
BEGIN
    UPDATE milestone SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE INDEX IF NOT EXISTS idx_milestone_project_id ON milestone(project_id);

ALTER TABLE project ADD COLUMN end_date DATE;

PRAGMA foreign_keys = ON;
""",
        ),
        (
            "v4",
            "Add notes column to milestone",
            "ALTER TABLE milestone ADD COLUMN notes TEXT NOT NULL DEFAULT '';",
        ),
    ]
