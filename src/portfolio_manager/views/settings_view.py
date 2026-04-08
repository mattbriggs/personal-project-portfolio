"""Settings view."""

import logging
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any

from portfolio_manager.config.settings import Settings, AppConfig, SessionConfig

logger = logging.getLogger(__name__)


class SettingsView(ttk.Frame):
    """Settings tab for configuring application behaviour.

    :param parent: Parent widget.
    :param controller: :class:`~portfolio_manager.controllers.settings_controller.SettingsController`.
    :param kwargs: Forwarded to :class:`ttk.Frame`.
    """

    def __init__(self, parent: tk.Widget, controller: Any, **kwargs: object) -> None:
        super().__init__(parent, **kwargs)  # type: ignore[arg-type]
        self._controller = controller
        self._build_ui()
        self._load_settings()

    def _build_ui(self) -> None:
        """Build the settings form layout."""
        form = ttk.LabelFrame(self, text="Application Settings")
        form.pack(fill="both", expand=False, padx=16, pady=16)

        row = 0

        # Weekly budget
        ttk.Label(form, text="Weekly budget (hours):").grid(
            row=row, column=0, sticky="e", padx=8, pady=4
        )
        self._budget_var = tk.IntVar()
        ttk.Spinbox(form, from_=1, to=40, textvariable=self._budget_var, width=6).grid(
            row=row, column=1, sticky="w", padx=8
        )
        row += 1

        # Default session duration
        ttk.Label(form, text="Default session duration (min):").grid(
            row=row, column=0, sticky="e", padx=8, pady=4
        )
        self._duration_var = tk.IntVar()
        ttk.Spinbox(
            form, from_=60, to=180, increment=15,
            textvariable=self._duration_var, width=6
        ).grid(row=row, column=1, sticky="w", padx=8)
        row += 1

        # Log level
        ttk.Label(form, text="Log level:").grid(
            row=row, column=0, sticky="e", padx=8, pady=4
        )
        self._log_level_var = tk.StringVar()
        ttk.Combobox(
            form,
            textvariable=self._log_level_var,
            values=["DEBUG", "INFO", "WARNING", "ERROR"],
            state="readonly",
            width=10,
        ).grid(row=row, column=1, sticky="w", padx=8)
        row += 1

        # Theme
        ttk.Label(form, text="Theme:").grid(
            row=row, column=0, sticky="e", padx=8, pady=4
        )
        self._theme_var = tk.StringVar()
        ttk.Combobox(
            form,
            textvariable=self._theme_var,
            values=["light", "dark"],
            state="readonly",
            width=10,
        ).grid(row=row, column=1, sticky="w", padx=8)
        row += 1

        ttk.Button(self, text="Save Settings", command=self._save_settings).pack(
            anchor="w", padx=16, pady=8
        )

    def _load_settings(self) -> None:
        """Populate form fields from current settings."""
        s = self._controller.settings
        self._budget_var.set(s.session.weekly_budget_hours)
        self._duration_var.set(s.session.default_duration_minutes)
        self._log_level_var.set(s.app.log_level)
        self._theme_var.set(s.app.theme)

    def _save_settings(self) -> None:
        """Read form values and persist updated settings."""
        s = self._controller.settings
        new_settings = Settings(
            app=AppConfig(
                log_level=self._log_level_var.get(),
                theme=self._theme_var.get(),
            ),
            session=SessionConfig(
                default_duration_minutes=self._duration_var.get(),
                weekly_budget_hours=self._budget_var.get(),
            ),
            database=s.database,
        )
        try:
            self._controller.update_settings(new_settings)
            messagebox.showinfo("Saved", "Settings saved.")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def refresh(self) -> None:
        """Reload settings from controller (called when SETTINGS_CHANGED fires)."""
        self._load_settings()
