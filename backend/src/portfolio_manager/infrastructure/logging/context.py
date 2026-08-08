"""Correlation-ID context for structured logging.

A context variable carries the current request's correlation ID so log records
emitted anywhere during request handling can be tagged with it.
"""

from contextvars import ContextVar

#: Correlation ID for the in-flight request, or ``"-"`` outside a request.
correlation_id: ContextVar[str] = ContextVar("correlation_id", default="-")
