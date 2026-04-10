"""Integration tests for SessionRepository."""

from datetime import date

import pytest

from portfolio_manager.exceptions import NotFoundError
from portfolio_manager.models.session import Session
from portfolio_manager.repositories.session_repo import SessionRepository
from portfolio_manager.utils.date_utils import to_week_key


@pytest.fixture
def repo(in_memory_db):
    return SessionRepository(in_memory_db)


@pytest.fixture
def a_session(repo, sample_project):
    today = date.today()
    return repo.create(
        Session(
            project_id=sample_project.id,
            scheduled_date=today,
            week_key=to_week_key(today),
            duration_minutes=90,
            status="planned",
            description="Write chapter 1",
        )
    )


class TestSessionRepositoryCreate:
    def test_create_assigns_id(self, repo, sample_project):
        today = date.today()
        s = repo.create(
            Session(
                project_id=sample_project.id,
                scheduled_date=today,
                week_key=to_week_key(today),
                duration_minutes=60,
                status="planned",
            )
        )
        assert s.id > 0

    def test_create_persists_fields(self, a_session, repo):
        fetched = repo.get(a_session.id)
        assert fetched.description == "Write chapter 1"
        assert fetched.duration_minutes == 90


class TestSessionRepositoryGet:
    def test_get_existing(self, repo, a_session):
        fetched = repo.get(a_session.id)
        assert fetched.id == a_session.id

    def test_get_missing_raises(self, repo):
        with pytest.raises(NotFoundError):
            repo.get(9999)


class TestSessionRepositoryList:
    def test_list_for_project(self, repo, sample_project, a_session):
        sessions = repo.list_for_project(sample_project.id)
        assert any(s.id == a_session.id for s in sessions)

    def test_list_for_project_week_filter(self, repo, sample_project, a_session):
        week_key = a_session.week_key
        sessions = repo.list_for_project(sample_project.id, week_key=week_key)
        assert all(s.week_key == week_key for s in sessions)

    def test_list_for_week(self, repo, sample_project, a_session):
        sessions = repo.list_for_week(a_session.week_key)
        assert any(s.id == a_session.id for s in sessions)


class TestSessionRepositoryUpdate:
    def test_update_status(self, repo, a_session):
        from datetime import datetime, timezone

        a_session.status = "done"
        a_session.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
        updated = repo.update(a_session)
        assert updated.status == "done"
        assert updated.completed_at is not None


class TestSessionRepositoryDelete:
    def test_delete_removes_session(self, repo, a_session):
        repo.delete(a_session.id)
        with pytest.raises(NotFoundError):
            repo.get(a_session.id)


class TestSessionRepositoryCountByStatus:
    def test_count_by_status(self, repo, sample_project, sample_sessions):
        week_key = sample_sessions[0].week_key
        counts = repo.count_by_status(sample_project.id, week_key)
        assert counts.get("planned", 0) >= 1
        assert counts.get("done", 0) >= 1
        assert counts.get("cancelled", 0) >= 1
