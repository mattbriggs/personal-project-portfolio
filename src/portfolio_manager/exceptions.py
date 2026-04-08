"""Custom exception hierarchy for Portfolio Manager.

All application-specific exceptions inherit from :class:`PortfolioManagerError`
so callers can catch the base class when they don't care about the sub-type.
"""


class PortfolioManagerError(Exception):
    """Base class for all Portfolio Manager exceptions."""


# --- Database ---


class DatabaseError(PortfolioManagerError):
    """Raised when a database operation fails unexpectedly."""


class DatabaseLockedError(DatabaseError):
    """Raised when the SQLite database is locked by another connection."""


class MigrationError(DatabaseError):
    """Raised when a schema migration cannot be applied."""


# --- Domain ---


class NotFoundError(PortfolioManagerError):
    """Raised when a requested entity does not exist in the database.

    :param entity: Human-readable entity type (e.g. 'Project', 'Session').
    :param entity_id: The primary key that was not found.
    """

    def __init__(self, entity: str, entity_id: int | str) -> None:
        super().__init__(f"{entity} with id={entity_id!r} not found.")
        self.entity = entity
        self.entity_id = entity_id


class SessionStateError(PortfolioManagerError):
    """Raised when a session operation is invalid for the current state.

    Example: marking an already-completed session as complete.
    """


class ProjectStateError(PortfolioManagerError):
    """Raised when a project operation is invalid for the current lifecycle state.

    Example: adding a session to an archived project.
    """


class ValidationError(PortfolioManagerError):
    """Raised when user-supplied input fails validation rules."""


# --- Config ---


class ConfigError(PortfolioManagerError):
    """Raised when the application configuration file is invalid or unreadable."""
