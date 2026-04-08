"""Main application window — left project panel + tabbed right panel."""

import logging
import tkinter as tk
from tkinter import ttk
from typing import Any

from portfolio_manager.utils.date_utils import current_week_key

logger = logging.getLogger(__name__)

_MIN_WIDTH = 1024
_MIN_HEIGHT = 768

# Tab definitions: (tab_label, view_class_attr)
_TABS = [
    ("Dashboard",       "_dashboard_view"),
    ("Sessions",        "_session_view"),
    ("Projects",        "_project_view"),
    ("Milestones",      "_milestone_view"),
    ("Weekly Review",   "_review_view"),
    ("Settings",        "_settings_view"),
]


class MainWindow(tk.Tk):
    """Root Tk window for Portfolio Manager.

    Owns the left project panel (quick-select list with status indicators)
    and the right tabbed notebook.

    :param controllers: Dict of controller instances keyed by name.
    :type controllers: dict[str, Any]
    """

    def __init__(self, controllers: dict[str, Any]) -> None:
        super().__init__()
        self._controllers = controllers
        self._configure_window()
        self._build_ui()
        self._refresh_project_panel()

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
        """Build the left project list panel."""
        left = ttk.Frame(self, width=200)
        left.grid(row=0, column=0, sticky="nswe", padx=(4, 0), pady=4)
        left.grid_propagate(False)
        left.rowconfigure(1, weight=1)

        ttk.Label(left, text="Projects", font=("", 10, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=4, pady=(4, 2)
        )

        self._project_listbox = tk.Listbox(left, selectmode="single", width=22)
        scroll = ttk.Scrollbar(left, orient="vertical", command=self._project_listbox.yview)
        self._project_listbox.configure(yscrollcommand=scroll.set)
        scroll.grid(row=1, column=1, sticky="ns")
        self._project_listbox.grid(row=1, column=0, sticky="nswe")
        left.columnconfigure(0, weight=1)

        self._project_listbox.bind("<<ListboxSelect>>", self._on_project_select)

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
        from portfolio_manager.views.session_view import SessionView
        from portfolio_manager.views.project_view import ProjectView
        from portfolio_manager.views.milestone_view import MilestoneView
        from portfolio_manager.views.review_view import ReviewView
        from portfolio_manager.views.settings_view import SettingsView

        self._dashboard_view = DashboardView(self._notebook, c["dashboard"])
        self._session_view = SessionView(
            self._notebook, c["session"], c["project"]
        )
        self._project_view = ProjectView(self._notebook, c["project"])
        self._milestone_view = MilestoneView(
            self._notebook, c["milestone"], c["project"]
        )
        self._review_view = ReviewView(self._notebook, c["review"])
        self._settings_view = SettingsView(self._notebook, c["settings"])

        for label, attr in _TABS:
            view = getattr(self, attr)
            self._notebook.add(view, text=label)

        self._dashboard_view.refresh()

    # ------------------------------------------------------------------
    # Left panel helpers
    # ------------------------------------------------------------------

    def _refresh_project_panel(self) -> None:
        """Reload active projects into the left-panel list."""
        self._project_listbox.delete(0, tk.END)
        try:
            projects = self._controllers["project"].list_projects(status="active")
        except Exception:
            logger.exception("Failed to load project panel")
            return
        self._left_projects = projects
        for p in projects:
            self._project_listbox.insert(tk.END, p.name)

    def _on_project_select(self, _event: object) -> None:
        """Switch the right panel context to the selected project.

        Currently switches to the Projects tab; future: context-awareness per tab.
        """
        sel = self._project_listbox.curselection()
        if not sel:
            return
        # Switch to the Projects tab so the user sees the selected project.
        self._notebook.select(2)  # index 2 = Projects tab
