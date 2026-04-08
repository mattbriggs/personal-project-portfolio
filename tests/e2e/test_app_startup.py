"""End-to-end headless smoke test — verifies the application starts without error.

The Tk window is withdrawn immediately so no display is required on CI.
The test exercises the full startup sequence: config loading, DB initialisation,
migration, and main window creation.
"""

import tkinter as tk
from pathlib import Path

import pytest

from portfolio_manager.app import build_app
from portfolio_manager.config.settings import DatabaseConfig, Settings


@pytest.fixture
def headless_settings(tmp_path):
    """Return Settings pointing at a temporary file-based database."""
    db_path = tmp_path / "test_portfolio.db"
    cfg = Settings()
    cfg.database = DatabaseConfig(path=str(db_path))
    return cfg


class TestAppStartup:
    def test_builds_without_error(self, headless_settings):
        """build_app() should return a MainWindow without raising."""
        try:
            window = build_app(settings=headless_settings)
            window.withdraw()  # hide the window — no display needed
            window.update()    # process any pending Tk events
            window.destroy()
        except tk.TclError as exc:
            pytest.skip(f"No display available for Tk: {exc}")

    def test_database_file_created(self, headless_settings, tmp_path):
        """The database file should exist after startup."""
        db_path = Path(headless_settings.database.path)
        try:
            window = build_app(settings=headless_settings)
            window.withdraw()
            window.destroy()
        except tk.TclError:
            pytest.skip("No display available")
        assert db_path.exists()

    def test_migrations_applied(self, headless_settings):
        """schema_migration table should have at least one record after startup."""
        from portfolio_manager.db.connection import DatabaseConnection
        try:
            window = build_app(settings=headless_settings)
            window.withdraw()
            window.destroy()
        except tk.TclError:
            pytest.skip("No display available")

        db = DatabaseConnection.get()
        rows = db.fetchall("SELECT * FROM schema_migration")
        assert len(rows) >= 1
        assert rows[0]["version"] == "v1"
