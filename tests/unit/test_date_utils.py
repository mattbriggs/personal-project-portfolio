"""Unit tests for date utility functions."""

from datetime import date

import pytest

from portfolio_manager.utils.date_utils import (
    parse_week_key,
    to_week_key,
    week_key_to_date_range,
)


class TestToWeekKey:
    def test_known_date(self):
        # 2026-04-07 is Tuesday of week 15 in ISO 2026
        assert to_week_key(date(2026, 4, 7)) == "2026.15"

    def test_monday_of_week(self):
        # 2026-04-06 is Monday of week 15
        assert to_week_key(date(2026, 4, 6)) == "2026.15"

    def test_sunday_of_week(self):
        # 2026-04-12 is Sunday of week 15
        assert to_week_key(date(2026, 4, 12)) == "2026.15"

    def test_iso_year_boundary(self):
        # 2015-12-31 is in ISO week 53 of 2015
        key = to_week_key(date(2015, 12, 31))
        assert key == "2015.53"


class TestWeekKeyToDateRange:
    def test_week_15_2026(self):
        monday, sunday = week_key_to_date_range("2026.15")
        assert monday == date(2026, 4, 6)
        assert sunday == date(2026, 4, 12)
        assert monday.weekday() == 0  # Monday
        assert sunday.weekday() == 6  # Sunday

    def test_invalid_format(self):
        with pytest.raises(ValueError, match="Invalid week key"):
            week_key_to_date_range("2026-15")

    def test_roundtrip(self):
        d = date(2026, 4, 7)
        wk = to_week_key(d)
        monday, sunday = week_key_to_date_range(wk)
        assert monday <= d <= sunday


class TestParseWeekKey:
    def test_parses_correctly(self):
        year, week = parse_week_key("2026.15")
        assert year == 2026
        assert week == 15

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            parse_week_key("bad")
