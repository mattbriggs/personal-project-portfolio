"""Domain and application error hierarchy.

These errors are transport-independent. The API layer
(:mod:`portfolio_manager.api.exception_handlers`) translates them into the
stable error taxonomy exposed to Rust and the renderer.

Mapping to error codes:

===============================  ====================
Exception                        Error code
===============================  ====================
:class:`NotFoundError`           ``NOT_FOUND``
:class:`ValidationError`         ``VALIDATION_ERROR``
:class:`ConflictError`           ``CONFLICT``
:class:`ArchivedProjectError`    ``ARCHIVED_READ_ONLY``
:class:`DatabaseError`           ``DATABASE_ERROR``
:class:`MigrationError`          ``MIGRATION_ERROR``
===============================  ====================
"""


class PortfolioManagerError(Exception):
    """Base class for all Portfolio Manager domain/application errors."""


class DatabaseError(PortfolioManagerError):
    """Raised when a database operation fails unexpectedly."""


class DatabaseLockedError(DatabaseError):
    """Raised when the SQLite database is locked by another connection."""


class MigrationError(DatabaseError):
    """Raised when a schema migration cannot be applied."""


class NotFoundError(PortfolioManagerError):
    """Raised when a requested entity does not exist.

    :param entity: Human-readable entity type (e.g. ``'Project'``).
    :param entity_id: The identifier that was not found.
    """

    def __init__(self, entity: str, entity_id: int | str) -> None:
        super().__init__(f"{entity} with id={entity_id!r} not found.")
        self.entity = entity
        self.entity_id = entity_id


class ValidationError(PortfolioManagerError):
    """Raised when user-supplied input fails a business validation rule."""


class ConflictError(PortfolioManagerError):
    """Raised on a uniqueness conflict (e.g. duplicate project slug)."""


class ArchivedProjectError(PortfolioManagerError):
    """Raised when a caller attempts to mutate an archived (read-only) project."""


class SessionStateError(PortfolioManagerError):
    """Raised when a session operation is invalid for the current state."""


class ConfigError(PortfolioManagerError):
    """Raised when application configuration is invalid or unreadable."""
