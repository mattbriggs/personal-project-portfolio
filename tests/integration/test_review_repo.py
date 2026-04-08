"""Integration tests for ReviewRepository."""

from datetime import date

import pytest

from portfolio_manager.models.review import WeeklyReview
from portfolio_manager.repositories.review_repo import ReviewRepository
from portfolio_manager.utils.date_utils import week_key_to_date_range


@pytest.fixture
def repo(in_memory_db):
    return ReviewRepository(in_memory_db)


def _make_review(week_key: str = "2026.15") -> WeeklyReview:
    monday, sunday = week_key_to_date_range(week_key)
    return WeeklyReview(
        week_key=week_key,
        date_from=monday,
        date_to=sunday,
        what_moved="Finished outline.",
        what_stalled="Chapter 2 stuck.",
        primary_focus="Novel",
    )


class TestReviewRepositoryUpsert:
    def test_upsert_creates_record(self, repo):
        review = repo.upsert(_make_review("2026.15"))
        assert review.id > 0

    def test_upsert_updates_existing(self, repo):
        repo.upsert(_make_review("2026.15"))
        updated = _make_review("2026.15")
        updated.what_moved = "Shipped chapter 1."
        repo.upsert(updated)
        fetched = repo.get_for_week("2026.15")
        assert fetched is not None
        assert fetched.what_moved == "Shipped chapter 1."

    def test_upsert_persists_date_range(self, repo):
        repo.upsert(_make_review("2026.15"))
        fetched = repo.get_for_week("2026.15")
        assert fetched is not None
        assert fetched.date_from == date(2026, 4, 6)
        assert fetched.date_to == date(2026, 4, 12)


class TestReviewRepositoryGet:
    def test_get_missing_returns_none(self, repo):
        assert repo.get_for_week("2000.1") is None

    def test_get_existing(self, repo):
        repo.upsert(_make_review("2026.15"))
        fetched = repo.get_for_week("2026.15")
        assert fetched is not None
        assert fetched.week_key == "2026.15"


class TestReviewRepositoryListAll:
    def test_list_all_returns_most_recent_first(self, repo):
        repo.upsert(_make_review("2026.10"))
        repo.upsert(_make_review("2026.15"))
        repo.upsert(_make_review("2026.12"))
        reviews = repo.list_all()
        week_keys = [r.week_key for r in reviews]
        assert week_keys == sorted(week_keys, reverse=True)

    def test_list_all_empty(self, repo):
        assert repo.list_all() == []
