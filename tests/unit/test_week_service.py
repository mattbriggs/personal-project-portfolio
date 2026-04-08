"""Unit tests for WeekService."""

from datetime import date

import pytest

from portfolio_manager.services.week_service import WeekService


@pytest.fixture
def svc():
    return WeekService()


class TestWeekService:
    def test_current_week_key_format(self, svc):
        key = svc.current_week_key()
        parts = key.split(".")
        assert len(parts) == 2
        assert parts[0].isdigit()
        assert parts[1].isdigit()

    def test_week_key_for_known_date(self, svc):
        assert svc.week_key_for_date(date(2026, 4, 7)) == "2026.15"

    def test_date_range_returns_monday_sunday(self, svc):
        monday, sunday = svc.date_range("2026.15")
        assert monday.weekday() == 0
        assert sunday.weekday() == 6
        assert (sunday - monday).days == 6

    def test_display_range_same_year(self, svc):
        result = svc.display_range("2026.15")
        assert "2026" in result
        assert "–" in result

    def test_display_range_contains_month_names(self, svc):
        result = svc.display_range("2026.15")
        assert "Apr" in result
