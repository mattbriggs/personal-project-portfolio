"""Application composition root.

Wires infrastructure adapters and application services into a single container.
This is the only place that knows about concrete SQLite/TOML implementations;
services receive them through constructor injection.

The container also runs pending migrations (with backup) at startup and records
the database path the sidecar actually opened, so settings changes to the path
can report ``restart_required`` without hot-switching the active database.
"""

import logging
from dataclasses import dataclass
from pathlib import Path

from portfolio_manager.application.services.dashboard_service import DashboardService
from portfolio_manager.application.services.milestone_service import MilestoneService
from portfolio_manager.application.services.plan_service import PlanService
from portfolio_manager.application.services.project_service import ProjectService
from portfolio_manager.application.services.review_service import ReviewService
from portfolio_manager.application.services.scoring_service import ScoringService
from portfolio_manager.application.services.session_service import SessionService
from portfolio_manager.application.services.settings_service import SettingsService
from portfolio_manager.infrastructure.config.toml_repository import TomlSettingsRepository
from portfolio_manager.infrastructure.db.connection import DatabaseConnection
from portfolio_manager.infrastructure.db.migrations import run_migrations
from portfolio_manager.infrastructure.db.unit_of_work import SqliteUnitOfWork
from portfolio_manager.infrastructure.system.clock import SystemClock

logger = logging.getLogger(__name__)


@dataclass
class Container:
    """Holds the wired services and runtime metadata.

    :param db: The open database connection.
    :param token: The expected sidecar auth token (empty in tests).
    :param production: Whether production hardening is enabled.
    :param projects: Project service.
    :param sessions: Session service.
    :param milestones: Milestone service.
    :param reviews: Review service.
    :param scoring: Scoring service.
    :param dashboard: Dashboard service.
    :param plans: Plan service.
    :param settings: Settings service.
    """

    db: DatabaseConnection
    token: str
    production: bool
    projects: ProjectService
    sessions: SessionService
    milestones: MilestoneService
    reviews: ReviewService
    scoring: ScoringService
    dashboard: DashboardService
    plans: PlanService
    settings: SettingsService

    def close(self) -> None:
        """Close the database connection."""
        self.db.close()


def build_container(
    *,
    config_path: Path | None = None,
    db_path: Path | str | None = None,
    token: str = "",
    production: bool = False,
) -> Container:
    """Build the application container.

    :param config_path: Optional override for the TOML config path.
    :param db_path: Optional override for the database path (e.g. ``":memory:"``
        in tests). When omitted, the path is read from settings.
    :param token: Expected sidecar auth token. Empty disables auth (tests).
    :param production: Enable production API hardening.
    :returns: A fully wired :class:`Container`.
    :rtype: Container
    """
    settings_repo = TomlSettingsRepository(config_path)
    settings = settings_repo.load()

    resolved_db_path: Path | str
    resolved_db_path = db_path if db_path is not None else settings.database.resolved_path

    db = DatabaseConnection(resolved_db_path)
    run_migrations(db)

    uow = SqliteUnitOfWork(db)
    clock = SystemClock()

    active_db_path = None if str(resolved_db_path) == ":memory:" else Path(resolved_db_path)
    settings_service = SettingsService(settings_repo, active_db_path=active_db_path)

    scoring = ScoringService(uow.sessions, uow.milestones, uow.scores)
    project_service = ProjectService(uow.projects)
    session_service = SessionService(uow.sessions, uow.projects, uow.milestones, clock)
    milestone_service = MilestoneService(uow.milestones, uow.projects, clock)
    review_service = ReviewService(uow.reviews)
    plan_service = PlanService(uow.projects)
    dashboard_service = DashboardService(
        uow.projects, uow.sessions, uow.milestones, scoring, settings_service
    )

    logger.info("Container built (production=%s, db=%s)", production, resolved_db_path)
    return Container(
        db=db,
        token=token,
        production=production,
        projects=project_service,
        sessions=session_service,
        milestones=milestone_service,
        reviews=review_service,
        scoring=scoring,
        dashboard=dashboard_service,
        plans=plan_service,
        settings=settings_service,
    )
