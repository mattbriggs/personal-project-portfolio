"""Domain unit tests for ISO week-key calculations."""

from datetime import date

import pytest

from portfolio_manager.domain.week import (
    is_valid_week_key,
    parse_week_key,
    to_week_key,
    week_key_to_date_range,
)


def test_to_week_key_basic() -> None:
    assert to_week_key(date(2026, 4, 7)) == "2026.15"


def test_week_key_to_date_range() -> None:
    monday, sunday = week_key_to_date_range("2026.15")
    assert monday == date(2026, 4, 6)
    assert sunday == date(2026, 4, 12)


def test_year_boundary_week_belongs_to_iso_year() -> None:
    # 2025-12-29 is Monday of ISO week 2026-W01.
    assert to_week_key(date(2025, 12, 29)) == "2026.1"
    # And 2027-01-01 (Friday) is ISO week 2026-W53.
    assert to_week_key(date(2027, 1, 1)) == "2026.53"


def test_week_key_round_trip_for_year_boundary() -> None:
    monday, sunday = week_key_to_date_range("2026.1")
    assert monday == date(2025, 12, 29)
    assert sunday == date(2026, 1, 4)


def test_parse_week_key_invalid() -> None:
    with pytest.raises(ValueError):
        parse_week_key("not-a-week")


@pytest.mark.parametrize(
    ("wk", "expected"),
    [("2026.15", True), ("2026.53", True), ("2026.0", False), ("bad", False)],
)
def test_is_valid_week_key(wk: str, expected: bool) -> None:
    assert is_valid_week_key(wk) is expected
