"""Schema migration runner and version registry."""

from portfolio_manager.infrastructure.db.migrations.runner import run_migrations

__all__ = ["run_migrations"]
