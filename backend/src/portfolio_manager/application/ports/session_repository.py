"""Session repository port."""

from collections.abc import Mapping
from typing import Protocol

from portfolio_manager.domain.enums import SessionStatus
from portfolio_manager.domain.models import Session


class SessionRepository(Protocol):
    """Persistence contract for :class:`Session`.

    ``list_*`` methods order by scheduled date. ``count_by_status`` returns a
    mapping of status name to count for a project in a week; missing statuses
    are absent from the mapping.
    """

    def create(self, session: Session) -> Session: ...
    def get(self, session_id: int) -> Session: ...
    def list_for_week(self, week_key: str) -> list[Session]: ...
    def list_for_project(
        self,
        project_id: int,
        week_key: str | None = None,
        status: SessionStatus | None = None,
    ) -> list[Session]: ...
    def update(self, session: Session) -> Session: ...
    def delete(self, session_id: int) -> None: ...
    def count_by_status(self, project_id: int, week_key: str) -> Mapping[str, int]: ...
