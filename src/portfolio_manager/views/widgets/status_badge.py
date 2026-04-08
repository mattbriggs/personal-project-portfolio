"""Traffic-light status badge widget."""

import tkinter as tk
from tkinter import ttk

# Status → colour + label text (REQ-UI-007: colour + text for accessibility)
_STATUS_CONFIG: dict[str, tuple[str, str]] = {
    "green": ("#2e7d32", "● Green"),
    "yellow": ("#f9a825", "● Yellow"),
    "red": ("#c62828", "● Red"),
    "": ("#9e9e9e", "● —"),
}


class StatusBadge(ttk.Label):
    """A label widget that displays a coloured traffic-light status indicator.

    :param parent: Parent Tk widget.
    :param status: Initial status string — ``'green'``, ``'yellow'``, or ``'red'``.
    :param kwargs: Additional keyword arguments forwarded to :class:`ttk.Label`.
    """

    def __init__(
        self,
        parent: tk.Widget,
        status: str = "",
        **kwargs: object,
    ) -> None:
        super().__init__(parent, **kwargs)  # type: ignore[arg-type]
        self._status = ""
        self.set_status(status)

    def set_status(self, status: str) -> None:
        """Update the displayed status.

        :param status: New status — ``'green'``, ``'yellow'``, ``'red'``, or empty.
        :type status: str
        """
        self._status = status
        colour, text = _STATUS_CONFIG.get(status, _STATUS_CONFIG[""])
        self.configure(text=text, foreground=colour)
