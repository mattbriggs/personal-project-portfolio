"""Abstract base repository for Portfolio Manager.

All concrete repositories extend :class:`BaseRepository` which holds a
reference to the shared :class:`~portfolio_manager.db.connection.DatabaseConnection`
and exposes the :meth:`transaction` helper.
"""

import sqlite3
from contextlib import contextmanager
from typing import Generator

from portfolio_manager.db.connection import DatabaseConnection


class BaseRepository:
    """Abstract base class for all repository classes.

    :param db: The shared database connection singleton.
    :type db: DatabaseConnection
    """

    def __init__(self, db: DatabaseConnection) -> None:
        self._db = db

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        """Delegate to the database connection's transaction context manager.

        :yields: The raw :class:`sqlite3.Connection` for use within the block.
        """
        with self._db.transaction() as conn:
            yield conn
