"""Milestone tracking view — table with popup create/edit."""

import logging
import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk
from typing import Any

from portfolio_manager.utils.date_utils import to_week_key

logger = logging.getLogger(__name__)

_STATUSES = ("backlog", "planned", "doing", "done", "cancelled")


class _MilestoneDialog(tk.Toplevel):
    """Modal dialog for creating or editing a milestone.

    :param parent: Parent widget.
    :param controller: MilestoneController instance.
    :param project_id: Parent project primary key.
    :param milestone: Existing milestone for edit mode; ``None`` for create mode.
    :param total_min: Pre-computed total session minutes (read-only display).
    """

    def __init__(
        self,
        parent: tk.Widget,
        controller: Any,
        project_id: int,
        milestone: Any = None,
        total_min: int = 0,
    ) -> None:
        super().__init__(parent)
        self._controller = controller
        self._project_id = project_id
        self._milestone = milestone
        self._total_min = total_min
        self.saved = False

        self.title("Edit Milestone" if milestone else "New Milestone")
        self.resizable(False, False)
        self.grab_set()
        self._build_ui()
        if milestone:
            self._populate(milestone)
        self.bind("<Escape>", lambda _e: self.destroy())

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        form = ttk.Frame(self, padding=12)
        form.pack(fill="both", expand=True)
        row = 0

        # Milestone name (description field)
        ttk.Label(form, text="Milestone:").grid(row=row, column=0, sticky="e", padx=6, pady=4)
        self._name_var = tk.StringVar()
        ttk.Entry(form, textvariable=self._name_var, width=36).grid(
            row=row, column=1, columnspan=2, sticky="ew", padx=6, pady=4
        )
        row += 1

        # Target date
        ttk.Label(form, text="Target (YYYY-MM-DD):").grid(
            row=row, column=0, sticky="e", padx=6, pady=4
        )
        self._target_var = tk.StringVar()
        target_frame = ttk.Frame(form)
        target_frame.grid(row=row, column=1, columnspan=2, sticky="w", padx=6, pady=4)
        ttk.Entry(target_frame, textvariable=self._target_var, width=14).pack(side="left")
        ttk.Button(
            target_frame, text="Today", width=6,
            command=lambda: self._target_var.set(date.today().isoformat()),
        ).pack(side="left", padx=(4, 0))
        row += 1

        # Status
        ttk.Label(form, text="Status:").grid(row=row, column=0, sticky="e", padx=6, pady=4)
        self._status_var = tk.StringVar(value="backlog")
        ttk.Combobox(
            form,
            textvariable=self._status_var,
            values=list(_STATUSES),
            state="readonly",
            width=14,
        ).grid(row=row, column=1, sticky="w", padx=6, pady=4)
        row += 1

        # Read-only info: Week + Total Min
        info = ttk.Frame(form)
        info.grid(row=row, column=0, columnspan=3, sticky="w", padx=6, pady=2)
        ttk.Label(info, text="Week:").pack(side="left")
        self._week_label = ttk.Label(info, text="—", foreground="#555")
        self._week_label.pack(side="left", padx=(4, 20))
        ttk.Label(info, text="Total Min:").pack(side="left")
        ttk.Label(
            info,
            text=str(self._total_min) if self._total_min else "—",
            foreground="#555",
        ).pack(side="left", padx=4)
        row += 1

        # Live week update when target date changes
        self._target_var.trace_add("write", self._on_target_change)

        # Description (notes field — longer text)
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

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _on_target_change(self, *_args: object) -> None:
        """Update the derived Week label whenever the target date field changes."""
        raw = self._target_var.get().strip()
        try:
            self._week_label.configure(text=to_week_key(date.fromisoformat(raw)))
        except ValueError:
            self._week_label.configure(text="—")

    def _populate(self, milestone: Any) -> None:
        self._name_var.set(milestone.description)
        self._target_var.set(
            milestone.target_date.isoformat() if milestone.target_date else ""
        )
        self._status_var.set(milestone.status)
        self._notes_text.delete("1.0", tk.END)
        self._notes_text.insert("1.0", milestone.notes)

    def _on_save(self) -> None:
        description = self._name_var.get().strip()
        if not description:
            messagebox.showwarning("Validation", "Milestone name is required.", parent=self)
            return

        raw = self._target_var.get().strip()
        target: date | None = None
        if raw:
            try:
                target = date.fromisoformat(raw)
            except ValueError:
                messagebox.showerror("Invalid Date", "Date must be YYYY-MM-DD.", parent=self)
                return

        notes = self._notes_text.get("1.0", tk.END).strip()
        status = self._status_var.get()

        try:
            if self._milestone is None:
                self._controller.add_milestone(
                    self._project_id,
                    description,
                    target_date=target,
                    notes=notes,
                    status=status,
                )
            else:
                self._controller.update_milestone_fields(
                    self._milestone.id,
                    description,
                    target_date=target,
                    notes=notes,
                    status=status,
                )
            self.saved = True
            self.destroy()
        except Exception as exc:
            messagebox.showerror("Error", str(exc), parent=self)


