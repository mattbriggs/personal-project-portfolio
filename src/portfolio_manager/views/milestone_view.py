"""Milestone tracking view."""

import logging
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from typing import Any

logger = logging.getLogger(__name__)


class MilestoneView(ttk.Frame):
    """Milestone tracking tab for the currently selected project.

    :param parent: Parent widget.
    :param controller: :class:`~portfolio_manager.controllers.milestone_controller.MilestoneController`.
    :param project_controller: Used to populate the project selector.
    :param kwargs: Forwarded to :class:`ttk.Frame`.
    """

    def __init__(
        self,
        parent: tk.Widget,
        controller: Any,
        project_controller: Any,
        **kwargs: object,
    ) -> None:
        super().__init__(parent, **kwargs)  # type: ignore[arg-type]
        self._controller = controller
        self._projects = project_controller
        self._selected_project_id: int | None = None
        self._milestone_ids: list[int] = []
        self._build_ui()
        self.refresh_projects()

    def _build_ui(self) -> None:
        """Build the milestone view layout."""
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=8, pady=4)

        ttk.Label(toolbar, text="Project:").pack(side="left")
        self._project_var = tk.StringVar()
        self._project_combo = ttk.Combobox(
            toolbar, textvariable=self._project_var, width=25, state="readonly"
        )
        self._project_combo.pack(side="left", padx=4)
        self._project_combo.bind("<<ComboboxSelected>>", self._on_project_change)

        ttk.Button(toolbar, text="Add Milestone", command=self._on_add).pack(side="left", padx=8)
        ttk.Button(toolbar, text="Toggle Complete", command=self._on_toggle).pack(side="left")
        ttk.Button(toolbar, text="Delete", command=self._on_delete).pack(side="left", padx=4)

        columns = ("done", "description", "completed_date")
        self._tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=15,
        )
        self._tree.heading("done", text="Done")
        self._tree.column("done", width=50, anchor="center")
        self._tree.heading("description", text="Description")
        self._tree.column("description", width=400, anchor="w")
        self._tree.heading("completed_date", text="Completed")
        self._tree.column("completed_date", width=100, anchor="center")

        scroll = ttk.Scrollbar(self, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y", padx=(0, 8))
        self._tree.pack(fill="both", expand=True, padx=8, pady=4)

    def refresh_projects(self) -> None:
        """Reload the project list into the project selector."""
        projects = self._projects.list_projects(status="active")
        self._project_map = {p.name: p.id for p in projects}
        self._project_combo["values"] = list(self._project_map.keys())
        if projects:
            self._project_combo.current(0)
            self._selected_project_id = projects[0].id
            self._refresh_milestones()

    def _on_project_change(self, _event: object) -> None:
        name = self._project_var.get()
        self._selected_project_id = self._project_map.get(name)
        self._refresh_milestones()

    def _refresh_milestones(self) -> None:
        """Reload milestones for the selected project."""
        for item in self._tree.get_children():
            self._tree.delete(item)
        self._milestone_ids = []
        if self._selected_project_id is None:
            return
        milestones = self._controller.list_milestones(self._selected_project_id)
        for ms in milestones:
            self._milestone_ids.append(ms.id)
            self._tree.insert(
                "",
                "end",
                values=(
                    "✓" if ms.is_complete else "",
                    ms.description,
                    ms.completed_date.isoformat() if ms.completed_date else "",
                ),
            )

    def _selected_milestone_id(self) -> int | None:
        sel = self._tree.selection()
        if not sel:
            return None
        return self._milestone_ids[self._tree.index(sel[0])]

    def _on_add(self) -> None:
        if self._selected_project_id is None:
            return
        desc = simpledialog.askstring("Add Milestone", "Milestone description:")
        if desc:
            self._controller.add_milestone(self._selected_project_id, desc)
            self._refresh_milestones()

    def _on_toggle(self) -> None:
        mid = self._selected_milestone_id()
        if mid is None:
            return
        self._controller.toggle_milestone(mid)
        self._refresh_milestones()

    def _on_delete(self) -> None:
        mid = self._selected_milestone_id()
        if mid is None:
            return
        if messagebox.askyesno("Delete Milestone", "Delete this milestone?"):
            self._controller.delete_milestone(mid)
            self._refresh_milestones()

    def refresh(self) -> None:
        """Public refresh entry point (called by event bus subscribers)."""
        self._refresh_milestones()
