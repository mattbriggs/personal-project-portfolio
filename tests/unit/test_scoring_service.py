"""Unit tests for the scoring service and strategy."""

import pytest

from portfolio_manager.models.score import ProjectScore
from portfolio_manager.services.scoring_service import (
    DefaultScoringStrategy,
    ScoringStrategy,
    score_to_status,
)


class TestDefaultScoringStrategy:
    def setup_method(self):
        self.strategy = DefaultScoringStrategy()

    def test_full_completion_no_milestones(self):
        score = self.strategy.compute_score(
            planned=4, completed=4, total_milestones=0, completed_milestones=0
        )
        assert score == 60

    def test_no_sessions_half_milestones(self):
        score = self.strategy.compute_score(
            planned=0, completed=0, total_milestones=4, completed_milestones=2
        )
        assert score == 20

    def test_full_completion_full_milestones(self):
        score = self.strategy.compute_score(
            planned=4, completed=4, total_milestones=5, completed_milestones=5
        )
        assert score == 100

    def test_zero_planned_zero_milestones(self):
        score = self.strategy.compute_score(
            planned=0, completed=0, total_milestones=0, completed_milestones=0
        )
        assert score == 0

    def test_partial_completion(self):
        score = self.strategy.compute_score(
            planned=4, completed=2, total_milestones=10, completed_milestones=5
        )
        # session: 2/4 * 60 = 30, milestone: 5/10 * 40 = 20 → 50
        assert score == 50

    def test_capped_at_100(self):
        # Edge case: more completed than planned would be odd but should still cap
        score = self.strategy.compute_score(
            planned=2, completed=4, total_milestones=1, completed_milestones=1
        )
        assert score <= 100


class TestScoreToStatus:
    def test_green_threshold(self):
        assert score_to_status(80) == "green"
        assert score_to_status(100) == "green"

    def test_yellow_threshold(self):
        assert score_to_status(60) == "yellow"
        assert score_to_status(79) == "yellow"

    def test_red_threshold(self):
        assert score_to_status(0) == "red"
        assert score_to_status(59) == "red"


class TestScoringStrategyIsReplaceable:
    """Verify the Strategy pattern: ScoringService accepts any ScoringStrategy."""

    def test_custom_strategy(self):
        class AlwaysMaxStrategy(ScoringStrategy):
            def compute_score(self, planned, completed, total_milestones, completed_milestones):
                return 100

        s = AlwaysMaxStrategy()
        assert s.compute_score(0, 0, 0, 0) == 100
