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
        # Future migrations go here, e.g.:
        # ("v2", "Add color column to project", "ALTER TABLE project ADD COLUMN color TEXT;"),
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
