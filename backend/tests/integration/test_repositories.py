"""Integration tests for SQLite repositories against a temporary database."""

from datetime import date

import pytest

from portfolio_manager.domain.models import Milestone, Project, ProjectScore, Session


def test_project_slug_unique_constraint(uow) -> None:
    import sqlite3

    uow.projects.create(Project(name="A", slug="dup"))
    with pytest.raises(sqlite3.IntegrityError):
        uow.projects.create(Project(name="B", slug="dup"))


def test_delete_cascades_sessions_and_milestones(uow) -> None:
    p = uow.projects.create(Project(name="P", slug="p"))
    uow.sessions.create(
        Session(project_id=p.id, scheduled_date=date(2026, 4, 7), week_key="2026.15")
    )
    uow.milestones.create(Milestone(project_id=p.id, description="m"))
    uow.projects.delete(p.id)
    assert uow.sessions.list_for_week("2026.15") == []
    assert uow.milestones.list_for_project(p.id) == []


def test_session_count_by_status(uow) -> None:
    p = uow.projects.create(Project(name="P", slug="p"))
    for status in ("planned", "done", "done", "cancelled"):
        uow.sessions.create(
            Session(
                project_id=p.id,
                scheduled_date=date(2026, 4, 7),
                week_key="2026.15",
                status=status,
            )
        )
    counts = uow.sessions.count_by_status(p.id, "2026.15")
    assert counts["done"] == 2
    assert counts["planned"] == 1
    assert counts["cancelled"] == 1


def test_score_one_per_project_week(uow) -> None:
    p = uow.projects.create(Project(name="P", slug="p"))
    uow.scores.upsert(ProjectScore(project_id=p.id, week_key="2026.15", score=10))
    uow.scores.upsert(ProjectScore(project_id=p.id, week_key="2026.15", score=42))
    got = uow.scores.get_for_week(p.id, "2026.15")
    assert got is not None and got.score == 42
    assert len(uow.scores.list_for_week("2026.15")) == 1


def test_milestone_count_excludes_cancelled(uow) -> None:
    p = uow.projects.create(Project(name="P", slug="p"))
    uow.milestones.create(Milestone(project_id=p.id, description="a", status="done"))
    uow.milestones.create(Milestone(project_id=p.id, description="b", status="backlog"))
    uow.milestones.create(Milestone(project_id=p.id, description="c", status="cancelled"))
    total, done = uow.milestones.count(p.id)
    assert (total, done) == (2, 1)


def test_milestone_session_minute_totals(uow) -> None:
    p = uow.projects.create(Project(name="P", slug="p"))
    m = uow.milestones.create(Milestone(project_id=p.id, description="m"))
    for minutes in (60, 30):
        uow.sessions.create(
            Session(
                project_id=p.id,
                milestone_id=m.id,
                scheduled_date=date(2026, 4, 7),
                week_key="2026.15",
                duration_minutes=minutes,
            )
        )
    pairs = uow.milestones.list_for_project_with_totals(p.id)
    assert pairs[0][1] == 90


def test_transaction_rollback_on_error(db, uow) -> None:
    p = uow.projects.create(Project(name="P", slug="p"))
    try:
        with db.transaction():
            db.execute("UPDATE project SET name = ? WHERE id = ?", ("Changed", p.id))
            raise RuntimeError("boom")
    except RuntimeError:
        pass
    assert uow.projects.get(p.id).name == "P"
