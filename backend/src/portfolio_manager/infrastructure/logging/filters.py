"""Logging filters: correlation ID injection and credential redaction."""

import logging
import re

from portfolio_manager.infrastructure.logging.context import correlation_id

# Patterns that must never appear in logs (auth headers / token query params).
_REDACT_PATTERNS = [
    re.compile(r"(x-api-key\s*[:=]\s*)(\S+)", re.IGNORECASE),
    re.compile(r"(authorization\s*[:=]\s*)(\S+)", re.IGNORECASE),
    re.compile(r"(token[\"']?\s*[:=]\s*[\"']?)([^\s\"',}]+)", re.IGNORECASE),
]
_REDACTED = r"\1[REDACTED]"


class CorrelationIdFilter(logging.Filter):
    """Attach the current correlation ID to every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Set ``record.correlation_id`` and always allow the record.

        :param record: The log record being processed.
        :rtype: bool
        """
        record.correlation_id = correlation_id.get()
        return True


class RedactionFilter(logging.Filter):
    """Redact tokens and auth headers from formatted log messages."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Redact sensitive substrings from ``record.msg``.

        :param record: The log record being processed.
        :rtype: bool
        """
        try:
            message = record.getMessage()
        except Exception:  # noqa: BLE001
            return True
        redacted = message
        for pattern in _REDACT_PATTERNS:
            redacted = pattern.sub(_REDACTED, redacted)
        if redacted != message:
            record.msg = redacted
            record.args = ()
        return True
