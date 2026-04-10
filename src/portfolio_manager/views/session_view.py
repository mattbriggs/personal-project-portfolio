"""Session management view — table with popup create/edit."""

import logging
import tkinter as tk
from datetime import date, timedelta
from tkinter import messagebox, ttk
from typing import Any

from portfolio_manager.events.event_bus import SETTINGS_CHANGED, EventBus
from portfolio_manager.utils.date_utils import to_week_key, week_key_to_date_range

logger = logging.getLogger(__name__)

_STATUSES = ("backlog", "planned", "doing", "done", "cancelled")


class _SessionDialog(tk.Toplevel):
    """Modal dialog for creating or editing a session.

    :param parent: Parent widget.
    :param controller: SessionController instance.
    :param project_map: ``{project_name: project_id}`` for all visible projects.
    :param session: Existing session for edit mode; ``None`` for create mode.
    """

    def __init__(
        self,
        parent: tk.Widget,
        controller: Any,
        project_map: dict[str, int],
        session: Any = None,
    ) -> None:
        super().__init__(parent)
        self._controller = controller
        self._project_map = project_map
        self._session = session
        self._milestone_map: dict[str, int | None] = {}
        self.saved = False

        self.title("Edit Session" if session else "New Session")
        self.resizable(False, False)
        self.grab_set()
        self._build_ui()
        if session:
            self._populate(session)
        self.bind("<Escape>", lambda _e: self.destroy())

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        form = ttk.Frame(self, padding=12)
        form.pack(fill="both", expand=True)
        row = 0

        # Project
        ttk.Label(form, text="Project:").grid(row=row, column=0, sticky="e", padx=6, pady=4)
        self._project_var = tk.StringVar()
        self._project_combo = ttk.Combobox(
            form,
            textvariable=self._project_var,
            values=list(self._project_map.keys()),
            state="readonly",
            width=32,
        )
        self._project_combo.grid(row=row, column=1, columnspan=2, sticky="ew", padx=6, pady=4)
        self._project_combo.bind("<<ComboboxSelected>>", self._on_project_change)
        row += 1

        # Milestone
        ttk.Label(form, text="Milestone:").grid(row=row, column=0, sticky="e", padx=6, pady=4)
        self._milestone_var = tk.StringVar()
        self._milestone_combo = ttk.Combobox(
            form,
            textvariable=self._milestone_var,
            state="readonly",
            width=32,
        )
        self._milestone_combo.grid(row=row, column=1, columnspan=2, sticky="ew", padx=6, pady=4)
        row += 1

        # Session name (the description field — shown as "Session" in UI)
        ttk.Label(form, text="Session:").grid(row=row, column=0, sticky="e", padx=6, pady=4)
        self._name_var = tk.StringVar()
        ttk.Entry(form, textvariable=self._name_var, width=36).grid(
            row=row, column=1, columnspan=2, sticky="ew", padx=6, pady=4
        )
        row += 1

        # Date
        ttk.Label(form, text="Date (YYYY-MM-DD):").grid(row=row, column=0, sticky="e", padx=6, pady=4)
        self._date_var = tk.StringVar(value=date.today().isoformat())
        date_frame = ttk.Frame(form)
        date_frame.grid(row=row, column=1, columnspan=2, sticky="w", padx=6, pady=4)
        ttk.Entry(date_frame, textvariable=self._date_var, width=14).pack(side="left")
        ttk.Button(
            date_frame, text="Today", width=6,
            command=lambda: self._date_var.set(date.today().isoformat()),
        ).pack(side="left", padx=(4, 0))
        row += 1

        # Status + Min on the same row
        ttk.Label(form, text="Status:").grid(row=row, column=0, sticky="e", padx=6, pady=4)
        inline = ttk.Frame(form)
        inline.grid(row=row, column=1, columnspan=2, sticky="w", padx=6, pady=4)
        self._status_var = tk.StringVar(value="backlog")
        ttk.Combobox(
            inline,
            textvariable=self._status_var,
            values=list(_STATUSES),
            state="readonly",
            width=14,
        ).pack(side="left")
        ttk.Label(inline, text="  Min:").pack(side="left")
        self._dur_var = tk.IntVar(value=self._controller.default_duration_minutes)
        ttk.Spinbox(
            inline,
            from_=15,
            to=480,
            increment=15,
            textvariable=self._dur_var,
            width=6,
        ).pack(side="left", padx=(4, 0))
        row += 1

        # Description (the notes field — longer text)
        ttk.Label(form, text="Description:").grid(row=row, column=0, sticky="ne", padx=6, pady=4)
        self._notes_text = tk.Text(form, height=5, wrap="word")
        scroll = ttk.Scrollbar(form, command=self._notes_text.yview)
        self._notes_text.configure(yscrollcommand=scroll.set)
        self._notes_text.grid(row=row, column=1, sticky="ew", padx=(6, 0), pady=4)
        scroll.grid(row=row, column=2, sticky="ns", pady=4)
        row += 1

        form.columnconfigure(1, weight=1)

        # Buttons
        btn_row = ttk.Frame(self)
        btn_row.pack(fill="x", padx=12, pady=(0, 12))
        ttk.Button(btn_row, text="Save", command=self._on_save, width=10).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(btn_row, text="Cancel", command=self.destroy, width=10).pack(side="left")

        # Seed the milestone combo for the first project
        if self._project_map:
            self._project_var.set(next(iter(self._project_map)))
            self._on_project_change(None)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _on_project_change(self, _event: object) -> None:
        project_id = self._project_map.get(self._project_var.get())
        self._milestone_map = {"— none —": None}
        if project_id is not None:
            for ms in self._controller.get_milestones_for_project(project_id):
                label = f"[{ms.id}] {ms.description[:36]}"
                self._milestone_map[label] = ms.id
        self._milestone_combo["values"] = list(self._milestone_map.keys())
        self._milestone_combo.current(0)

    def _populate(self, session: Any) -> None:
        """Fill form fields from an existing session."""
        for name, pid in self._project_map.items():
            if pid == session.project_id:
                self._project_var.set(name)
                self._on_project_change(None)
                break
        if session.milestone_id is not None:
            for label, mid in self._milestone_map.items():
                if mid == session.milestone_id:
                    self._milestone_var.set(label)
                    break
        self._name_var.set(session.description)
        self._date_var.set(session.scheduled_date.isoformat())
        self._status_var.set(session.status)
        self._dur_var.set(session.duration_minutes)
        self._notes_text.delete("1.0", tk.END)
        self._notes_text.insert("1.0", session.notes)

    def _on_save(self) -> None:
        project_name = self._project_var.get()
        if not project_name or project_name not in self._project_map:
            messagebox.showwarning("Validation", "Please select a project.", parent=self)
            return
        try:
            d = date.fromisoformat(self._date_var.get().strip())
        except ValueError:
            messagebox.showerror("Invalid Date", "Date must be YYYY-MM-DD.", parent=self)
            return

        project_id = self._project_map[project_name]
        milestone_id = self._milestone_map.get(self._milestone_var.get())
        description = self._name_var.get().strip()
        notes = self._notes_text.get("1.0", tk.END).strip()
        status = self._status_var.get()
        duration = self._dur_var.get()

        try:
            if self._session is None:
                self._controller.create_session(
                    project_id=project_id,
                    scheduled_date=d,
                    duration_minutes=duration,
                    description=description,
                    notes=notes,
                    milestone_id=milestone_id,
                    status=status,
                )
            else:
                s = self._session
                s.project_id = project_id
                s.milestone_id = milestone_id
                s.description = description
                s.notes = notes
                s.scheduled_date = d
                s.status = status
                s.duration_minutes = duration
                self._controller.update_session(s)
            self.saved = True
            self.destroy()
        except Exception as exc:
            messagebox.showerror("Error", str(exc), parent=self)


