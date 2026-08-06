"""Correlation-ID middleware.

Assigns a correlation ID to each request (honoring an inbound
``X-Correlation-ID`` header if present), stores it in a context variable for
structured logging, and echoes it back on the response.
"""

import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from portfolio_manager.infrastructure.logging.context import correlation_id

CORRELATION_HEADER = "X-Correlation-ID"


class CorrelationMiddleware(BaseHTTPMiddleware):
    """Attach a correlation ID to each request and response."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Set the correlation ID context var and echo it on the response.

        :param request: The inbound request.
        :param call_next: The next handler in the chain.
        :rtype: starlette.responses.Response
        """
        cid = request.headers.get(CORRELATION_HEADER) or uuid.uuid4().hex
        token = correlation_id.set(cid)
        request.state.correlation_id = cid
        try:
            response = await call_next(request)
        finally:
            correlation_id.reset(token)
        response.headers[CORRELATION_HEADER] = cid
        return response
