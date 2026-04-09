"""Schema migration runner for Portfolio Manager.

Migrations are defined as a list of ``(version, description, sql)`` tuples
in :data:`MIGRATIONS`.  Each migration is applied once and recorded in the
``schema_migration`` table.  On first launch the full schema SQL is applied
as migration ``v1``.

Usage::

    from portfolio_manager.db.connection import DatabaseConnection
    from portfolio_manager.db.migrations import run_migrations

    db = DatabaseConnection.get()
    run_migrations(db)
"""

import logging
import shutil
from pathlib import Path

from portfolio_manager.db.connection import DatabaseConnection
from portfolio_manager.exceptions import MigrationError

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Schema DDL (loaded from schema.sql at runtime)
# ---------------------------------------------------------------------------

_SCHEMA_SQL_PATH = Path(__file__).parent / "schema.sql"


def _load_schema() -> str:
    """Read the schema SQL from disk.

    :rtype: str
    :raises MigrationError: If the file cannot be read.
    """
    try:
        return _SCHEMA_SQL_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        raise MigrationError(f"Cannot read schema file: {exc}") from exc


# ---------------------------------------------------------------------------
# Migration registry
# Each entry: (version_string, human_description, sql_to_apply)
# The initial schema creation is version "v1".
# Add future migrations here with incrementing version strings.
# ---------------------------------------------------------------------------


def _build_migrations() -> list[tuple[str, str, str]]:
    """Return the ordered list of migrations.

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
            "Rework session and milestone models: new statuses, milestone_id on session, project end_date",
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
    (id, project_id, description, status, completed_date, target_date, sort_order, created_at, updated_at)
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


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def _backup_database(db: DatabaseConnection) -> None:
    """Write a ``.bak`` copy of the database file before migrating.

    Skips backup for in-memory databases (path is ``:memory:``).

    :param db: Active :class:`~portfolio_manager.db.connection.DatabaseConnection`.
    """
    path = db._path  # noqa: SLF001 — intentional internal access
    if str(path) == ":memory:":
        return
    bak = path.with_suffix(".db.bak")
    try:
        shutil.copy2(path, bak)
        logger.info("Database backed up to %s", bak)
    except OSError as exc:
        logger.warning("Could not back up database: %s", exc)


def _applied_versions(db: DatabaseConnection) -> set[str]:
    """Return the set of migration version strings already applied.

    :param db: Active database connection.
    :rtype: set[str]
    """
    try:
        rows = db.fetchall("SELECT version FROM schema_migration")
        return {row["version"] for row in rows}
    except Exception:
        # Table may not exist yet on a brand-new database.
        return set()


def run_migrations(db: DatabaseConnection) -> None:
    """Apply any pending migrations to the database.

    Creates the ``schema_migration`` table if absent, then applies each
    migration whose version is not yet recorded.  A database backup is
    written before the first migration in a session.

    :param db: Active :class:`~portfolio_manager.db.connection.DatabaseConnection`.
    :raises MigrationError: If a migration SQL fails.
    """
    migrations = _build_migrations()
    applied = _applied_versions(db)
    pending = [(v, d, s) for v, d, s in migrations if v not in applied]

    if not pending:
        logger.debug("No pending migrations.")
        return

    logger.info(
        "%d migration(s) to apply: %s", len(pending), [v for v, _, _ in pending]
    )
    _backup_database(db)

    for version, description, sql in pending:
        logger.info("Applying migration %s: %s", version, description)
        try:
            db.executescript(sql)
            # Record the migration (executescript commits, so plain execute here).
            db.execute(
                "INSERT INTO schema_migration (version, description) VALUES (?, ?)",
                (version, description),
            )
            db.conn.commit()
            logger.info("Migration %s applied.", version)
        except Exception as exc:
            raise MigrationError(f"Migration {version!r} failed: {exc}") from exc