# ---------------------------------------------------------------------------
# Main view
# ---------------------------------------------------------------------------


class SessionView(ttk.Frame):
    """Session management tab — full-width table with popup create/edit.

    :param parent: Parent widget.
    :param session_controller: :class:`~portfolio_manager.controllers.session_controller.SessionController`.
    :param project_controller: Used to populate project references.
    :param settings_controller: Used to read weekly budget hours.
    :param kwargs: Forwarded to :class:`ttk.Frame`.
    """

    def __init__(
        self,
        parent: tk.Widget,
        session_controller: Any,
        project_controller: Any,
        settings_controller: Any = None,
        **kwargs: object,
    ) -> None:
        super().__init__(parent, **kwargs)  # type: ignore[arg-type]
        self._sessions = session_controller
        self._projects = project_controller
        self._settings = settings_controller
        self._session_ids: list[int] = []
        self._sessions_cache: list[Any] = []
        self._build_ui()
        self.refresh()
        EventBus.get().subscribe(SETTINGS_CHANGED, lambda **_kw: self.refresh())

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        # ── Toolbar: week nav + New Session ─────────────────────────────
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=8, pady=(6, 2))

        ttk.Label(toolbar, text="Week:").pack(side="left")
        ttk.Button(toolbar, text="<", command=self._prev_week, width=2).pack(side="left")
        self._week_var = tk.StringVar(value=self._sessions._weeks.current_week_key())
        ttk.Entry(toolbar, textvariable=self._week_var, width=10).pack(side="left", padx=2)
        ttk.Button(toolbar, text=">", command=self._next_week, width=2).pack(side="left")
        ttk.Button(toolbar, text="Load", command=self.refresh).pack(side="left", padx=4)
        ttk.Button(toolbar, text="New Session", command=self._on_new).pack(side="right")

        # ── Session table ─────────────────────────────────────────────
        columns = ("project", "milestone", "date", "min", "status", "session")
        self._tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=16,
        )
        for col, heading, width, anchor in [
            ("project",   "Project",   150, "w"),
            ("milestone", "Milestone", 130, "w"),
            ("date",      "Date",       90, "center"),
            ("min",       "Min",        50, "center"),
            ("status",    "Status",     80, "center"),
            ("session",   "Session",   260, "w"),
        ]:
            self._tree.heading(col, text=heading)
            self._tree.column(col, width=width, anchor=anchor)

        scroll = ttk.Scrollbar(self, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y", padx=(0, 8))
        self._tree.pack(fill="both", expand=True, padx=8, pady=4)
        self._tree.bind("<Double-Button-1>", self._on_double_click)

        # ── Action bar ────────────────────────────────────────────────
        action_row = ttk.Frame(self)
        action_row.pack(fill="x", padx=8, pady=(0, 8))

        ttk.Label(action_row, text="Set Status:").pack(side="left")
        self._status_var = tk.StringVar(value="planned")
        ttk.Combobox(
            action_row,
            textvariable=self._status_var,
            values=list(_STATUSES),
            state="readonly",
            width=12,
        ).pack(side="left", padx=4)
        ttk.Button(action_row, text="Apply", command=self._on_set_status).pack(
            side="left", padx=(0, 16)
        )
        ttk.Button(action_row, text="Delete", command=self._on_delete).pack(side="left")

        # ── Budget summary bar ────────────────────────────────────────
        budget_bar = ttk.Frame(self, relief="groove", borderwidth=1)
        budget_bar.pack(fill="x", padx=8, pady=(0, 8))
        self._budget_label = ttk.Label(budget_bar, text="", foreground="#555")
        self._budget_label.pack(side="left", padx=8, pady=3)

    # ------------------------------------------------------------------
    # Data refresh
    # ------------------------------------------------------------------

    def refresh(self) -> None:
        """Reload sessions for the current week."""
        all_projects = self._projects.list_projects(status=None)
        all_by_id = {p.id: p.name for p in all_projects}

        # Build milestone name lookup (one query per project — acceptable at this scale)
        milestone_name_map: dict[int, str] = {}
        for pid in all_by_id:
            for ms in self._sessions.get_milestones_for_project(pid):
                milestone_name_map[ms.id] = ms.description[:30]

        week_key = self._week_var.get().strip()
        sessions = self._sessions.get_week_sessions(week_key)
        self._sessions_cache = sessions

        for item in self._tree.get_children():
            self._tree.delete(item)
        self._session_ids = []

        total_min = 0
        done_min = 0
        for s in sessions:
            self._session_ids.append(s.id)
            ms_label = (
                milestone_name_map.get(s.milestone_id, f"#{s.milestone_id}")
                if s.milestone_id
                else ""
            )
            self._tree.insert(
                "",
                "end",
                values=(
                    all_by_id.get(s.project_id, f"#{s.project_id}"),
                    ms_label,
                    s.scheduled_date.isoformat(),
                    s.duration_minutes,
                    s.status,
                    s.description,
                ),
            )
            if s.status != "cancelled":
                total_min += s.duration_minutes
            if s.status == "done":
                done_min += s.duration_minutes

        self._update_budget_bar(total_min, done_min)

    def _update_budget_bar(self, total_min: int, done_min: int) -> None:
        """Refresh the budget summary label."""
        budget_hours = 0
        if self._settings is not None:
            try:
                budget_hours = self._settings.settings.session.weekly_budget_hours
            except Exception:
                pass
        budget_min = budget_hours * 60
        remaining_min = budget_min - total_min

        parts = [
            f"Planned: {total_min} min",
            f"Done: {done_min} min",
        ]
        if budget_min > 0:
            remaining_str = f"{remaining_min} min" if remaining_min >= 0 else f"{abs(remaining_min)} min over"
            parts.append(f"Budget: {budget_min} min  |  Remaining: {remaining_str}")
        self._budget_label.configure(text="  |  ".join(parts))

    def navigate_to_week(self, week_key: str) -> None:
        """Navigate to *week_key* and reload.

        :param week_key: Week key in ``YYYY.W`` format.
        """
        self._week_var.set(week_key)
        self.refresh()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _selected_idx(self) -> int | None:
        sel = self._tree.selection()
        if not sel:
            return None
        return self._tree.index(sel[0])

    def _on_new(self) -> None:
        active = self._projects.list_projects(status="active")
        project_map = {p.name: p.id for p in active}
        dialog = _SessionDialog(self, self._sessions, project_map)
        self.wait_window(dialog)
        if dialog.saved:
            self.refresh()

    def _on_double_click(self, _event: object) -> None:
        idx = self._selected_idx()
        if idx is None or idx >= len(self._sessions_cache):
            return
        session = self._sessions_cache[idx]
        all_projects = self._projects.list_projects(status=None)
        project_map = {p.name: p.id for p in all_projects}
        dialog = _SessionDialog(self, self._sessions, project_map, session=session)
        self.wait_window(dialog)
        if dialog.saved:
            self.refresh()

    def _on_set_status(self) -> None:
        idx = self._selected_idx()
        if idx is None:
            messagebox.showwarning("No Selection", "Select a session first.")
            return
        try:
            self._sessions.set_session_status(self._session_ids[idx], self._status_var.get())
            self.refresh()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _on_delete(self) -> None:
        idx = self._selected_idx()
        if idx is None:
            messagebox.showwarning("No Selection", "Select a session first.")
            return
        if messagebox.askyesno("Delete Session", "Delete this session?"):
            try:
                self._sessions.delete_session(self._session_ids[idx])
                self.refresh()
            except Exception as exc:
                messagebox.showerror("Error", str(exc))

    def _prev_week(self) -> None:
        try:
            monday, _ = week_key_to_date_range(self._week_var.get().strip())
            self._week_var.set(to_week_key(monday - timedelta(weeks=1)))
            self.refresh()
        except ValueError:
            pass

    def _next_week(self) -> None:
        try:
            monday, _ = week_key_to_date_range(self._week_var.get().strip())
            self._week_var.set(to_week_key(monday + timedelta(weeks=1)))
            self.refresh()
        except ValueError:
            pass
