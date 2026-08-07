"""Exception-to-error-response translation.

Maps domain/application exceptions and framework errors to the stable
:class:`ErrorResponse` taxonomy. Unexpected errors are sanitized: the response
carries a correlation ID but never a stack trace (SRS §5.15).
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from portfolio_manager.contracts.errors import ErrorCode, ErrorResponse
from portfolio_manager.domain.errors import (
    ArchivedProjectError,
    ConflictError,
    DatabaseError,
    MigrationError,
    NotFoundError,
    ValidationError,
)
from portfolio_manager.infrastructure.logging.context import correlation_id

logger = logging.getLogger(__name__)

_STATUS_BY_CODE = {
    ErrorCode.VALIDATION_ERROR: 422,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.CONFLICT: 409,
    ErrorCode.ARCHIVED_READ_ONLY: 409,
    ErrorCode.DATABASE_ERROR: 500,
    ErrorCode.MIGRATION_ERROR: 500,
    ErrorCode.INTERNAL_ERROR: 500,
}


def _error(code: ErrorCode, message: str, *, field_errors=None, retryable=False):
    body = ErrorResponse(
        code=code,
        message=message,
        field_errors=field_errors or {},
        correlation_id=correlation_id.get(),
        retryable=retryable,
    )
    return JSONResponse(status_code=_STATUS_BY_CODE[code], content=body.model_dump(mode="json"))


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers on *app*.

    :param app: The FastAPI application.
    """

    @app.exception_handler(NotFoundError)
    async def _not_found(_r: Request, exc: NotFoundError):
        return _error(ErrorCode.NOT_FOUND, str(exc))

    @app.exception_handler(ValidationError)
    async def _validation(_r: Request, exc: ValidationError):
        return _error(ErrorCode.VALIDATION_ERROR, str(exc))

    @app.exception_handler(ConflictError)
    async def _conflict(_r: Request, exc: ConflictError):
        return _error(ErrorCode.CONFLICT, str(exc))

    @app.exception_handler(ArchivedProjectError)
    async def _archived(_r: Request, exc: ArchivedProjectError):
        return _error(ErrorCode.ARCHIVED_READ_ONLY, str(exc))

    @app.exception_handler(MigrationError)
    async def _migration(_r: Request, exc: MigrationError):
        logger.error("Migration error: %s", exc)
        return _error(ErrorCode.MIGRATION_ERROR, "A database migration failed.")

    @app.exception_handler(DatabaseError)
    async def _database(_r: Request, exc: DatabaseError):
        logger.error("Database error: %s", exc)
        return _error(ErrorCode.DATABASE_ERROR, "A database error occurred.", retryable=True)

    @app.exception_handler(RequestValidationError)
    async def _request_validation(_r: Request, exc: RequestValidationError):
        field_errors: dict[str, list[str]] = {}
        for err in exc.errors():
            loc = ".".join(str(p) for p in err.get("loc", []) if p != "body")
            field_errors.setdefault(loc or "body", []).append(err.get("msg", "invalid"))
        return _error(
            ErrorCode.VALIDATION_ERROR,
            "Request validation failed.",
            field_errors=field_errors,
        )

    @app.exception_handler(Exception)
    async def _unexpected(_r: Request, exc: Exception):
        logger.exception("Unhandled error: %s", exc)
        return _error(
            ErrorCode.INTERNAL_ERROR,
            "An unexpected error occurred. See logs for the correlation ID.",
        )
