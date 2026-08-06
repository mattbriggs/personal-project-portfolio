"""Migration runner with backup-before-migrate behavior.

Ported verbatim from the original ``db/migrations.run_migrations`` so upgrade,
backup, and version-recording semantics are unchanged for legacy databases.
"""

import logging
import shutil
from pathlib import Path

from portfolio_manager.domain.errors import MigrationError
from portfolio_manager.infrastructure.db.connection import DatabaseConnection
from portfolio_manager.infrastructure.db.migrations.versions import build_migrations

logger = logging.getLogger(__name__)


def _backup_database(db: DatabaseConnection) -> None:
    """Write a ``.db.bak`` copy of the database before migrating.

    Skips in-memory databases.

    :param db: Active database connection.
    """
    path = db.path
    if str(path) == ":memory:":
        return
    path = Path(path)
    bak = path.with_suffix(".db.bak")
    try:
        shutil.copy2(path, bak)
        logger.info("Database backed up to %s", bak)
    except OSError as exc:
        logger.warning("Could not back up database: %s", exc)


def _applied_versions(db: DatabaseConnection) -> set[str]:
    """Return the set of migration version strings already applied.

    :rtype: set[str]
    """
    try:
        rows = db.fetchall("SELECT version FROM schema_migration")
        return {row["version"] for row in rows}
    except Exception:  # noqa: BLE001 — table may not exist on a new database
        return set()


def run_migrations(db: DatabaseConnection) -> None:
    """Apply any pending migrations to the database.

    Creates the ``schema_migration`` table (via the v1 baseline) if absent, then
    applies each migration whose version is not yet recorded. A backup is written
    before the first pending migration in a session.

    :param db: Active database connection.
    :raises MigrationError: If a migration SQL statement fails.
    """
    migrations = build_migrations()
    applied = _applied_versions(db)
    pending = [(v, d, s) for v, d, s in migrations if v not in applied]

    if not pending:
        logger.debug("No pending migrations.")
        return

    logger.info("%d migration(s) to apply: %s", len(pending), [v for v, _, _ in pending])
    _backup_database(db)

    for version, description, sql in pending:
        logger.info("Applying migration %s: %s", version, description)
        try:
            db.executescript(sql)
            db.execute(
                "INSERT INTO schema_migration (version, description) VALUES (?, ?)",
                (version, description),
            )
            db.conn.commit()
            logger.info("Migration %s applied.", version)
        except Exception as exc:
            raise MigrationError(f"Migration {version!r} failed: {exc}") from exc
