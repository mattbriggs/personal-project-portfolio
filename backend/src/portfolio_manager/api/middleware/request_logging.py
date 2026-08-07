"""Request-logging middleware.

Logs method, path, and status for each request. Never logs headers or bodies, so
the ``X-API-Key`` token cannot leak into logs.
"""

import logging

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("portfolio_manager.request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log a single line per request (method, path, status)."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Log the request outcome.

        :param request: The inbound request.
        :param call_next: The next handler.
        :rtype: starlette.responses.Response
        """
        response = await call_next(request)
        logger.info("%s %s -> %s", request.method, request.url.path, response.status_code)
        return response
