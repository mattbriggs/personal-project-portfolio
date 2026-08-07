"""Service tests for :class:`MilestoneService`."""

import pytest

from portfolio_manager.application.services.milestone_service import MilestoneService
from portfolio_manager.application.services.project_service import ProjectService
from portfolio_manager.domain.errors import ValidationError


@pytest.fixture
def project(uow):
    return ProjectService(uow.projects).create_project(name="Proj")


@pytest.fixture
def service(uow, frozen_clock) -> MilestoneService:
    return MilestoneService(uow.milestones, uow.projects, frozen_clock)


def test_description_required(service: MilestoneService, project) -> None:
    with pytest.raises(ValidationError):
        service.create_milestone(project.id, description="  ")


def test_entering_done_sets_completed_date(
    service: MilestoneService, project, frozen_clock
) -> None:
    m = service.create_milestone(project.id, "Ship it")
    done = service.set_status(m.id, "done")
    assert done.completed_date == frozen_clock.today()


def test_leaving_done_clears_completed_date(service: MilestoneService, project) -> None:
    m = service.create_milestone(project.id, "Ship it", status="done")
    reopened = service.set_status(m.id, "doing")
    assert reopened.completed_date is None


def test_listing_is_ordered(service: MilestoneService, project) -> None:
    service.create_milestone(project.id, "B", sort_order=2)
    service.create_milestone(project.id, "A", sort_order=1)
    ordered = [m.description for m, _ in service.list_for_project(project.id)]
    assert ordered == ["A", "B"]
