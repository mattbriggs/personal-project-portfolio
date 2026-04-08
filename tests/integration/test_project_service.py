"""Integration tests for ProjectService with real repositories."""

import pytest

from portfolio_manager.events.event_bus import EventBus
from portfolio_manager.exceptions import (
    NotFoundError,
    ProjectStateError,
    ValidationError,
)
from portfolio_manager.repositories.project_repo import ProjectRepository
from portfolio_manager.services.project_service import ProjectService


@pytest.fixture
def svc(in_memory_db):
    repo = ProjectRepository(in_memory_db)
    bus = EventBus.get()
    return ProjectService(repo, bus)


class TestProjectServiceCreate:
    def test_create_returns_project_with_id(self, svc):
        p = svc.create_project("My Novel")
        assert p.id > 0
        assert p.name == "My Novel"

    def test_create_generates_slug(self, svc):
        p = svc.create_project("My Great Novel!")
        assert p.slug == "my-great-novel"

    def test_create_empty_name_raises(self, svc):
        with pytest.raises(ValidationError):
            svc.create_project("")

    def test_create_invalid_priority_raises(self, svc):
        with pytest.raises(ValidationError):
            svc.create_project("Novel", priority=6)

    def test_create_emits_event(self, svc):
        received = []
        EventBus.get().subscribe("PROJECT_CREATED", lambda **kw: received.append(kw))
        svc.create_project("Event Novel")
        assert len(received) == 1
        assert "project_id" in received[0]


class TestProjectServiceArchive:
    def test_archive_sets_status(self, svc):
        p = svc.create_project("To Archive")
        archived = svc.archive_project(p.id)
        assert archived.status == "archive"

    def test_update_archived_raises(self, svc):
        p = svc.create_project("Archived Project")
        svc.archive_project(p.id)
        archived = svc.get_project(p.id)
        with pytest.raises(ProjectStateError):
            svc.update_project(archived)


class TestProjectServiceDelete:
    def test_delete_removes_project(self, svc):
        p = svc.create_project("To Delete")
        svc.delete_project(p.id)
        with pytest.raises(NotFoundError):
            svc.get_project(p.id)

    def test_delete_emits_event(self, svc):
        received = []
        EventBus.get().subscribe("PROJECT_DELETED", lambda **kw: received.append(kw))
        p = svc.create_project("Delete Me")
        svc.delete_project(p.id)
        assert len(received) == 1


class TestProjectServiceList:
    def test_list_active_only_by_default(self, svc):
        svc.create_project("Active")
        archived = svc.create_project("Archived")
        svc.archive_project(archived.id)
        active = svc.list_projects(status="active")
        assert all(p.status == "active" for p in active)

    def test_list_all_returns_all(self, svc):
        svc.create_project("Active")
        svc.create_project("Backlog", status="backlog")
        all_projects = svc.list_projects(status=None)
        assert len(all_projects) >= 2
