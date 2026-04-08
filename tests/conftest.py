"""Shared pytest fixtures for Portfolio Manager tests.

Fixtures provided:
- ``in_memory_db`` — fully migrated :class:`DatabaseConnection` backed by ``:memory:``
- ``test_config`` — :class:`Settings` with in-memory database path
- ``sample_project`` — a persisted :class:`Project` with plan_content
- ``sample_sessions`` — planned / completed / cancelled sessions for the sample project
"""

from datetime import date
from pathlib import Path

import pytest

from portfolio_manager.config.settings import DatabaseConfig, Settings
from portfolio_manager.db.connection import DatabaseConnection
from portfolio_manager.db.migrations import run_migrations
from portfolio_manager.events.event_bus import EventBus
from portfolio_manager.models.project import Project
from portfolio_manager.models.session import Session
from portfolio_manager.repositories.project_repo import ProjectRepository
from portfolio_manager.repositories.session_repo import SessionRepository
from portfolio_manager.utils.date_utils import to_week_key


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset shared singletons before and after every test."""
    DatabaseConnection.reset()
    EventBus.reset()
    yield
    DatabaseConnection.reset()
    EventBus.reset()


@pytest.fixture
def in_memory_db() -> DatabaseConnection:
    """Return a fully migrated in-memory :class:`DatabaseConnection`.

    :rtype: DatabaseConnection
    """
    db = DatabaseConnection.initialise(Path(":memory:"))
    run_migrations(db)
    return db


@pytest.fixture
def test_config() -> Settings:
    """Return a :class:`Settings` object configured for testing.

    Uses an in-memory database path so no files are written during tests.

    :rtype: Settings
    """
    cfg = Settings()
    cfg.database = DatabaseConfig(path=":memory:")
    return cfg


@pytest.fixture
def sample_project(in_memory_db: DatabaseConnection) -> Project:
    """Return a persisted :class:`Project` in the in-memory database.

    :rtype: Project
    """
    repo = ProjectRepository(in_memory_db)
    project = Project(
        name="Test Novel",
        slug="test-novel",
        status="active",
        priority=2,
        description="A test project.",
        plan_content="# Test Plan\n\nThis is a test plan.\n\n```mermaid\nflowchart LR\n  A --> B\n```",
    )
    return repo.create(project)


@pytest.fixture
def sample_sessions(
    in_memory_db: DatabaseConnection, sample_project: Project
) -> list[Session]:
    """Return three sessions (planned, completed, cancelled) for *sample_project*.

    :rtype: list[Session]
    """
    repo = SessionRepository(in_memory_db)
    today = date.today()
    week_key = to_week_key(today)

    planned = repo.create(
        Session(
            project_id=sample_project.id,
            scheduled_date=today,
            week_key=week_key,
            duration_minutes=90,
            status="planned",
            focus="Write chapter 1",
        )
    )
    completed = repo.create(
        Session(
            project_id=sample_project.id,
            scheduled_date=today,
            week_key=week_key,
            duration_minutes=60,
            status="completed",
            focus="Outline done",
            notes="Completed outline.",
        )
    )
    cancelled = repo.create(
        Session(
            project_id=sample_project.id,
            scheduled_date=today,
            week_key=week_key,
            duration_minutes=120,
            status="cancelled",
        )
    )
    return [planned, completed, cancelled]
