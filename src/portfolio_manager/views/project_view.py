"""Project management view — table with popup edit and embedded plan editor."""

import logging
import tkinter as tk
from datetime import date
from tkinter import messagebox, simpledialog, ttk
from typing import Any

from portfolio_manager.views.widgets.plan_editor import PlanEditor

logger = logging.getLogger(__name__)


class _ProjectDialog(tk.Toplevel):
    """Non-modal popup for editing a project's metadata and plan document.

    The dialog is intentionally non-modal so the user can reference other
    tabs (e.g. Sessions) while editing the plan.

    :param parent: Parent widget.
    :param controller: :class:`~portfolio_manager.controllers.project_controller.ProjectController`.
    :param project: The project to edit.
    """

    def __init__(
        self,
        parent: tk.Widget,
        controller: Any,
        project: Any,
    ) -> None:
        super().__init__(parent)
        self._controller = controller
        self._project = project

        self.title(f"Project — {project.name}")
        self.geometry("900x680")
        self.minsize(700, 500)

        self._build_ui()
        self._populate()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        # ── Metadata section ─────────────────────────────────────────
        meta = ttk.LabelFrame(self, text="Details", padding=8)
        meta.pack(fill="x", padx=12, pady=(12, 4))

        row = 0

        # Project name
        ttk.Label(meta, text="Project:").grid(row=row, column=0, sticky="e", padx=6, pady=3)
        self._name_var = tk.StringVar()
        ttk.Entry(meta, textvariable=self._name_var, width=42).grid(
            row=row, column=1, columnspan=3, sticky="ew", padx=6, pady=3
        )
        row += 1

        # Description
        ttk.Label(meta, text="Description:").grid(row=row, column=0, sticky="e", padx=6, pady=3)
        self._desc_var = tk.StringVar()
        ttk.Entry(meta, textvariable=self._desc_var, width=42).grid(
            row=row, column=1, columnspan=3, sticky="ew", padx=6, pady=3
        )
        row += 1

        # Status | Priority
        ttk.Label(meta, text="Status:").grid(row=row, column=0, sticky="e", padx=6, pady=3)
        self._status_var = tk.StringVar()
        ttk.Combobox(
            meta,
            textvariable=self._status_var,
            values=["active", "backlog", "archive"],
            state="readonly",
            width=14,
        ).grid(row=row, column=1, sticky="w", padx=6, pady=3)
        ttk.Label(meta, text="Priority:").grid(row=row, column=2, sticky="e", padx=6, pady=3)
        self._priority_var = tk.StringVar()
        ttk.Combobox(
            meta,
            textvariable=self._priority_var,
            values=["1", "2", "3", "4", "5"],
            state="readonly",
            width=6,
        ).grid(row=row, column=3, sticky="w", padx=6, pady=3)
        row += 1

        # Start | End
        ttk.Label(meta, text="Start (YYYY-MM-DD):").grid(row=row, column=0, sticky="e", padx=6, pady=3)
        self._start_var = tk.StringVar()
        start_frame = ttk.Frame(meta)
        start_frame.grid(row=row, column=1, sticky="w", padx=6, pady=3)
        ttk.Entry(start_frame, textvariable=self._start_var, width=14).pack(side="left")
        ttk.Button(
            start_frame, text="Today", width=6,
            command=lambda: self._start_var.set(date.today().isoformat()),
        ).pack(side="left", padx=(4, 0))
        ttk.Label(meta, text="End (YYYY-MM-DD):").grid(row=row, column=2, sticky="e", padx=6, pady=3)
        self._end_var = tk.StringVar()
        end_frame = ttk.Frame(meta)
        end_frame.grid(row=row, column=3, sticky="w", padx=6, pady=3)
        ttk.Entry(end_frame, textvariable=self._end_var, width=14).pack(side="left")
        ttk.Button(
            end_frame, text="Today", width=6,
            command=lambda: self._end_var.set(date.today().isoformat()),
        ).pack(side="left", padx=(4, 0))

        meta.columnconfigure(1, weight=1)
        meta.columnconfigure(3, weight=1)

        # Save / Close buttons
        btn_row = ttk.Frame(self)
        btn_row.pack(fill="x", padx=12, pady=(4, 4))
        ttk.Button(btn_row, text="Save Changes", command=self._on_save).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(btn_row, text="Close", command=self.destroy).pack(side="left")

        # ── Plan editor ───────────────────────────────────────────────
        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=12, pady=4)

        plan_frame = ttk.LabelFrame(self, text="Plan Document", padding=4)
        plan_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self._plan_editor = PlanEditor(
            plan_frame,
            on_save=lambda text: self._controller.save_plan(self._project.id, text),
            render_fn=self._controller.render_plan,
        )
        self._plan_editor.pack(fill="both", expand=True)

    # ------------------------------------------------------------------
    # Data helpers
    # ------------------------------------------------------------------

    def _populate(self) -> None:
        p = self._project
        self._name_var.set(p.name)
        self._desc_var.set(p.description)
        self._status_var.set(p.status)
        self._priority_var.set(str(p.priority))
        self._start_var.set(p.started_date.isoformat() if p.started_date else "")
        self._end_var.set(p.end_date.isoformat() if p.end_date else "")
        self._plan_editor.set_content(p.plan_content)

    def _on_save(self) -> None:
        try:
            self._project.name = self._name_var.get().strip()
            self._project.description = self._desc_var.get().strip()
            self._project.status = self._status_var.get()
            self._project.priority = int(self._priority_var.get() or "3")

            raw_start = self._start_var.get().strip()
            self._project.started_date = date.fromisoformat(raw_start) if raw_start else None

            raw_end = self._end_var.get().strip()
            self._project.end_date = date.fromisoformat(raw_end) if raw_end else None

            self._controller.update_project(self._project)
            self.title(f"Project — {self._project.name}")
        except ValueError as exc:
            messagebox.showerror("Invalid Date", str(exc), parent=self)
        except Exception as exc:
            messagebox.showerror("Error", str(exc), parent=self)


