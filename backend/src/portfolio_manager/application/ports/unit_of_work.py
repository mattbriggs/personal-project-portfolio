"""Unit-of-work port for coordinated multi-repository writes."""

from types import TracebackType
from typing import Protocol

from portfolio_manager.application.ports.milestone_repository import MilestoneRepository
from portfolio_manager.application.ports.project_repository import ProjectRepository
from portfolio_manager.application.ports.review_repository import ReviewRepository
from portfolio_manager.application.ports.score_repository import ScoreRepository
from portfolio_manager.application.ports.session_repository import SessionRepository


class UnitOfWork(Protocol):
    """Transaction boundary exposing all repositories.

    Use for operations spanning multiple repositories (project deletion, status
    change followed by score recomputation). ``__exit__`` rolls back on error.
    """

    projects: ProjectRepository
    sessions: SessionRepository
    milestones: MilestoneRepository
    scores: ScoreRepository
    reviews: ReviewRepository

    def __enter__(self) -> "UnitOfWork": ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
