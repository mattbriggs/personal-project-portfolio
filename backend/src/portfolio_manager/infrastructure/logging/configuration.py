"""Structured logging configuration.

Emits single-line JSON records to stderr (captured by the Rust supervisor) with
correlation IDs and credential redaction. A rotating file handler writes to
``~/.portfolio_manager/logs/sidecar.log``.
"""

import json
import logging
import logging.handlers

from portfolio_manager.infrastructure.logging.filters import (
    CorrelationIdFilter,
    RedactionFilter,
)
from portfolio_manager.infrastructure.system.paths import LOG_DIR


class JsonFormatter(logging.Formatter):
    """Format log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        """Serialize *record* to a JSON string.

        :param record: The log record.
        :rtype: str
        """
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": getattr(record, "correlation_id", "-"),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(level: str = "INFO") -> None:
    """Configure root logging with JSON output, redaction, and rotation.

    Safe to call once at startup. Existing handlers are cleared to avoid
    duplicate output on reconfiguration.

    :param level: Logging level name (e.g. ``"INFO"``).
    """
    root = logging.getLogger()
    root.setLevel(level.upper())
    for handler in list(root.handlers):
        root.removeHandler(handler)

    formatter = JsonFormatter()
    corr = CorrelationIdFilter()
    redact = RedactionFilter()

    stream = logging.StreamHandler()
    stream.setFormatter(formatter)
    stream.addFilter(corr)
    stream.addFilter(redact)
    root.addHandler(stream)

    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            LOG_DIR / "sidecar.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        file_handler.addFilter(corr)
        file_handler.addFilter(redact)
        root.addHandler(file_handler)
    except OSError:
        # File logging is best-effort; stderr logging is always available.
        root.warning("Could not open log file in %s", LOG_DIR)
