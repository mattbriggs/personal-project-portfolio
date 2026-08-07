"""Domain unit tests for the scoring policy and status mapping."""

import pytest

from portfolio_manager.domain.scoring import DefaultScoringStrategy, score_to_status

strategy = DefaultScoringStrategy()


def test_full_session_and_milestone_completion_caps_at_100() -> None:
    assert strategy.compute_score(10, 10, 5, 5) == 100


def test_zero_denominators_yield_zero() -> None:
    assert strategy.compute_score(0, 0, 0, 0) == 0


def test_session_only_component() -> None:
    # 5/10 sessions -> 30; no milestones -> 0.
    assert strategy.compute_score(10, 5, 0, 0) == 30


def test_milestone_only_component() -> None:
    # no sessions -> 0; 2/4 milestones -> 20.
    assert strategy.compute_score(0, 0, 4, 2) == 20


def test_rounding() -> None:
    # 1/3 sessions -> 20; 1/3 milestones -> 13.33 -> total 33.33 -> 33.
    assert strategy.compute_score(3, 1, 3, 1) == 33


@pytest.mark.parametrize(
    ("score", "status"),
    [(0, "red"), (59, "red"), (60, "yellow"), (79, "yellow"), (80, "green"), (100, "green")],
)
def test_score_to_status_boundaries(score: int, status: str) -> None:
    assert score_to_status(score) == status
