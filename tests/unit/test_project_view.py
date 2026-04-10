"""Unit tests for project view save helpers."""

from datetime import date

import pytest

from portfolio_manager.models.project import Project
from portfolio_manager.views.project_view import _apply_project_form_values


class TestApplyProjectFormValues:
    def test_uses_latest_plan_content(self) -> None:
        project = Project(id=1, name="Test", slug="test", plan_content="# Old")

        updated = _apply_project_form_values(
            project,
            name="Test",
            description="Desc",
            status="active",
            priority="3",
            raw_start="",
            raw_end="",
            plan_content="# New",
        )

        assert updated.plan_content == "# New"

    def test_parses_dates_and_priority(self) -> None:
        project = Project(id=1, name="Test", slug="test")

        updated = _apply_project_form_values(
            project,
            name=" Renamed ",
            description=" Notes ",
            status="backlog",
            priority="5",
            raw_start="2026-04-01",
            raw_end="2026-04-30",
            plan_content="# Plan",
        )

        assert updated.name == "Renamed"
        assert updated.description == "Notes"
        assert updated.priority == 5
        assert updated.started_date == date(2026, 4, 1)
        assert updated.end_date == date(2026, 4, 30)

    def test_invalid_date_raises_value_error(self) -> None:
        project = Project(id=1, name="Test", slug="test")

        with pytest.raises(ValueError):
            _apply_project_form_values(
                project,
                name="Test",
                description="Desc",
                status="active",
                priority="3",
                raw_start="bad-date",
                raw_end="",
                plan_content="# Plan",
            )
