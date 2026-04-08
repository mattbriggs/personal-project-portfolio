"""Integration tests for MilestoneRepository."""

from datetime import date

import pytest

from portfolio_manager.exceptions import NotFoundError
from portfolio_manager.models.milestone import Milestone
from portfolio_manager.repositories.milestone_repo import MilestoneRepository


@pytest.fixture
def repo(in_memory_db):
    return MilestoneRepository(in_memory_db)


@pytest.fixture
def a_milestone(repo, sample_project):
    return repo.create(
        Milestone(
            project_id=sample_project.id,
            description="Ship chapter 1",
            sort_order=1,
        )
    )


class TestMilestoneRepositoryCreate:
    def test_create_assigns_id(self, repo, sample_project):
        ms = repo.create(
            Milestone(project_id=sample_project.id, description="Ship v1")
        )
        assert ms.id > 0

    def test_create_persists_description(self, repo, a_milestone):
        fetched = repo.get(a_milestone.id)
        assert fetched.description == "Ship chapter 1"


class TestMilestoneRepositoryToggle:
    def test_toggle_updates_is_complete(self, repo, a_milestone):
        a_milestone.toggle()
        updated = repo.update(a_milestone)
        assert updated.is_complete is True
        assert updated.completed_date == date.today()

    def test_double_toggle_restores(self, repo, a_milestone):
        a_milestone.toggle()
        repo.update(a_milestone)
        a_milestone.toggle()
        updated = repo.update(a_milestone)
        assert updated.is_complete is False
        assert updated.completed_date is None


class TestMilestoneRepositoryCount:
    def test_count_zero_initially(self, repo, sample_project):
        total, completed = repo.count(sample_project.id)
        assert total == 0
        assert completed == 0

    def test_count_with_milestones(self, repo, sample_project):
        ms1 = repo.create(Milestone(project_id=sample_project.id, description="M1"))
        ms2 = repo.create(Milestone(project_id=sample_project.id, description="M2"))
        ms1.is_complete = True
        ms1.completed_date = date.today()
        repo.update(ms1)

        total, completed = repo.count(sample_project.id)
        assert total == 2
        assert completed == 1


class TestMilestoneRepositoryDelete:
    def test_delete_removes(self, repo, a_milestone):
        repo.delete(a_milestone.id)
        with pytest.raises(NotFoundError):
            repo.get(a_milestone.id)
