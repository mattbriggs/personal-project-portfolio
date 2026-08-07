"""Weekly review routes under ``/api/v1``."""

from fastapi import APIRouter, Depends

from portfolio_manager.api.dependencies import get_reviews
from portfolio_manager.application.services.review_service import ReviewService
from portfolio_manager.contracts.reviews import (
    ReviewListResponse,
    ReviewResponse,
    ReviewSaveRequest,
)
from portfolio_manager.domain.models import WeeklyReview

router = APIRouter(prefix="/api/v1", tags=["reviews"])


@router.get("/reviews", response_model=ReviewListResponse)
async def list_reviews(
    reviews: ReviewService = Depends(get_reviews),
) -> ReviewListResponse:
    """List all weekly reviews, most recent first."""
    items = reviews.list_reviews()
    return ReviewListResponse(reviews=[ReviewResponse.from_domain(r) for r in items])


@router.get("/reviews/{week_key}", response_model=ReviewResponse)
async def get_or_create_review(
    week_key: str, reviews: ReviewService = Depends(get_reviews)
) -> ReviewResponse:
    """Return the review for *week_key*, or a transient blank one if absent."""
    return ReviewResponse.from_domain(reviews.get_or_create(week_key))


@router.put("/reviews/{week_key}", response_model=ReviewResponse)
async def save_review(
    week_key: str,
    body: ReviewSaveRequest,
    reviews: ReviewService = Depends(get_reviews),
) -> ReviewResponse:
    """Persist a weekly review for *week_key*."""
    existing = reviews.get_or_create(week_key)
    review = WeeklyReview(
        id=existing.id,
        week_key=week_key,
        hours_invested=body.hours_invested,
        sessions_completed=body.sessions_completed,
        what_moved=body.what_moved,
        what_stalled=body.what_stalled,
        signals=body.signals,
        decision_next_week=body.decision_next_week,
        primary_focus=body.primary_focus,
        project_to_deprioritize=body.project_to_deprioritize,
        risk_to_watch=body.risk_to_watch,
        first_session_target=body.first_session_target,
        written_to_repo=body.written_to_repo,
    )
    return ReviewResponse.from_domain(reviews.save(review))
