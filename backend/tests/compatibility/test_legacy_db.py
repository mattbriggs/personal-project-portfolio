"""Compatibility tests: legacy Tkinter-created databases open and upgrade.

Builds a database at the original v1/v2 schema (old ``session.focus`` /
``session.status='completed'`` and ``milestone.is_complete``), records those
migration versions, then runs the current migration runner and verifies the data
survives the v3/v4 rework — proving existing databases open without manual
conversion.
"""

import sqlite3
from pathlib import Path

from portfolio_manager.infrastructure.db.connection import DatabaseConnection
from portfolio_manager.infrastructure.db.migrations import run_migrations
from portfolio_manager.infrastructure.db.migrations.versions import build_migrations

_V1_SQL = build_migrations()[0][2]  # baseline schema.sql
_V2_SQL = build_migrations()[1][2]  # milestone.target_date


def _build_legacy_v2_db(path: Path) -> None:
    conn = sqlite3.connect(path)
    conn.executescript(_V1_SQL)
    conn.executescript(_V2_SQL)
    conn.execute(
        "INSERT INTO schema_migration (version, description) VALUES ('v1', 'x'), ('v2', 'y')"
    )
    conn.execute(
        "INSERT INTO project (name, slug, status, priority) "
        "VALUES ('Legacy', 'legacy', 'active', 2)"
    )
    conn.execute(
        "INSERT INTO session (project_id, scheduled_date, week_key, duration_minutes, "
        "status, focus, notes) VALUES (1, '2026-04-07', '2026.15', 90, 'completed', "
        "'Old focus text', 'note')"
    )
    conn.execute(
        "INSERT INTO milestone (project_id, description, is_complete) "
        "VALUES (1, 'Old milestone', 1)"
    )
    conn.commit()
    conn.close()


def test_legacy_v2_database_upgrades_and_preserves_data(tmp_path: Path) -> None:
    path = tmp_path / "portfolio.db"
    _build_legacy_v2_db(path)

    db = DatabaseConnection(path)
    run_migrations(db)

    # Backup created before pending migrations.
    assert (tmp_path / "portfolio.db.bak").exists()

    # v3 mapped 'completed' -> 'done' and 'focus' -> 'description'.
    session = db.fetchone("SELECT * FROM session WHERE id = 1")
    assert session["status"] == "done"
    assert session["description"] == "Old focus text"

    # v3 mapped is_complete=1 -> status 'done'; v4 added notes.
    milestone = db.fetchone("SELECT * FROM milestone WHERE id = 1")
    assert milestone["status"] == "done"
    # sqlite3.Row: `in` checks values, so .keys() is required here.
    assert "notes" in milestone.keys()  # noqa: SIM118

    project = db.fetchone("SELECT * FROM project WHERE id = 1")
    assert project["name"] == "Legacy"
    db.close()


def test_legacy_write_persists_across_restart(tmp_path: Path) -> None:
    path = tmp_path / "portfolio.db"
    _build_legacy_v2_db(path)

    db = DatabaseConnection(path)
    run_migrations(db)
    with db.transaction():
        db.execute(
            "INSERT INTO milestone (project_id, description, status, notes) "
            "VALUES (1, 'New after upgrade', 'backlog', '')"
        )
    db.close()

    reopened = DatabaseConnection(path)
    rows = reopened.fetchall("SELECT description FROM milestone ORDER BY id")
    descriptions = [r["description"] for r in rows]
    assert "New after upgrade" in descriptions
    reopened.close()
