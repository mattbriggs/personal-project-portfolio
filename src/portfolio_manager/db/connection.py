"""Singleton database connection for Portfolio Manager.

All repositories share the same :class:`DatabaseConnection` instance obtained
via :meth:`DatabaseConnection.get`.  The connection enables foreign-key
enforcement and WAL journal mode on creation.

Usage::

    db = DatabaseConnection.get()
    with db.transaction():
        db.execute("UPDATE project SET name = ? WHERE id = ?", ("New", 1))
"""

import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from portfolio_manager.exceptions import DatabaseLockedError

logger = logging.getLogger(__name__)

_instance: "DatabaseConnection | None" = None


class DatabaseConnection:
    """Singleton wrapper around a :mod:`sqlite3` connection.

    :param db_path: Filesystem path to the SQLite database file.
    :type db_path: pathlib.Path
    """

    def __init__(self, db_path: Path) -> None:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._path = db_path
        self._conn = self._open()
        logger.info("Opened database at %s", db_path)

    # ------------------------------------------------------------------
    # Class-level singleton access
    # ------------------------------------------------------------------

    @classmethod
    def get(cls) -> "DatabaseConnection":
        """Return the shared :class:`DatabaseConnection` instance.

        :raises RuntimeError: If :func:`initialise` has not been called.
        :rtype: DatabaseConnection
        """
        if _instance is None:
            raise RuntimeError(
                "DatabaseConnection has not been initialised. "
                "Call DatabaseConnection.initialise(path) at startup."
            )
        return _instance

    @classmethod
    def initialise(cls, db_path: Path) -> "DatabaseConnection":
        """Create (or reuse) the singleton connection.

        Safe to call multiple times; subsequent calls with the same path are
        no-ops.

        :param db_path: Path to the SQLite database file.
        :type db_path: pathlib.Path
        :returns: The shared :class:`DatabaseConnection`.
        :rtype: DatabaseConnection
        """
        global _instance
        if _instance is None:
            _instance = cls(db_path)
        return _instance

    @classmethod
    def reset(cls) -> None:
        """Close and discard the singleton instance.

        Primarily useful in tests to obtain a fresh in-memory database.
        """
        global _instance
        if _instance is not None:
            try:
                _instance._conn.close()
            except Exception:
                pass
            _instance = None

    # ------------------------------------------------------------------
    # Connection helpers
    # ------------------------------------------------------------------

    def _open(self) -> sqlite3.Connection:
        """Open the SQLite connection with recommended settings."""
        conn = sqlite3.connect(str(self._path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        return conn

    @property
    def conn(self) -> sqlite3.Connection:
        """The underlying :class:`sqlite3.Connection`.

        :rtype: sqlite3.Connection
        """
        return self._conn

    # ------------------------------------------------------------------
    # Transaction context manager
    # ------------------------------------------------------------------

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager that wraps statements in a single transaction.

        On success the transaction is committed; on any exception it is rolled
        back and the exception is re-raised.

        :raises DatabaseLockedError: If SQLite reports a locked database.

        Usage::

            with db.transaction():
                db.execute("UPDATE ...")
                db.execute("INSERT ...")
        """
        try:
            self._conn.execute("BEGIN")
            yield self._conn
            self._conn.execute("COMMIT")
        except sqlite3.OperationalError as exc:
            self._conn.execute("ROLLBACK")
            if "locked" in str(exc).lower():
                raise DatabaseLockedError(
                    "The database is locked by another process."
                ) from exc
            raise
        except Exception:
            self._conn.execute("ROLLBACK")
            raise

    # ------------------------------------------------------------------
    # Convenience wrappers
    # ------------------------------------------------------------------

    def execute(
        self,
        sql: str,
        params: tuple | list = (),
    ) -> sqlite3.Cursor:
        """Execute a single SQL statement.

        :param sql: SQL statement to execute.
        :type sql: str
        :param params: Bind parameters.
        :returns: The resulting :class:`sqlite3.Cursor`.
        :rtype: sqlite3.Cursor
        """
        try:
            return self._conn.execute(sql, params)
        except sqlite3.OperationalError as exc:
            if "locked" in str(exc).lower():
                raise DatabaseLockedError(str(exc)) from exc
            raise

    def executescript(self, sql: str) -> None:
        """Execute a multi-statement SQL script (commits implicitly).

        :param sql: SQL script text.
        :type sql: str
        """
        self._conn.executescript(sql)

    def fetchall(
        self,
        sql: str,
        params: tuple | list = (),
    ) -> list[sqlite3.Row]:
        """Execute *sql* and return all rows.

        :param sql: SELECT statement.
        :param params: Bind parameters.
        :returns: List of :class:`sqlite3.Row` objects.
        :rtype: list[sqlite3.Row]
        """
        return self.execute(sql, params).fetchall()

    def fetchone(
        self,
        sql: str,
        params: tuple | list = (),
    ) -> sqlite3.Row | None:
        """Execute *sql* and return the first row, or ``None``.

        :param sql: SELECT statement.
        :param params: Bind parameters.
        :returns: A :class:`sqlite3.Row` or ``None``.
        :rtype: sqlite3.Row | None
        """
        return self.execute(sql, params).fetchone()
