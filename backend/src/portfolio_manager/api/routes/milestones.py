"""Milestone routes under ``/api/v1``.

Milestones are listed per project (``/projects/{id}/milestones``) and mutated by
milestone id.
"""

from fastapi import APIRouter, Depends

from portfolio_manager.api.dependencies import get_milestones
from portfolio_manager.application.services.milestone_service import MilestoneService
from portfolio_manager.contracts.common import OkResponse
from portfolio_manager.contracts.milestones import (
    MilestoneCreateRequest,
    MilestoneListResponse,
    MilestoneResponse,
    MilestoneStatusRequest,
    MilestoneUpdateRequest,
)
from portfolio_manager.domain.models import Milestone

router = APIRouter(prefix="/api/v1", tags=["milestones"])


@router.get("/projects/{project_id}/milestones", response_model=MilestoneListResponse)
async def list_milestones(
    project_id: int, milestones: MilestoneService = Depends(get_milestones)
) -> MilestoneListResponse:
    """List a project's milestones (ordered) with session-minute totals."""
    pairs = milestones.list_for_project(project_id)
    return MilestoneListResponse(
        milestones=[MilestoneResponse.from_domain(m, total) for m, total in pairs]
    )


@router.post("/milestones", response_model=MilestoneResponse, status_code=201)
async def create_milestone(
    body: MilestoneCreateRequest,
    milestones: MilestoneService = Depends(get_milestones),
) -> MilestoneResponse:
    """Create a milestone."""
    milestone = milestones.create_milestone(
        project_id=body.project_id,
        description=body.description,
        status=body.status,
        target_date=body.target_date,
        sort_order=body.sort_order,
        notes=body.notes,
    )
    return MilestoneResponse.from_domain(milestone)


@router.get("/milestones/{milestone_id}", response_model=MilestoneResponse)
async def get_milestone(
    milestone_id: int, milestones: MilestoneService = Depends(get_milestones)
) -> MilestoneResponse:
    """Fetch a single milestone."""
    return MilestoneResponse.from_domain(milestones.get_milestone(milestone_id))


@router.put("/milestones/{milestone_id}", response_model=MilestoneResponse)
async def update_milestone(
    milestone_id: int,
    body: MilestoneUpdateRequest,
    milestones: MilestoneService = Depends(get_milestones),
) -> MilestoneResponse:
    """Update a milestone's editable fields."""
    existing = milestones.get_milestone(milestone_id)
    updated = Milestone(
        id=milestone_id,
        project_id=existing.project_id,
        description=body.description,
        status=body.status,
        completed_date=existing.completed_date,
        target_date=body.target_date,
        sort_order=body.sort_order,
        notes=body.notes,
    )
    return MilestoneResponse.from_domain(milestones.update_milestone(updated))


@router.post("/milestones/{milestone_id}/status", response_model=MilestoneResponse)
async def set_status(
    milestone_id: int,
    body: MilestoneStatusRequest,
    milestones: MilestoneService = Depends(get_milestones),
) -> MilestoneResponse:
    """Transition a milestone to a new status."""
    return MilestoneResponse.from_domain(milestones.set_status(milestone_id, body.status))


@router.delete("/milestones/{milestone_id}", response_model=OkResponse)
async def delete_milestone(
    milestone_id: int, milestones: MilestoneService = Depends(get_milestones)
) -> OkResponse:
    """Delete a milestone permanently."""
    milestones.delete_milestone(milestone_id)
    return OkResponse()
