"""Service tests for :class:`SessionService`."""

from datetime import date

import pytest

from portfolio_manager.application.services.project_service import ProjectService
from portfolio_manager.application.services.session_service import SessionService
from portfolio_manager.domain.errors import ArchivedProjectError, ValidationError
from portfolio_manager.domain.models import Milestone


@pytest.fixture
def project(uow):
    return ProjectService(uow.projects).create_project(name="Proj")


@pytest.fixture
def service(uow, frozen_clock) -> SessionService:
    return SessionService(uow.sessions, uow.projects, uow.milestones, frozen_clock)


def test_create_derives_week_key(service: SessionService, project) -> None:
    s = service.create_session(project.id, date(2026, 4, 7))
    assert s.week_key == "2026.15"


def test_duration_bounds(service: SessionService, project) -> None:
    with pytest.raises(ValidationError):
        service.create_session(project.id, date(2026, 4, 7), duration_minutes=10)
    with pytest.raises(ValidationError):
        service.create_session(project.id, date(2026, 4, 7), duration_minutes=500)


def test_entering_done_sets_completed_at(service: SessionService, project, frozen_clock) -> None:
    s = service.create_session(project.id, date(2026, 4, 7), status="planned")
    done = service.set_status(s.id, "done")
    assert done.completed_at == frozen_clock.now()


def test_leaving_done_clears_completed_at(service: SessionService, project) -> None:
    s = service.create_session(project.id, date(2026, 4, 7), status="done")
    reopened = service.set_status(s.id, "planned")
    assert reopened.completed_at is None


def test_reschedule_recomputes_week_key(service: SessionService, project) -> None:
    s = service.create_session(project.id, date(2026, 4, 7))
    moved = service.reschedule_session(s.id, date(2026, 4, 14))
    assert moved.week_key == "2026.16"


def test_archived_project_blocks_session_create(uow, service: SessionService, project) -> None:
    ProjectService(uow.projects).archive_project(project.id)
    with pytest.raises(ArchivedProjectError):
        service.create_session(project.id, date(2026, 4, 7))


def test_milestone_must_belong_to_project(uow, service: SessionService, project) -> None:
    other = ProjectService(uow.projects).create_project(name="Other")
    m = uow.milestones.create(Milestone(project_id=other.id, description="m"))
    with pytest.raises(ValidationError):
        service.create_session(project.id, date(2026, 4, 7), milestone_id=m.id)