# ---------------------------------------------------------------------------
# Main view
# ---------------------------------------------------------------------------


class ProjectView(ttk.Frame):
    """Project management tab — full-width table with popup edit.

    :param parent: Parent widget.
    :param controller: :class:`~portfolio_manager.controllers.project_controller.ProjectController`.
    :param milestone_controller: Used to count milestones per project.
    :param kwargs: Forwarded to :class:`ttk.Frame`.
    """

    def __init__(
        self,
        parent: tk.Widget,
        controller: Any,
        milestone_controller: Any = None,
        **kwargs: object,
    ) -> None:
        super().__init__(parent, **kwargs)  # type: ignore[arg-type]
        self._controller = controller
        self._milestone_ctrl = milestone_controller
        self._projects_cache: list[Any] = []
        self._build_ui()
        self.refresh()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        # ── Toolbar: status filter + New Project ────────────────────
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=8, pady=(6, 2))

        self._filter_var = tk.StringVar(value="active")
        for status in ("active", "backlog", "archive", "all"):
            ttk.Radiobutton(
                toolbar,
                text=status.capitalize(),
                variable=self._filter_var,
                value=status,
                command=self.refresh,
            ).pack(side="left", padx=2)

        ttk.Button(toolbar, text="New Project", command=self._on_new).pack(side="right")

        # ── Project table ─────────────────────────────────────────────
        columns = ("name", "milestones", "start", "end", "status", "priority")
        self._tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=18,
        )
        for col, heading, width, anchor in [
            ("name",       "Name",       220, "w"),
            ("milestones", "Milestones",  90, "center"),
            ("start",      "Start",       95, "center"),
            ("end",        "End",         95, "center"),
            ("status",     "Status",      80, "center"),
            ("priority",   "Priority",    60, "center"),
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
        ttk.Button(action_row, text="Archive", command=self._on_archive).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(action_row, text="Delete", command=self._on_delete).pack(side="left")

    # ------------------------------------------------------------------
    # Data refresh
    # ------------------------------------------------------------------

    def refresh(self) -> None:
        """Reload the project list from the controller."""
        status_filter = self._filter_var.get()
        status = None if status_filter == "all" else status_filter  # type: ignore[assignment]
        projects = self._controller.list_projects(status=status)
        self._projects_cache = projects

        for item in self._tree.get_children():
            self._tree.delete(item)

        for p in projects:
            if self._milestone_ctrl is not None:
                total, done = self._milestone_ctrl.count_milestones(p.id)
                ms_label = f"{done}/{total}" if total > 0 else "—"
            else:
                ms_label = "—"

            self._tree.insert(
                "",
                "end",
                values=(
                    p.name,
                    ms_label,
                    p.started_date.isoformat() if p.started_date else "—",
                    p.end_date.isoformat() if p.end_date else "—",
                    p.status,
                    p.priority,
                ),
            )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _selected_idx(self) -> int | None:
        sel = self._tree.selection()
        if not sel:
            return None
        return self._tree.index(sel[0])

    def _on_new(self) -> None:
        name = simpledialog.askstring("New Project", "Project name:", parent=self)
        if name:
            try:
                project = self._controller.create_project(name.strip())
                self.refresh()
                # Open the edit dialog immediately so the user can fill in details
                _ProjectDialog(self, self._controller, project)
            except Exception as exc:
                messagebox.showerror("Error", str(exc))

    def _on_double_click(self, _event: object) -> None:
        idx = self._selected_idx()
        if idx is None or idx >= len(self._projects_cache):
            return
        project = self._projects_cache[idx]
        # Fetch fresh copy so plan_content is up to date
        try:
            project = self._controller.get_project(project.id)
        except Exception:
            pass
        _ProjectDialog(self, self._controller, project)

    def _on_archive(self) -> None:
        idx = self._selected_idx()
        if idx is None:
            messagebox.showwarning("No Selection", "Select a project first.")
            return
        if messagebox.askyesno("Archive", "Archive this project?"):
            try:
                self._controller.archive_project(self._projects_cache[idx].id)
                self.refresh()
            except Exception as exc:
                messagebox.showerror("Error", str(exc))

    def _on_delete(self) -> None:
        idx = self._selected_idx()
        if idx is None:
            messagebox.showwarning("No Selection", "Select a project first.")
            return
        if messagebox.askyesno(
            "Delete Project",
            "Delete this project and all its sessions/milestones?\nThis cannot be undone.",
        ):
            try:
                self._controller.delete_project(self._projects_cache[idx].id)
                self.refresh()
            except Exception as exc:
                messagebox.showerror("Error", str(exc))
