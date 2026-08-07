"""Error contract and stable error-code taxonomy.

Shared by Python (this module), Rust (``CommandError``), and TypeScript
(generated types) so error handling is consistent across the boundary.
"""

from enum import StrEnum

from pydantic import BaseModel, Field


class ErrorCode(StrEnum):
    """Stable error codes returned in :class:`ErrorResponse`."""

    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    ARCHIVED_READ_ONLY = "ARCHIVED_READ_ONLY"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    DATABASE_ERROR = "DATABASE_ERROR"
    MIGRATION_ERROR = "MIGRATION_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class ErrorResponse(BaseModel):
    """Structured error payload returned for every non-2xx business response.

    :param code: Stable error code.
    :param message: User-safe message (never contains a stack trace or token).
    :param field_errors: Field-level validation messages.
    :param correlation_id: Correlation ID for cross-referencing logs.
    :param retryable: Whether the client may safely retry.
    """

    code: ErrorCode
    message: str
    field_errors: dict[str, list[str]] = Field(default_factory=dict)
    correlation_id: str = "-"
    retryable: bool = False
