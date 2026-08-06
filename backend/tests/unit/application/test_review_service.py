"""Service tests for :class:`ReviewService`."""

from datetime import date

import pytest

from portfolio_manager.application.services.review_service import ReviewService
from portfolio_manager.domain.errors import ValidationError


@pytest.fixture
def service(uow) -> ReviewService:
    return ReviewService(uow.reviews)


def test_get_or_create_returns_transient_blank(service: ReviewService, uow) -> None:
    review = service.get_or_create("2026.15")
    assert review.id == 0  # not persisted
    assert review.date_from == date(2026, 4, 6)
    assert review.date_to == date(2026, 4, 12)
    assert uow.reviews.get_for_week("2026.15") is None


def test_save_persists_and_derives_range(service: ReviewService) -> None:
    review = service.get_or_create("2026.15")
    review.what_moved = "chapter 1"
    saved = service.save(review)
    assert saved.id > 0
    assert saved.date_from == date(2026, 4, 6)


def test_invalid_week_key_rejected(service: ReviewService) -> None:
    with pytest.raises(ValidationError):
        service.get_or_create("nope")


def test_list_orders_most_recent_first(service: ReviewService) -> None:
    for wk in ("2026.14", "2026.16", "2026.15"):
        r = service.get_or_create(wk)
        service.save(r)
    keys = [r.week_key for r in service.list_reviews()]
    assert keys == ["2026.16", "2026.15", "2026.14"]
