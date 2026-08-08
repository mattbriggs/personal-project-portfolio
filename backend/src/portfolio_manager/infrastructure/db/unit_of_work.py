"""SQLite Unit of Work.

Bundles the five repositories over a single :class:`DatabaseConnection` and
provides explicit ``commit``/``rollback`` for multi-repository writes (e.g.
project deletion, or a session status change followed by score recomputation).

The connection uses SQLite's implicit transaction handling; ``commit`` and
``rollback`` operate on the shared connection. Individual repository methods
already wrap their own statements in transactions, so the Unit of Work is used
where a service coordinates several writes that must succeed or fail together.
"""

from types import TracebackType

from portfolio_manager.infrastructure.db.connection import DatabaseConnection
from portfolio_manager.infrastructure.db.repositories.milestones import (
    SqliteMilestoneRepository,
)
from portfolio_manager.infrastructure.db.repositories.projects import (
    SqliteProjectRepository,
)
from portfolio_manager.infrastructure.db.repositories.reviews import (
    SqliteReviewRepository,
)
from portfolio_manager.infrastructure.db.repositories.scores import SqliteScoreRepository
from portfolio_manager.infrastructure.db.repositories.sessions import (
    SqliteSessionRepository,
)


class SqliteUnitOfWork:
    """Concrete unit of work backed by SQLite.

    :param db: Shared database connection.

    Usage::

        with uow:
            uow.projects.delete(project_id)
            uow.commit()
    """

    def __init__(self, db: DatabaseConnection) -> None:
        self._db = db
        self.projects = SqliteProjectRepository(db)
        self.sessions = SqliteSessionRepository(db)
        self.milestones = SqliteMilestoneRepository(db)
        self.scores = SqliteScoreRepository(db)
        self.reviews = SqliteReviewRepository(db)

    def __enter__(self) -> "SqliteUnitOfWork":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            self.rollback()

    def commit(self) -> None:
        """Commit the current connection state."""
        self._db.conn.commit()

    def rollback(self) -> None:
        """Roll back the current connection state."""
        self._db.conn.rollback()
