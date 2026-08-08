"""Score routes under ``/api/v1``."""

from fastapi import APIRouter, Depends

from portfolio_manager.api.dependencies import get_scoring
from portfolio_manager.application.services.scoring_service import ScoringService
from portfolio_manager.contracts.scores import ScoreOverrideRequest, ScoreResponse

router = APIRouter(prefix="/api/v1", tags=["scores"])


@router.post("/scores/override", response_model=ScoreResponse)
async def override_score(
    body: ScoreOverrideRequest,
    scoring: ScoringService = Depends(get_scoring),
) -> ScoreResponse:
    """Persist a manual score override (requires a non-empty reason)."""
    score = scoring.manual_override(
        project_id=body.project_id,
        week_key=body.week_key,
        score=body.score,
        status=body.status,
        reason=body.reason,
        status_note=body.status_note,
    )
    return ScoreResponse.from_domain(score)
