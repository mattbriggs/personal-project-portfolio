"""FastAPI dependency providers.

The composition happens once in :func:`portfolio_manager.api.app.create_app`,
which stores the :class:`Container` in ``app.state``. These providers expose the
individual services to route handlers.
"""

from fastapi import Request

from portfolio_manager.application.services.dashboard_service import DashboardService
from portfolio_manager.application.services.milestone_service import MilestoneService
from portfolio_manager.application.services.plan_service import PlanService
from portfolio_manager.application.services.project_service import ProjectService
from portfolio_manager.application.services.review_service import ReviewService
from portfolio_manager.application.services.scoring_service import ScoringService
from portfolio_manager.application.services.session_service import SessionService
from portfolio_manager.application.services.settings_service import SettingsService
from portfolio_manager.bootstrap import Container


def get_container(request: Request) -> Container:
    """Return the application container from ``app.state``.

    :rtype: Container
    """
    return request.app.state.container


def get_projects(request: Request) -> ProjectService:
    """Provide the project service.

    :rtype: ProjectService
    """
    return get_container(request).projects


def get_sessions(request: Request) -> SessionService:
    """Provide the session service.

    :rtype: SessionService
    """
    return get_container(request).sessions


def get_milestones(request: Request) -> MilestoneService:
    """Provide the milestone service.

    :rtype: MilestoneService
    """
    return get_container(request).milestones


def get_reviews(request: Request) -> ReviewService:
    """Provide the review service.

    :rtype: ReviewService
    """
    return get_container(request).reviews


def get_scoring(request: Request) -> ScoringService:
    """Provide the scoring service.

    :rtype: ScoringService
    """
    return get_container(request).scoring


def get_dashboard(request: Request) -> DashboardService:
    """Provide the dashboard service.

    :rtype: DashboardService
    """
    return get_container(request).dashboard


def get_plans(request: Request) -> PlanService:
    """Provide the plan service.

    :rtype: PlanService
    """
    return get_container(request).plans


def get_settings_service(request: Request) -> SettingsService:
    """Provide the settings service.

    :rtype: SettingsService
    """
    return get_container(request).settings
