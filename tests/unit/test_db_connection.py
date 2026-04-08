"""Unit tests for DatabaseConnection."""

from pathlib import Path

import pytest

from portfolio_manager.db.connection import DatabaseConnection
from portfolio_manager.exceptions import DatabaseLockedError


@pytest.fixture
def db(in_memory_db):
    return in_memory_db


class TestDatabaseConnectionSingleton:
    def test_get_returns_same_instance(self, db):
        a = DatabaseConnection.get()
        b = DatabaseConnection.get()
        assert a is b

    def test_get_before_init_raises(self):
        DatabaseConnection.reset()
        with pytest.raises(RuntimeError):
            DatabaseConnection.get()


class TestDatabaseConnectionExecute:
    def test_fetchall_returns_rows(self, db):
        rows = db.fetchall("SELECT * FROM project")
        assert isinstance(rows, list)

    def test_fetchone_returns_none_for_empty(self, db):
        result = db.fetchone("SELECT * FROM project WHERE id = 9999")
        assert result is None

    def test_execute_insert_and_fetch(self, db):
        with db.transaction():
            db.execute(
                "INSERT INTO project (name, slug, status) VALUES (?, ?, ?)",
                ("Test", "test", "active"),
            )
        row = db.fetchone("SELECT * FROM project WHERE slug = 'test'")
        assert row is not None
        assert row["name"] == "Test"


class TestDatabaseConnectionTransaction:
    def test_transaction_rollback_on_error(self, db):
        try:
            with db.transaction():
                db.execute(
                    "INSERT INTO project (name, slug, status) VALUES (?, ?, ?)",
                    ("Will Rollback", "will-rollback", "active"),
                )
                raise ValueError("forced rollback")
        except ValueError:
            pass
        row = db.fetchone("SELECT * FROM project WHERE slug = 'will-rollback'")
        assert row is None
