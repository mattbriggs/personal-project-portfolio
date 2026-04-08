"""Controller for the settings view."""

import logging

from portfolio_manager.config.settings import Settings, save_settings
from portfolio_manager.events.event_bus import SETTINGS_CHANGED, EventBus

logger = logging.getLogger(__name__)


class SettingsController:
    """Mediates between the settings view and the config/settings layer.

    :param settings: Current application settings.
    :param bus: Event bus for broadcasting settings changes.
    """

    def __init__(
        self,
        settings: Settings,
        bus: EventBus | None = None,
    ) -> None:
        self._settings = settings
        self._bus = bus or EventBus.get()

    @property
    def settings(self) -> Settings:
        """Return the current :class:`~portfolio_manager.config.settings.Settings`.

        :rtype: Settings
        """
        return self._settings

    def update_settings(self, settings: Settings) -> None:
        """Persist updated settings and notify subscribers.

        :param settings: Modified settings object to persist.
        :type settings: Settings
        """
        save_settings(settings)
        self._settings = settings
        self._bus.emit(SETTINGS_CHANGED)
        logger.info("Settings updated and saved.")
