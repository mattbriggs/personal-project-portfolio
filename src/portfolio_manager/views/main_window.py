"""Main application window — left project panel + tabbed right panel."""

import logging
import tkinter as tk
from datetime import date, timedelta
from tkinter import ttk
from typing import Any

from portfolio_manager.events.event_bus import (
    MILESTONE_UPDATED,
    PROJECT_CREATED,
    PROJECT_DELETED,
    PROJECT_UPDATED,
    EventBus,
)
from portfolio_manager.utils.date_utils import current_week_key

logger = logging.getLogger(__name__)

_MIN_WIDTH = 1024
_MIN_HEIGHT = 768

# Tab definitions: (tab_label, view_class_attr)
_TABS = [
    ("Dashboard", "_dashboard_view"),
    ("Sessions", "_session_view"),
    ("Projects", "_project_view"),
    ("Milestones", "_milestone_view"),
    ("Weekly Review", "_review_view"),
    ("Settings", "_settings_view"),
]


class MainWindow(tk.Tk):
    """Root Tk window for Portfolio Manager.

    Owns the left week-navigator panel and the right tabbed notebook.

    :param controllers: Dict of controller instances keyed by name.
    :type controllers: dict[str, Any]
    """

    def __init__(self, controllers: dict[str, Any]) -> None:
        super().__init__()
        self._controllers = controllers
        self._configure_window()
        self._build_ui()

    # ------------------------------------------------------------------
    # Window configuration
    # ------------------------------------------------------------------

    def _configure_window(self) -> None:
        """Set window title, minimum size, and grid weights."""
        week_key = current_week_key()
        self.title(f"Portfolio Manager — Week {week_key}")
        self.minsize(_MIN_WIDTH, _MIN_HEIGHT)
        self.geometry(f"{_MIN_WIDTH}x{_MIN_HEIGHT}")
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """Build the main two-panel layout."""
        self._build_left_panel()
        self._build_right_panel()

    def _build_left_panel(self) -> None:
        """Build the left week-navigator panel."""
        left = ttk.Frame(self, width=210)
        left.grid(row=0, column=0, sticky="nswe", padx=(4, 0), pady=4)
        left.grid_propagate(False)
        left.rowconfigure(1, weight=1)

        ttk.Label(left, text="Weeks", font=("", 10, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=4, pady=(4, 2)
        )

        self._week_listbox = tk.Listbox(left, selectmode="single", width=24)
        scroll = ttk.Scrollbar(
            left, orient="vertical", command=self._week_listbox.yview
        )
        self._week_listbox.configure(yscrollcommand=scroll.set)
        scroll.grid(row=1, column=1, sticky="ns")
        self._week_listbox.grid(row=1, column=0, sticky="nswe")
        left.columnconfigure(0, weight=1)

        self._week_listbox.bind("<<ListboxSelect>>", self._on_week_select)
        self._week_keys: list[str] = []

    def _build_right_panel(self) -> None:
        """Build the tabbed right panel and instantiate all views."""
        right = ttk.Frame(self)
        right.grid(row=0, column=1, sticky="nswe", padx=4, pady=4)
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)

        self._notebook = ttk.Notebook(right)
        self._notebook.grid(row=0, column=0, sticky="nswe")

        c = self._controllers

        from portfolio_manager.views.dashboard_view import DashboardView
        from portfolio_manager.views.milestone_view import MilestoneView
        from portfolio_manager.views.project_view import ProjectView
        from portfolio_manager.views.review_view import ReviewView
        from portfolio_manager.views.session_view import SessionView
        from portfolio_manager.views.settings_view import SettingsView

        self._dashboard_view = DashboardView(self._notebook, c["dashboard"])
        self._session_view = SessionView(self._notebook, c["session"], c["project"], c["settings"])
        self._project_view = ProjectView(self._notebook, c["project"], c["milestone"])
        self._milestone_view = MilestoneView(
            self._notebook, c["milestone"], c["project"]
        )
        self._review_view = ReviewView(self._notebook, c["review"])
        self._settings_view = SettingsView(self._notebook, c["settings"])

        for label, attr in _TABS:
            view = getattr(self, attr)
            self._notebook.add(view, text=label)

        self._dashboard_view.refresh()
        self._refresh_week_panel()
        self._wire_cross_view_events()

    def _wire_cross_view_events(self) -> None:
        """Subscribe views to events that their controllers don't already handle."""
        bus = EventBus.get()

        def _refresh_projects(**_kw: object) -> None:
            self._project_view.refresh()

        def _refresh_milestone_projects(**_kw: object) -> None:
            self._milestone_view.refresh_projects()

        # Milestone counts in ProjectView go stale when milestones change.
        bus.subscribe(MILESTONE_UPDATED, _refresh_projects)
        # ProjectView table goes stale when projects are created, updated, or deleted.
        for event in (PROJECT_CREATED, PROJECT_UPDATED, PROJECT_DELETED):
            bus.subscribe(event, _refresh_projects)
        # MilestoneView project selector goes stale when projects change.
        for event in (PROJECT_CREATED, PROJECT_UPDATED, PROJECT_DELETED):
            bus.subscribe(event, _refresh_milestone_projects)

    # ------------------------------------------------------------------
    # Left panel (week navigator) helpers
    # ------------------------------------------------------------------

    def _refresh_week_panel(self) -> None:
        """Populate the week list: 12 past weeks + current + 4 future weeks."""
        self._week_listbox.delete(0, tk.END)
        self._week_keys = []

        today = date.today()
        monday_today = today - timedelta(days=today.weekday())
        start_monday = monday_today - timedelta(weeks=12)

        current_idx: int | None = None
        for i in range(17):  # 12 past + current + 4 future
            wk_monday = start_monday + timedelta(weeks=i)
            wk_sunday = wk_monday + timedelta(days=6)
            iso = wk_monday.isocalendar()
            wk_key = f"{iso.year}.{iso.week}"
            label = (
                f"{wk_key}  "
                f"{wk_monday.strftime('%b %-d')}–{wk_sunday.strftime('%-d')}"
            )
            self._week_listbox.insert(tk.END, label)
            self._week_keys.append(wk_key)
            if wk_monday == monday_today:
                current_idx = i
                self._week_listbox.itemconfigure(i, background="#d4edda")  # highlight

        if current_idx is not None:
            self._week_listbox.see(current_idx)
            self._week_listbox.selection_set(current_idx)

    def _on_week_select(self, _event: object) -> None:
        """Navigate Sessions and Weekly Review tabs to the selected week."""
        sel = self._week_listbox.curselection()
        if not sel:
            return
        week_key = self._week_keys[sel[0]]
        self._session_view.navigate_to_week(week_key)
        self._review_view.navigate_to_week(week_key)
