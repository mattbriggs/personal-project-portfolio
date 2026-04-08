"""Unit tests for domain model dataclasses."""

from datetime import date

from portfolio_manager.models.milestone import Milestone
from portfolio_manager.models.project import Project
from portfolio_manager.models.review import WeeklyReview
from portfolio_manager.models.score import ProjectScore
from portfolio_manager.models.session import Session


class TestProject:
    def test_defaults(self):
        p = Project(name="Test", slug="test")
        assert p.status == "active"
        assert p.priority == 3
        assert p.owner == "Matt Briggs"
        assert p.plan_content == ""

    def test_is_archived_false_for_active(self):
        p = Project(name="A", slug="a", status="active")
        assert not p.is_archived()

    def test_is_archived_true(self):
        p = Project(name="A", slug="a", status="archive")
        assert p.is_archived()

    def test_str_contains_name(self):
        p = Project(id=1, name="My Project", slug="my-project", status="active")
        assert "My Project" in str(p)


class TestSession:
    def test_defaults(self):
        s = Session(project_id=1)
        assert s.status == "planned"
        assert s.duration_minutes == 90

    def test_is_completed(self):
        s = Session(project_id=1, status="completed")
        assert s.is_completed()
        assert not s.is_planned()

    def test_is_planned(self):
        s = Session(project_id=1, status="planned")
        assert s.is_planned()
        assert not s.is_completed()


class TestMilestone:
    def test_toggle_marks_complete(self):
        ms = Milestone(project_id=1, description="Ship v1")
        assert not ms.is_complete
        ms.toggle()
        assert ms.is_complete
        assert ms.completed_date == date.today()

    def test_toggle_clears_completion(self):
        ms = Milestone(
            project_id=1,
            description="Ship v1",
            is_complete=True,
            completed_date=date.today(),
        )
        ms.toggle()
        assert not ms.is_complete
        assert ms.completed_date is None

    def test_str_contains_description(self):
        ms = Milestone(description="Launch")
        assert "Launch" in str(ms)


class TestProjectScore:
    def test_defaults(self):
        ps = ProjectScore()
        assert ps.score == 0
        assert ps.status == "red"
        assert not ps.is_manual_override

    def test_manual_override_str(self):
        ps = ProjectScore(is_manual_override=True)
        assert "[manual]" in str(ps)


class TestWeeklyReview:
    def test_defaults(self):
        wr = WeeklyReview()
        assert wr.hours_invested == 0.0
        assert wr.sessions_completed == 0
        assert not wr.written_to_repo

    def test_str(self):
        wr = WeeklyReview(week_key="2026.15")
        assert "2026.15" in str(wr)
