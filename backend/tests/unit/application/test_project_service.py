"""Service tests for :class:`ProjectService`."""

import pytest

from portfolio_manager.application.services.project_service import ProjectService
from portfolio_manager.domain.errors import (
    ArchivedProjectError,
    ConflictError,
    ValidationError,
)


@pytest.fixture
def service(uow) -> ProjectService:
    return ProjectService(uow.projects)


def test_create_rejects_empty_name(service: ProjectService) -> None:
    with pytest.raises(ValidationError):
        service.create_project(name="   ")


def test_create_rejects_out_of_range_priority(service: ProjectService) -> None:
    with pytest.raises(ValidationError):
        service.create_project(name="Ok", priority=6)


def test_create_generates_slug(service: ProjectService) -> None:
    p = service.create_project(name="My Novel")
    assert p.slug == "my-novel"
    assert p.id > 0


def test_duplicate_slug_rejected_as_conflict(service: ProjectService) -> None:
    service.create_project(name="My Novel")
    with pytest.raises(ConflictError):
        service.create_project(name="My Novel")


def test_archived_project_is_read_only(service: ProjectService) -> None:
    p = service.create_project(name="Thing")
    service.archive_project(p.id)
    p.name = "Renamed"
    with pytest.raises(ArchivedProjectError):
        service.update_project(p)


def test_archive_preserves_record(service: ProjectService) -> None:
    p = service.create_project(name="Thing")
    archived = service.archive_project(p.id)
    assert archived.status == "archive"
    assert service.get_project(p.id).status == "archive"


def test_delete_removes_project(service: ProjectService) -> None:
    p = service.create_project(name="Gone")
    service.delete_project(p.id)
    assert service.list_projects(status=None) == []
