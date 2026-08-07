"""Shared pytest fixtures.

Provides an in-memory container, isolated repositories, a deterministic clock, and
a FastAPI test client (with and without authentication).
"""

from datetime import date, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from portfolio_manager.api.app import create_app
from portfolio_manager.bootstrap import build_container
from portfolio_manager.infrastructure.db.connection import DatabaseConnection
from portfolio_manager.infrastructure.db.migrations import run_migrations
from portfolio_manager.infrastructure.db.unit_of_work import SqliteUnitOfWork

TEST_TOKEN = "test-token-123"


class FrozenClock:
    """Deterministic clock for time-sensitive tests."""

    def __init__(self, now: datetime, today: date) -> None:
        self._now = now
        self._today = today

    def now(self) -> datetime:
        return self._now

    def today(self) -> date:
        return self._today


@pytest.fixture
def test_token() -> str:
    """The token the authenticated client uses."""
    return TEST_TOKEN


@pytest.fixture
def frozen_clock() -> FrozenClock:
    """A clock frozen to 2026-04-07 12:00 UTC (ISO week 2026.15)."""
    return FrozenClock(datetime(2026, 4, 7, 12, 0, 0), date(2026, 4, 7))


@pytest.fixture
def db() -> DatabaseConnection:
    """A fresh migrated in-memory database."""
    connection = DatabaseConnection(":memory:")
    run_migrations(connection)
    yield connection
    connection.close()


@pytest.fixture
def uow(db: DatabaseConnection) -> SqliteUnitOfWork:
    """A unit of work over the in-memory database."""
    return SqliteUnitOfWork(db)


@pytest.fixture
def container(tmp_path: Path):
    """An in-memory container with authentication enabled."""
    config_path = tmp_path / "config.toml"
    c = build_container(
        config_path=config_path,
        db_path=":memory:",
        token=TEST_TOKEN,
        production=False,
    )
    yield c
    c.close()


@pytest.fixture
def client(container) -> TestClient:
    """Authenticated-capable test client (send X-API-Key to pass auth)."""
    return TestClient(create_app(container))


@pytest.fixture
def auth_client(client: TestClient) -> TestClient:
    """Test client that sends a valid API key on every request."""
    client.headers.update({"X-API-Key": TEST_TOKEN})
    return client
