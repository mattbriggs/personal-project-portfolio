"""Project management view — list and detail with plan editor."""

import logging
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from typing import Any

from portfolio_manager.views.widgets.plan_editor import PlanEditor

logger = logging.getLogger(__name__)


class ProjectView(ttk.Frame):
    """Project management tab: project list + detail form + plan editor.

    :param parent: Parent widget.
    :param controller: :class:`~portfolio_manager.controllers.project_controller.ProjectController`.
    :param kwargs: Forwarded to :class:`ttk.Frame`.
    """

    def __init__(self, parent: tk.Widget, controller: Any, **kwargs: object) -> None:
        super().__init__(parent, **kwargs)  # type: ignore[arg-type]
        self._controller = controller
        self._selected_id: int | None = None
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        """Build the project view layout."""
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill="both", expand=True)

        # Left: project list
        left = ttk.Frame(paned)
        paned.add(left, weight=1)

        btn_row = ttk.Frame(left)
        btn_row.pack(fill="x", padx=4, pady=4)
        ttk.Button(btn_row, text="New Project", command=self._on_new).pack(side="left")
        ttk.Button(btn_row, text="Archive", command=self._on_archive).pack(side="left", padx=4)
        ttk.Button(btn_row, text="Delete", command=self._on_delete).pack(side="left")

        # Status filter
        self._filter_var = tk.StringVar(value="active")
        filter_row = ttk.Frame(left)
        filter_row.pack(fill="x", padx=4)
        for status in ("active", "backlog", "archive", "all"):
            ttk.Radiobutton(
                filter_row, text=status.capitalize(),
                variable=self._filter_var, value=status,
                command=self.refresh,
            ).pack(side="left")

        self._listbox = tk.Listbox(left, selectmode="single")
        scroll = ttk.Scrollbar(left, command=self._listbox.yview)
        self._listbox.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self._listbox.pack(fill="both", expand=True, padx=4, pady=4)
        self._listbox.bind("<<ListboxSelect>>", self._on_select)

        # Right: detail + plan editor
        right = ttk.Frame(paned)
        paned.add(right, weight=3)

        detail = ttk.LabelFrame(right, text="Project Details")
        detail.pack(fill="x", padx=4, pady=4)

        for row_idx, (label_text, attr) in enumerate([
            ("Name:", "_name_var"),
            ("Status:", "_status_var"),
            ("Priority:", "_priority_var"),
            ("Description:", "_desc_var"),
        ]):
            ttk.Label(detail, text=label_text).grid(
                row=row_idx, column=0, sticky="e", padx=4, pady=2
            )
            var = tk.StringVar()
            setattr(self, attr, var)
            entry = ttk.Entry(detail, textvariable=var)
            entry.grid(row=row_idx, column=1, sticky="ew", padx=4, pady=2)

        detail.columnconfigure(1, weight=1)

        ttk.Button(right, text="Save Changes", command=self._on_save).pack(
            anchor="e", padx=4, pady=(0, 4)
        )

        self._plan_editor: PlanEditor | None = None
        self._plan_frame = ttk.LabelFrame(right, text="Plan Document")
        self._plan_frame.pack(fill="both", expand=True, padx=4, pady=4)

    def _build_plan_editor(self, project_id: int) -> None:
        """Create or re-create the plan editor for the selected project."""
        for widget in self._plan_frame.winfo_children():
            widget.destroy()

        def on_save(text: str) -> None:
            self._controller.save_plan(project_id, text)

        self._plan_editor = PlanEditor(
            self._plan_frame,
            on_save=on_save,
            render_fn=self._controller.render_plan,
        )
        self._plan_editor.pack(fill="both", expand=True)

        project = self._controller.get_project(project_id)
        self._plan_editor.set_content(project.plan_content)

    def refresh(self) -> None:
        """Reload the project list from the controller."""
        status_filter = self._filter_var.get()
        status = None if status_filter == "all" else status_filter  # type: ignore[assignment]
        projects = self._controller.list_projects(status=status)

        self._listbox.delete(0, tk.END)
        self._projects: list[Any] = projects
        for p in projects:
            self._listbox.insert(tk.END, f"[{p.priority}] {p.name}")

    def _on_select(self, _event: object) -> None:
        """Load selected project details into the form."""
        sel = self._listbox.curselection()
        if not sel:
            return
        project = self._projects[sel[0]]
        self._selected_id = project.id
        self._name_var.set(project.name)
        self._status_var.set(project.status)
        self._priority_var.set(str(project.priority))
        self._desc_var.set(project.description)
        self._build_plan_editor(project.id)

    def _on_save(self) -> None:
        """Save changes to the selected project."""
        if self._selected_id is None:
            return
        try:
            project = self._controller.get_project(self._selected_id)
            project.name = self._name_var.get().strip()
            project.status = self._status_var.get()  # type: ignore[assignment]
            project.priority = int(self._priority_var.get())
            project.description = self._desc_var.get()
            self._controller.update_project(project)
            self.refresh()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _on_new(self) -> None:
        """Prompt for a name and create a new project."""
        name = simpledialog.askstring("New Project", "Project name:")
        if name:
            try:
                self._controller.create_project(name)
                self.refresh()
            except Exception as exc:
                messagebox.showerror("Error", str(exc))

    def _on_archive(self) -> None:
        """Archive the selected project."""
        if self._selected_id is None:
            return
        if messagebox.askyesno("Archive", "Archive this project?"):
            try:
                self._controller.archive_project(self._selected_id)
                self._selected_id = None
                self.refresh()
            except Exception as exc:
                messagebox.showerror("Error", str(exc))

    def _on_delete(self) -> None:
        """Delete the selected project after confirmation."""
        if self._selected_id is None:
            return
        if messagebox.askyesno(
            "Delete Project",
            "Delete this project and all its sessions/milestones?\nThis cannot be undone.",
        ):
            try:
                self._controller.delete_project(self._selected_id)
                self._selected_id = None
                self.refresh()
            except Exception as exc:
                messagebox.showerror("Error", str(exc))
