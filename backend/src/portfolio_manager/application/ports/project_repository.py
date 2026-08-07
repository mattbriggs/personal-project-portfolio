"""Project repository port."""

from typing import Protocol

from portfolio_manager.domain.enums import ProjectStatus
from portfolio_manager.domain.models import Project


class ProjectRepository(Protocol):
    """Persistence contract for :class:`Project`.

    Implementations return detached domain values (not live rows). ``get``
    raises :class:`~portfolio_manager.domain.errors.NotFoundError` when the
    entity is missing; ``create`` may raise ``sqlite3.IntegrityError`` on a
    duplicate slug (translated to a conflict by the service layer). Results of
    ``list`` are ordered by priority then name.
    """

    def create(self, project: Project) -> Project: ...
    def get(self, project_id: int) -> Project: ...
    def get_by_slug(self, slug: str) -> Project | None: ...
    def list(self, status: ProjectStatus | None = None) -> list[Project]: ...
    def update(self, project: Project) -> Project: ...
    def update_plan(self, project_id: int, plan_content: str) -> None: ...
    def delete(self, project_id: int) -> None: ...
