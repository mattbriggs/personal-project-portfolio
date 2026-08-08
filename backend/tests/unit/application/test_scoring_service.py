"""Service tests for :class:`ScoringService`."""

from datetime import date

import pytest

from portfolio_manager.application.services.project_service import ProjectService
from portfolio_manager.application.services.scoring_service import ScoringService
from portfolio_manager.application.services.session_service import SessionService
from portfolio_manager.domain.errors import ValidationError


@pytest.fixture
def project(uow):
    return ProjectService(uow.projects).create_project(name="Proj")


@pytest.fixture
def scoring(uow) -> ScoringService:
    return ScoringService(uow.sessions, uow.milestones, uow.scores)


def test_manual_override_requires_reason(scoring: ScoringService, project) -> None:
    with pytest.raises(ValidationError):
        scoring.manual_override(project.id, "2026.15", 50, "yellow", reason="")


def test_manual_override_blocks_recompute(uow, scoring: ScoringService, project) -> None:
    scoring.manual_override(project.id, "2026.15", 90, "green", reason="on track")
    sessions = SessionService(uow.sessions, uow.projects, uow.milestones)
    sessions.create_session(project.id, date(2026, 4, 7), status="planned")
    result = scoring.compute_and_save(project.id, "2026.15")
    assert result.is_manual_override is True
    assert result.score == 90


def test_portfolio_score_zero_when_no_scores(scoring: ScoringService) -> None:
    assert scoring.portfolio_score("2026.15") == 0


def test_compute_uses_committed_sessions(uow, scoring: ScoringService, project) -> None:
    sessions = SessionService(uow.sessions, uow.projects, uow.milestones)
    sessions.create_session(project.id, date(2026, 4, 7), status="planned")
    sessions.create_session(project.id, date(2026, 4, 7), status="done")
    # 1 done / 2 committed -> 30 (no milestones).
    score = scoring.compute_and_save(project.id, "2026.15")
    assert score.score == 30
    assert score.status == "red"
