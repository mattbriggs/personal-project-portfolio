"""Dashboard route under ``/api/v1``."""

from fastapi import APIRouter, Depends

from portfolio_manager.api.dependencies import get_dashboard
from portfolio_manager.application.services.dashboard_service import DashboardService
from portfolio_manager.contracts.dashboard import DashboardResponse

router = APIRouter(prefix="/api/v1", tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard_view(
    week_key: str | None = None,
    dashboard: DashboardService = Depends(get_dashboard),
) -> DashboardResponse:
    """Return the aggregate dashboard for a week (defaults to the current week)."""
    return DashboardResponse.from_domain(dashboard.get_dashboard(week_key))
