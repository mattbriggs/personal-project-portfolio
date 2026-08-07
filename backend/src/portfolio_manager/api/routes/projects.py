"""Project and plan routes under ``/api/v1``."""

from fastapi import APIRouter, Depends

from portfolio_manager.api.dependencies import get_plans, get_projects
from portfolio_manager.application.services.plan_service import PlanService
from portfolio_manager.application.services.project_service import ProjectService
from portfolio_manager.contracts.common import OkResponse
from portfolio_manager.contracts.plans import PlanResponse, PlanSaveRequest
from portfolio_manager.contracts.projects import (
    ProjectCreateRequest,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdateRequest,
)
from portfolio_manager.domain.enums import ProjectStatus
from portfolio_manager.domain.models import Project

router = APIRouter(prefix="/api/v1", tags=["projects"])


@router.get("/projects", response_model=ProjectListResponse)
async def list_projects(
    status: ProjectStatus | None = None,
    projects: ProjectService = Depends(get_projects),
) -> ProjectListResponse:
    """List projects, optionally filtered by status (``None`` returns all)."""
    items = projects.list_projects(status=status)
    return ProjectListResponse(projects=[ProjectResponse.from_domain(p) for p in items])


@router.post("/projects", response_model=ProjectResponse, status_code=201)
async def create_project(
    body: ProjectCreateRequest,
    projects: ProjectService = Depends(get_projects),
) -> ProjectResponse:
    """Create a project."""
    project = projects.create_project(
        name=body.name,
        status=body.status,
        priority=body.priority,
        description=body.description,
        started_date=body.started_date,
        end_date=body.end_date,
        owner=body.owner,
        review_cadence=body.review_cadence,
    )
    return ProjectResponse.from_domain(project)


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int, projects: ProjectService = Depends(get_projects)
) -> ProjectResponse:
    """Fetch a single project."""
    return ProjectResponse.from_domain(projects.get_project(project_id))


@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    body: ProjectUpdateRequest,
    projects: ProjectService = Depends(get_projects),
) -> ProjectResponse:
    """Update a project's editable fields."""
    existing = projects.get_project(project_id)
    updated = Project(
        id=project_id,
        name=body.name,
        slug=existing.slug,
        status=body.status,
        priority=body.priority,
        description=body.description,
        started_date=body.started_date,
        end_date=body.end_date,
        owner=body.owner,
        review_cadence=body.review_cadence,
        plan_content=existing.plan_content,
    )
    return ProjectResponse.from_domain(projects.update_project(updated))


@router.post("/projects/{project_id}/archive", response_model=ProjectResponse)
async def archive_project(
    project_id: int, projects: ProjectService = Depends(get_projects)
) -> ProjectResponse:
    """Archive a project (makes it read-only)."""
    return ProjectResponse.from_domain(projects.archive_project(project_id))


@router.delete("/projects/{project_id}", response_model=OkResponse)
async def delete_project(
    project_id: int, projects: ProjectService = Depends(get_projects)
) -> OkResponse:
    """Permanently delete a project and its cascaded records."""
    projects.delete_project(project_id)
    return OkResponse()


@router.get("/projects/{project_id}/plan", response_model=PlanResponse)
async def get_plan(project_id: int, plans: PlanService = Depends(get_plans)) -> PlanResponse:
    """Return a project's raw Markdown plan content."""
    return PlanResponse(project_id=project_id, content=plans.get_plan(project_id))


@router.put("/projects/{project_id}/plan", response_model=PlanResponse)
async def save_plan(
    project_id: int,
    body: PlanSaveRequest,
    plans: PlanService = Depends(get_plans),
) -> PlanResponse:
    """Persist a project's Markdown plan content."""
    plans.save_plan(project_id, body.content)
    return PlanResponse(project_id=project_id, content=body.content)