# ---------------------------------------------------------------------------
# Main view
# ---------------------------------------------------------------------------


class MilestoneView(ttk.Frame):
    """Milestone tracking tab — full-width table with popup create/edit.

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
        self._milestones_cache: list[Any] = []  # list of (Milestone, total_min)
        self._build_ui()
        self.refresh_projects()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        # ── Toolbar: project filter + New Milestone ──────────────────
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=8, pady=(6, 2))

        ttk.Label(toolbar, text="Project:").pack(side="left")
        self._project_var = tk.StringVar()
        self._project_combo = ttk.Combobox(
            toolbar, textvariable=self._project_var, width=25, state="readonly"
        )
        self._project_combo.pack(side="left", padx=4)
        self._project_combo.bind("<<ComboboxSelected>>", self._on_project_change)

        ttk.Button(toolbar, text="New Milestone", command=self._on_new).pack(side="right")

        # ── Milestone table ───────────────────────────────────────────
        columns = ("milestone", "target", "week", "total_min", "status")
        self._tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=18,
        )
        for col, heading, width, anchor in [
            ("milestone",  "Milestone",  320, "w"),
            ("target",     "Target",     100, "center"),
            ("week",       "Week",        70, "center"),
            ("total_min",  "Total Min",   80, "center"),
            ("status",     "Status",      80, "center"),
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

    # ------------------------------------------------------------------
    # Data refresh
    # ------------------------------------------------------------------

    def refresh_projects(self) -> None:
        """Reload the project list into the project selector."""
        projects = self._projects.list_projects(status="active")
        self._project_map = {p.name: p.id for p in projects}
        self._project_combo["values"] = list(self._project_map.keys())
        if projects:
            # Preserve selection if the current project is still in the list.
            current_id = self._selected_project_id
            still_present = [p for p in projects if p.id == current_id]
            if still_present:
                idx = projects.index(still_present[0])
                self._project_combo.current(idx)
            else:
                self._project_combo.current(0)
                self._selected_project_id = projects[0].id
            self._refresh_milestones()
        else:
            self._project_combo.set("")
            self._selected_project_id = None
            self._refresh_milestones()  # clears the table

    def _on_project_change(self, _event: object) -> None:
        self._selected_project_id = self._project_map.get(self._project_var.get())
        self._refresh_milestones()

    def _refresh_milestones(self) -> None:
        """Reload milestones for the selected project."""
        for item in self._tree.get_children():
            self._tree.delete(item)
        self._milestone_ids = []
        self._milestones_cache = []

        if self._selected_project_id is None:
            return

        rows = self._controller.list_milestones_with_totals(self._selected_project_id)
        self._milestones_cache = rows

        for ms, total_min in rows:
            self._milestone_ids.append(ms.id)
            week_str = to_week_key(ms.target_date) if ms.target_date else "—"
            self._tree.insert(
                "",
                "end",
                values=(
                    ms.description,
                    ms.target_date.isoformat() if ms.target_date else "—",
                    week_str,
                    total_min if total_min else "—",
                    ms.status,
                ),
            )

    def refresh(self) -> None:
        """Public refresh hook (called by event bus subscribers)."""
        self._refresh_milestones()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _selected_idx(self) -> int | None:
        sel = self._tree.selection()
        if not sel:
            return None
        return self._tree.index(sel[0])

    def _on_new(self) -> None:
        if self._selected_project_id is None:
            messagebox.showwarning("No Project", "Select a project first.")
            return
        dialog = _MilestoneDialog(self, self._controller, self._selected_project_id)
        self.wait_window(dialog)
        if dialog.saved:
            self._refresh_milestones()

    def _on_double_click(self, _event: object) -> None:
        idx = self._selected_idx()
        if idx is None or idx >= len(self._milestones_cache):
            return
        ms, total_min = self._milestones_cache[idx]
        dialog = _MilestoneDialog(
            self,
            self._controller,
            ms.project_id,
            milestone=ms,
            total_min=total_min,
        )
        self.wait_window(dialog)
        if dialog.saved:
            self._refresh_milestones()

    def _on_set_status(self) -> None:
        idx = self._selected_idx()
        if idx is None:
            messagebox.showwarning("No Selection", "Select a milestone first.")
            return
        try:
            self._controller.set_milestone_status(
                self._milestone_ids[idx], self._status_var.get()
            )
            self._refresh_milestones()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _on_delete(self) -> None:
        idx = self._selected_idx()
        if idx is None:
            messagebox.showwarning("No Selection", "Select a milestone first.")
            return
        if messagebox.askyesno("Delete Milestone", "Delete this milestone?"):
            self._controller.delete_milestone(self._milestone_ids[idx])
            self._refresh_milestones()
