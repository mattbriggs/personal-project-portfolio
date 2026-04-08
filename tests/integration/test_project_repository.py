"""Integration tests for ProjectRepository using an in-memory SQLite database."""

from datetime import date

import pytest

from portfolio_manager.db.connection import DatabaseConnection
from portfolio_manager.exceptions import NotFoundError
from portfolio_manager.models.project import Project
from portfolio_manager.repositories.project_repo import ProjectRepository


@pytest.fixture
def repo(in_memory_db):
    return ProjectRepository(in_memory_db)


class TestProjectRepositoryCreate:
    def test_create_assigns_id(self, repo):
        p = repo.create(Project(name="Novel", slug="novel", status="active"))
        assert p.id > 0

    def test_create_persists_name(self, repo):
        repo.create(Project(name="Blog", slug="blog", status="active"))
        fetched = repo.list()
        assert any(p.name == "Blog" for p in fetched)

    def test_create_with_started_date(self, repo):
        p = repo.create(
            Project(
                name="Art",
                slug="art",
                status="active",
                started_date=date(2026, 1, 1),
            )
        )
        fetched = repo.get(p.id)
        assert fetched.started_date == date(2026, 1, 1)


class TestProjectRepositoryGet:
    def test_get_existing(self, repo, sample_project):
        fetched = repo.get(sample_project.id)
        assert fetched.name == sample_project.name

    def test_get_missing_raises(self, repo):
        with pytest.raises(NotFoundError):
            repo.get(9999)


class TestProjectRepositoryList:
    def test_list_filters_by_status(self, repo, sample_project):
        repo.create(Project(name="Archived", slug="archived", status="archive"))
        active = repo.list(status="active")
        assert all(p.status == "active" for p in active)

    def test_list_all_returns_all(self, repo, sample_project):
        repo.create(Project(name="Backlog Item", slug="backlog-item", status="backlog"))
        all_projects = repo.list(status=None)
        assert len(all_projects) >= 2

    def test_list_ordered_by_priority(self, repo):
        repo.create(Project(name="Low", slug="low", status="active", priority=5))
        repo.create(Project(name="High", slug="high", status="active", priority=1))
        projects = repo.list(status="active")
        priorities = [p.priority for p in projects]
        assert priorities == sorted(priorities)


class TestProjectRepositoryUpdate:
    def test_update_changes_name(self, repo, sample_project):
        sample_project.name = "Updated Novel"
        updated = repo.update(sample_project)
        assert updated.name == "Updated Novel"

    def test_update_plan(self, repo, sample_project):
        repo.update_plan(sample_project.id, "# New Plan\n")
        fetched = repo.get(sample_project.id)
        assert fetched.plan_content == "# New Plan\n"


class TestProjectRepositoryDelete:
    def test_delete_removes_project(self, repo, sample_project):
        repo.delete(sample_project.id)
        with pytest.raises(NotFoundError):
            repo.get(sample_project.id)

    def test_delete_missing_raises(self, repo):
        with pytest.raises(NotFoundError):
            repo.delete(9999)
