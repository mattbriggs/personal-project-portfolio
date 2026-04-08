"""Integration tests for ScoreRepository and ScoringService."""

from datetime import date

import pytest

from portfolio_manager.models.score import ProjectScore
from portfolio_manager.repositories.milestone_repo import MilestoneRepository
from portfolio_manager.repositories.score_repo import ScoreRepository
from portfolio_manager.repositories.session_repo import SessionRepository
from portfolio_manager.services.scoring_service import ScoringService, score_to_status
from portfolio_manager.utils.date_utils import to_week_key


@pytest.fixture
def score_repo(in_memory_db):
    return ScoreRepository(in_memory_db)


@pytest.fixture
def scoring_svc(in_memory_db):
    return ScoringService(
        session_repo=SessionRepository(in_memory_db),
        milestone_repo=MilestoneRepository(in_memory_db),
        score_repo=ScoreRepository(in_memory_db),
    )


class TestScoreRepository:
    def test_upsert_creates_record(self, score_repo, sample_project):
        week_key = to_week_key(date.today())
        ps = ProjectScore(
            project_id=sample_project.id,
            week_key=week_key,
            score=75,
            status="yellow",
        )
        saved = score_repo.upsert(ps)
        assert saved.score == 75

    def test_upsert_replaces_existing(self, score_repo, sample_project):
        week_key = to_week_key(date.today())
        ps = ProjectScore(project_id=sample_project.id, week_key=week_key, score=50, status="red")
        score_repo.upsert(ps)
        ps2 = ProjectScore(project_id=sample_project.id, week_key=week_key, score=90, status="green")
        score_repo.upsert(ps2)
        fetched = score_repo.get_for_week(sample_project.id, week_key)
        assert fetched is not None
        assert fetched.score == 90

    def test_get_for_week_returns_none_when_absent(self, score_repo, sample_project):
        result = score_repo.get_for_week(sample_project.id, "2020.1")
        assert result is None

    def test_list_for_project(self, score_repo, sample_project):
        score_repo.upsert(ProjectScore(project_id=sample_project.id, week_key="2026.10", score=80, status="green"))
        score_repo.upsert(ProjectScore(project_id=sample_project.id, week_key="2026.11", score=60, status="yellow"))
        records = score_repo.list_for_project(sample_project.id)
        assert len(records) == 2

    def test_list_for_week(self, score_repo, sample_project):
        week_key = "2026.15"
        score_repo.upsert(ProjectScore(project_id=sample_project.id, week_key=week_key, score=70, status="yellow"))
        records = score_repo.list_for_week(week_key)
        assert any(r.project_id == sample_project.id for r in records)


class TestScoringService:
    def test_compute_and_save_returns_score(self, scoring_svc, sample_project, sample_sessions):
        week_key = sample_sessions[0].week_key
        ps = scoring_svc.compute_and_save(sample_project.id, week_key)
        assert 0 <= ps.score <= 100
        assert ps.status in ("green", "yellow", "red")

    def test_compute_skips_manual_override(self, scoring_svc, sample_project):
        week_key = to_week_key(date.today())
        # Set a manual override
        scoring_svc.manual_override(
            project_id=sample_project.id,
            week_key=week_key,
            score=99,
            status="green",
            reason="Manual test override",
        )
        # compute_and_save should leave the override untouched
        ps = scoring_svc.compute_and_save(sample_project.id, week_key)
        assert ps.score == 99
        assert ps.is_manual_override is True

    def test_manual_override_sets_flag(self, scoring_svc, sample_project):
        week_key = to_week_key(date.today())
        ps = scoring_svc.manual_override(
            project_id=sample_project.id,
            week_key=week_key,
            score=42,
            status="red",
            reason="Testing override",
        )
        assert ps.is_manual_override is True
        assert ps.override_reason == "Testing override"

    def test_portfolio_score_returns_zero_with_no_scores(self, scoring_svc):
        assert scoring_svc.portfolio_score("2000.1") == 0

    def test_portfolio_score_averages(self, scoring_svc, sample_project):
        from portfolio_manager.repositories.score_repo import ScoreRepository
        from portfolio_manager.db.connection import DatabaseConnection
        sr = ScoreRepository(DatabaseConnection.get())
        week_key = "2026.15"
        sr.upsert(ProjectScore(project_id=sample_project.id, week_key=week_key, score=80, status="green"))
        avg = scoring_svc.portfolio_score(week_key)
        assert avg == 80
