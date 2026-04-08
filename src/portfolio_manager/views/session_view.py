"""Session management view — list, create, complete, cancel sessions."""

import logging
import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk
from typing import Any

logger = logging.getLogger(__name__)


class SessionView(ttk.Frame):
    """Session management tab.

    Shows sessions for the current week across all projects, with controls to
    create, complete, reschedule, and delete sessions.

    :param parent: Parent widget.
    :param session_controller: :class:`~portfolio_manager.controllers.session_controller.SessionController`.
    :param project_controller: :class:`~portfolio_manager.controllers.project_controller.ProjectController`
        (used to populate the project dropdown).
    :param kwargs: Forwarded to :class:`ttk.Frame`.
    """

    def __init__(
        self,
        parent: tk.Widget,
        session_controller: Any,
        project_controller: Any,
        **kwargs: object,
    ) -> None:
        super().__init__(parent, **kwargs)  # type: ignore[arg-type]
        self._sessions = session_controller
        self._projects = project_controller
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        """Build the session view layout."""
        # Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=8, pady=4)

        ttk.Label(toolbar, text="Week:").pack(side="left")
        self._week_var = tk.StringVar(value=self._sessions._weeks.current_week_key())
        week_entry = ttk.Entry(toolbar, textvariable=self._week_var, width=10)
        week_entry.pack(side="left", padx=4)
        ttk.Button(toolbar, text="Load", command=self.refresh).pack(side="left")

        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=8)

        ttk.Label(toolbar, text="Project:").pack(side="left")
        self._project_var = tk.StringVar()
        self._project_combo = ttk.Combobox(
            toolbar, textvariable=self._project_var, width=20, state="readonly"
        )
        self._project_combo.pack(side="left", padx=4)

        ttk.Label(toolbar, text="Date (YYYY-MM-DD):").pack(side="left", padx=(8, 0))
        self._date_var = tk.StringVar(value=date.today().isoformat())
        ttk.Entry(toolbar, textvariable=self._date_var, width=12).pack(
            side="left", padx=4
        )

        ttk.Button(toolbar, text="Add Session", command=self._on_add).pack(
            side="left", padx=4
        )

        # Session table
        columns = ("project", "date", "week", "duration", "status", "focus")
        self._tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=15,
        )
        for col, heading, width in [
            ("project", "Project", 160),
            ("date", "Date", 90),
            ("week", "Week", 70),
            ("duration", "Min", 50),
            ("status", "Status", 80),
            ("focus", "Focus", 200),
        ]:
            self._tree.heading(col, text=heading)
            self._tree.column(col, width=width, anchor="center")
        self._tree.column("project", anchor="w")
        self._tree.column("focus", anchor="w")

        scroll = ttk.Scrollbar(self, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y", padx=(0, 8))
        self._tree.pack(fill="both", expand=True, padx=8, pady=4)

        # Action buttons
        action_row = ttk.Frame(self)
        action_row.pack(fill="x", padx=8, pady=(0, 8))
        ttk.Button(action_row, text="Mark Complete", command=self._on_complete).pack(
            side="left", padx=4
        )
        ttk.Button(action_row, text="Cancel Session", command=self._on_cancel).pack(
            side="left", padx=4
        )
        ttk.Button(action_row, text="Delete", command=self._on_delete).pack(
            side="left", padx=4
        )

        self._session_ids: list[int] = []

    def refresh(self) -> None:
        """Reload sessions for the current week from the controller."""
        # Refresh project combo
        all_projects = self._projects.list_projects(status="active")
        self._project_names = [p.name for p in all_projects]
        self._project_map = {p.name: p.id for p in all_projects}
        self._project_combo["values"] = self._project_names
        if self._project_names and not self._project_var.get():
            self._project_combo.current(0)

        week_key = self._week_var.get().strip()
        sessions = self._sessions.get_week_sessions(week_key)
        all_projects_map = {
            p.id: p.name for p in self._projects.list_projects(status=None)
        }

        for item in self._tree.get_children():
            self._tree.delete(item)

        self._session_ids = []
        for s in sessions:
            self._session_ids.append(s.id)
            self._tree.insert(
                "",
                "end",
                values=(
                    all_projects_map.get(s.project_id, f"#{s.project_id}"),
                    s.scheduled_date.isoformat(),
                    s.week_key,
                    s.duration_minutes,
                    s.status,
                    s.focus or "",
                ),
            )

    def _selected_session_id(self) -> int | None:
        """Return the id of the currently selected session, or ``None``."""
        sel = self._tree.selection()
        if not sel:
            return None
        idx = self._tree.index(sel[0])
        return self._session_ids[idx]

    def _on_add(self) -> None:
        """Create a new planned session from the form values."""
        project_name = self._project_var.get()
        if not project_name or project_name not in self._project_map:
            messagebox.showwarning("Select Project", "Please select a project.")
            return
        try:
            d = date.fromisoformat(self._date_var.get().strip())
        except ValueError:
            messagebox.showerror("Invalid Date", "Date must be in YYYY-MM-DD format.")
            return
        try:
            self._sessions.create_session(
                project_id=self._project_map[project_name],
                scheduled_date=d,
            )
            self.refresh()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _on_complete(self) -> None:
        """Mark the selected session as completed."""
        sid = self._selected_session_id()
        if sid is None:
            return
        try:
            self._sessions.complete_session(sid)
            self.refresh()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _on_cancel(self) -> None:
        """Cancel the selected session."""
        sid = self._selected_session_id()
        if sid is None:
            return
        try:
            self._sessions.cancel_session(sid)
            self.refresh()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _on_delete(self) -> None:
        """Delete the selected session after confirmation."""
        sid = self._selected_session_id()
        if sid is None:
            return
        if messagebox.askyesno("Delete Session", "Delete this session?"):
            try:
                self._sessions.delete_session(sid)
                self.refresh()
            except Exception as exc:
                messagebox.showerror("Error", str(exc))
