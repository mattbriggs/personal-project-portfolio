"""Application bootstrap — wires all layers together and starts the GUI."""

import logging
import tempfile
from pathlib import Path

from portfolio_manager.config.settings import Settings, load_settings
from portfolio_manager.controllers.dashboard_controller import DashboardController
from portfolio_manager.controllers.milestone_controller import MilestoneController
from portfolio_manager.controllers.project_controller import ProjectController
from portfolio_manager.controllers.review_controller import ReviewController
from portfolio_manager.controllers.session_controller import SessionController
from portfolio_manager.controllers.settings_controller import SettingsController
from portfolio_manager.db.connection import DatabaseConnection
from portfolio_manager.db.migrations import run_migrations
from portfolio_manager.events.event_bus import EventBus
from portfolio_manager.repositories.milestone_repo import MilestoneRepository
from portfolio_manager.repositories.project_repo import ProjectRepository
from portfolio_manager.repositories.review_repo import ReviewRepository
from portfolio_manager.repositories.score_repo import ScoreRepository
from portfolio_manager.repositories.session_repo import SessionRepository
from portfolio_manager.services.plan_service import PlanService
from portfolio_manager.services.project_service import ProjectService
from portfolio_manager.services.scoring_service import ScoringService
from portfolio_manager.services.session_service import SessionService
from portfolio_manager.services.week_service import WeekService
from portfolio_manager.utils.logging_config import configure_logging
from portfolio_manager.views.main_window import MainWindow

logger = logging.getLogger(__name__)


def build_app(
    settings: Settings | None = None,
    log_dir: Path | None = None,
) -> MainWindow:
    """Bootstrap the application and return the root Tk window.

    :param settings: Optional pre-loaded settings (used in tests to inject
        an in-memory database path).
    :type settings: Settings | None
    :param log_dir: Override the log directory.  When ``None`` (default) the
        directory is derived from the database path so that tests using a
        temporary database automatically get isolated logs.
    :type log_dir: pathlib.Path | None
    :returns: The fully wired :class:`~portfolio_manager.views.main_window.MainWindow`.
    :rtype: MainWindow
    """
    if settings is None:
        settings = load_settings()

    # Logging — derive log dir from DB location so tests get isolated logs.
    if log_dir is None:
        db_path_str = settings.database.path
        if db_path_str == ":memory:":
            log_dir = Path(tempfile.mkdtemp()) / "logs"
        else:
            log_dir = Path(db_path_str).expanduser().parent / "logs"
    configure_logging(log_level=settings.app.log_level, log_dir=log_dir)
    logger.info("Portfolio Manager starting up.")

    # Database
    db_path = settings.database.resolved_path
    db = DatabaseConnection.initialise(db_path)
    run_migrations(db)
    logger.info("Database ready at %s", db_path)

    # Event bus
    bus = EventBus.get()

    # Repositories
    project_repo = ProjectRepository(db)
    session_repo = SessionRepository(db)
    milestone_repo = MilestoneRepository(db)
    score_repo = ScoreRepository(db)
    review_repo = ReviewRepository(db)

    # Services
    week_svc = WeekService()
    project_svc = ProjectService(project_repo, bus)
    session_svc = SessionService(session_repo, bus)
    scoring_svc = ScoringService(session_repo, milestone_repo, score_repo)
    plan_svc = PlanService(project_repo)

    # Controllers
    dashboard_ctrl = DashboardController(project_svc, scoring_svc, week_svc, bus)
    project_ctrl = ProjectController(project_svc, plan_svc)
    session_ctrl = SessionController(
        session_svc,
        week_svc,
        milestone_repo=milestone_repo,
        default_duration_minutes=settings.session.default_duration_minutes,
    )
    milestone_ctrl = MilestoneController(milestone_repo, bus)
    review_ctrl = ReviewController(review_repo, week_svc, bus)
    settings_ctrl = SettingsController(settings, bus)

    controllers = {
        "dashboard": dashboard_ctrl,
        "project": project_ctrl,
        "session": session_ctrl,
        "milestone": milestone_ctrl,
        "review": review_ctrl,
        "settings": settings_ctrl,
    }

    window = MainWindow(controllers)
    logger.info("Main window created.")
    return window


def run() -> None:
    """Entry point: build the application and start the Tk main loop."""
    window = build_app()
    window.mainloop()
