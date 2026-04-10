"""Integration tests for SessionService with real repositories."""

from datetime import date, timedelta

import pytest

from portfolio_manager.db.connection import DatabaseConnection
from portfolio_manager.events.event_bus import EventBus
from portfolio_manager.exceptions import ValidationError
from portfolio_manager.repositories.session_repo import SessionRepository
from portfolio_manager.services.session_service import SessionService
from portfolio_manager.utils.date_utils import to_week_key


@pytest.fixture
def svc(in_memory_db):
    repo = SessionRepository(in_memory_db)
    bus = EventBus.get()
    return SessionService(repo, bus)


@pytest.fixture
def today():
    return date.today()


class TestSessionServiceCreate:
    def test_create_returns_session_with_id(self, svc, sample_project, today):
        s = svc.create_session(sample_project.id, today)
        assert s.id > 0
        assert s.status == "backlog"

    def test_create_sets_week_key(self, svc, sample_project, today):
        s = svc.create_session(sample_project.id, today)
        assert s.week_key == to_week_key(today)

    def test_create_invalid_duration_raises(self, svc, sample_project, today):
        with pytest.raises(ValidationError):
            svc.create_session(sample_project.id, today, duration_minutes=10)

    def test_create_emits_event(self, svc, sample_project, today):
        received = []
        EventBus.get().subscribe("SESSION_CREATED", lambda **kw: received.append(kw))
        svc.create_session(sample_project.id, today)
        assert len(received) == 1

    def test_create_stores_description(self, svc, sample_project, today):
        s = svc.create_session(sample_project.id, today, description="Write chapter 1")
        assert s.description == "Write chapter 1"


class TestSessionServiceComplete:
    def test_complete_changes_status_to_done(self, svc, sample_project, today):
        s = svc.create_session(sample_project.id, today)
        completed = svc.complete_session(s.id, notes="Done!", description="Final edit")
        assert completed.status == "done"
        assert completed.completed_at is not None
        assert completed.notes == "Done!"

    def test_complete_sets_completed_at(self, svc, sample_project, today):
        s = svc.create_session(sample_project.id, today)
        completed = svc.complete_session(s.id)
        assert completed.completed_at is not None

    def test_complete_from_cancelled_changes_to_done(self, svc, sample_project, today):
        s = svc.create_session(sample_project.id, today)
        svc.cancel_session(s.id)
        result = svc.complete_session(s.id)
        assert result.status == "done"

    def test_complete_emits_event(self, svc, sample_project, today):
        received = []
        EventBus.get().subscribe("SESSION_COMPLETED", lambda **kw: received.append(kw))
        s = svc.create_session(sample_project.id, today)
        svc.complete_session(s.id)
        assert len(received) == 1


class TestSessionServiceReschedule:
    def test_reschedule_updates_date_and_week(self, svc, sample_project, today):
        s = svc.create_session(sample_project.id, today)
        next_week = today + timedelta(days=7)
        updated = svc.reschedule_session(s.id, next_week)
        assert updated.scheduled_date == next_week
        assert updated.week_key == to_week_key(next_week)

    def test_reschedule_from_done_status(self, svc, sample_project, today):
        s = svc.create_session(sample_project.id, today)
        svc.complete_session(s.id)
        updated = svc.reschedule_session(s.id, today + timedelta(days=1))
        assert updated.scheduled_date == today + timedelta(days=1)


class TestSessionServiceCancel:
    def test_cancel_changes_status(self, svc, sample_project, today):
        s = svc.create_session(sample_project.id, today)
        cancelled = svc.cancel_session(s.id)
        assert cancelled.status == "cancelled"

    def test_cancel_from_done_status(self, svc, sample_project, today):
        s = svc.create_session(sample_project.id, today)
        svc.complete_session(s.id)
        result = svc.cancel_session(s.id)
        assert result.status == "cancelled"


class TestSessionServiceSetStatus:
    def test_set_status_to_planned(self, svc, sample_project, today):
        s = svc.create_session(sample_project.id, today)
        svc.complete_session(s.id)
        reopened = svc.set_status(s.id, "planned")
        assert reopened.status == "planned"
        assert reopened.completed_at is None

    def test_set_status_cancelled_to_planned(self, svc, sample_project, today):
        s = svc.create_session(sample_project.id, today)
        svc.cancel_session(s.id)
        reopened = svc.set_status(s.id, "planned")
        assert reopened.status == "planned"

    def test_set_status_invalid_raises(self, svc, sample_project, today):
        s = svc.create_session(sample_project.id, today)
        with pytest.raises(ValidationError):
            svc.set_status(s.id, "unknown")


class TestSessionServiceDelete:
    def test_delete_removes_session(self, svc, sample_project, today):
        from portfolio_manager.exceptions import NotFoundError

        s = svc.create_session(sample_project.id, today)
        svc.delete_session(s.id)
        from portfolio_manager.repositories.session_repo import SessionRepository

        repo = SessionRepository(DatabaseConnection.get())
        with pytest.raises(NotFoundError):
            repo.get(s.id)


class TestSessionServiceQuery:
    def test_get_sessions_for_week(self, svc, sample_project, today):
        week_key = to_week_key(today)
        svc.create_session(sample_project.id, today)
        sessions = svc.get_sessions_for_week(week_key)
        assert len(sessions) >= 1

    def test_get_sessions_for_project(self, svc, sample_project, today):
        svc.create_session(sample_project.id, today)
        sessions = svc.get_sessions_for_project(sample_project.id)
        assert len(sessions) >= 1
