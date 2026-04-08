"""Simple in-process event bus implementing the Observer pattern.

Views subscribe to named events; services emit those events after state
changes.  This keeps the service layer decoupled from the presentation layer.

Usage::

    bus = EventBus.get()
    bus.subscribe("SESSION_COMPLETED", dashboard_controller.on_session_completed)
    bus.emit("SESSION_COMPLETED", session_id=42)
"""

import logging
from collections import defaultdict
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)

# Named event constants — use these rather than bare strings.
PROJECT_CREATED = "PROJECT_CREATED"
PROJECT_UPDATED = "PROJECT_UPDATED"
PROJECT_DELETED = "PROJECT_DELETED"
SESSION_CREATED = "SESSION_CREATED"
SESSION_UPDATED = "SESSION_UPDATED"
SESSION_COMPLETED = "SESSION_COMPLETED"
SESSION_DELETED = "SESSION_DELETED"
MILESTONE_UPDATED = "MILESTONE_UPDATED"
SCORE_UPDATED = "SCORE_UPDATED"
REVIEW_SAVED = "REVIEW_SAVED"
SETTINGS_CHANGED = "SETTINGS_CHANGED"

_instance: "EventBus | None" = None

Callback = Callable[..., None]


class EventBus:
    """Singleton in-process event bus.

    Subscribers register a callable; the bus calls all subscribers for a given
    event when :meth:`emit` is invoked with that event name.
    """

    def __init__(self) -> None:
        self._listeners: dict[str, list[Callback]] = defaultdict(list)

    @classmethod
    def get(cls) -> "EventBus":
        """Return the shared :class:`EventBus` singleton.

        Creates the instance on first call.

        :rtype: EventBus
        """
        global _instance
        if _instance is None:
            _instance = cls()
        return _instance

    @classmethod
    def reset(cls) -> None:
        """Discard the singleton.

        Useful in tests to start with a clean bus.
        """
        global _instance
        _instance = None

    def subscribe(self, event: str, callback: Callback) -> None:
        """Register *callback* to be called when *event* is emitted.

        :param event: Event name string (use module-level constants).
        :type event: str
        :param callback: Callable invoked with keyword arguments from the emitter.
        :type callback: Callable[..., None]
        """
        self._listeners[event].append(callback)
        logger.debug("Subscribed %s to event '%s'", callback, event)

    def unsubscribe(self, event: str, callback: Callback) -> None:
        """Remove *callback* from the subscriber list for *event*.

        A no-op if the callback was not subscribed.

        :param event: Event name.
        :param callback: The previously registered callable.
        """
        try:
            self._listeners[event].remove(callback)
        except ValueError:
            pass

    def emit(self, event: str, **kwargs: Any) -> None:
        """Notify all subscribers of *event* with *kwargs*.

        Exceptions raised by a subscriber are logged and suppressed so that
        one bad subscriber cannot prevent others from receiving the event.

        :param event: Event name to emit.
        :param kwargs: Arbitrary keyword arguments passed to each subscriber.
        """
        listeners = list(self._listeners.get(event, []))
        logger.debug("Emitting '%s' to %d subscriber(s)", event, len(listeners))
        for cb in listeners:
            try:
                cb(**kwargs)
            except Exception:
                logger.exception("Error in subscriber %s for event '%s'", cb, event)
