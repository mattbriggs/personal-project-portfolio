"""Dashboard view — portfolio summary table and status notes."""

import logging
import tkinter as tk
from tkinter import ttk
from typing import Any

from portfolio_manager.views.widgets.status_badge import StatusBadge

logger = logging.getLogger(__name__)


class DashboardView(ttk.Frame):
    """Portfolio dashboard tab — renders project rows, scores, and weekly summary.

    :param parent: Parent notebook or frame.
    :param controller: :class:`~portfolio_manager.controllers.dashboard_controller.DashboardController`
        instance that supplies dashboard data.
    :param kwargs: Forwarded to :class:`ttk.Frame`.
    """

    def __init__(self, parent: tk.Widget, controller: Any, **kwargs: object) -> None:
        super().__init__(parent, **kwargs)  # type: ignore[arg-type]
        self._controller = controller
        self._build_ui()
        controller.bind_view(self)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """Build the dashboard layout."""
        # Header row
        header = ttk.Frame(self)
        header.pack(fill="x", padx=8, pady=(8, 4))

        self._week_label = ttk.Label(header, text="", font=("", 12, "bold"))
        self._week_label.pack(side="left")
        self._range_label = ttk.Label(header, text="", foreground="#555")
        self._range_label.pack(side="left", padx=(8, 0))

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=8)

        # Project table
        columns = ("project", "status", "planned", "done", "remaining", "score")
        self._tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=10,
        )
        for col, heading, width in [
            ("project",   "Project",   200),
            ("status",    "Status",     80),
            ("planned",   "Planned",    60),
            ("done",      "Done",       60),
            ("remaining", "Remaining",  80),
            ("score",     "Score",      60),
        ]:
            self._tree.heading(col, text=heading)
            self._tree.column(col, width=width, anchor="center")
        self._tree.column("project", anchor="w")

        scroll = ttk.Scrollbar(self, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y", padx=(0, 8))
        self._tree.pack(fill="both", expand=True, padx=8, pady=4)

        # Summary row
        summary_frame = ttk.LabelFrame(self, text="Portfolio Summary")
        summary_frame.pack(fill="x", padx=8, pady=4)

        self._portfolio_score_label = ttk.Label(summary_frame, text="Score: —")
        self._portfolio_score_label.pack(side="left", padx=12, pady=4)

        self._portfolio_status_badge = StatusBadge(summary_frame)
        self._portfolio_status_badge.pack(side="left", padx=8)

        # Status notes
        notes_frame = ttk.LabelFrame(self, text="Status Notes")
        notes_frame.pack(fill="x", padx=8, pady=(0, 8))

        self._notes_text = tk.Text(
            notes_frame, height=4, state="disabled", wrap="word"
        )
        self._notes_text.pack(fill="x", padx=4, pady=4)

    # ------------------------------------------------------------------
    # Data refresh
    # ------------------------------------------------------------------

    def refresh(self) -> None:
        """Reload all dashboard data from the controller and redisplay."""
        try:
            data = self._controller.get_dashboard_data()
        except Exception:
            logger.exception("Failed to load dashboard data")
            return

        week_key: str = data["week_key"]
        date_range: str = data["date_range"]
        rows: list[dict] = data["rows"]
        portfolio_score: int = data["portfolio_score"]
        portfolio_status: str = data["portfolio_status"]

        self._week_label.configure(text=f"Week {week_key}")
        self._range_label.configure(text=date_range)

        # Clear tree
        for item in self._tree.get_children():
            self._tree.delete(item)

        # Populate rows
        notes_lines: list[str] = []
        total_planned = total_done = total_remaining = 0

        for row in rows:
            project = row["project"]
            score_obj = row["score"]
            planned = row["planned"]
            done = row["completed"]
            remaining = row["remaining"]

            total_planned += planned
            total_done += done
            total_remaining += remaining

            self._tree.insert(
                "",
                "end",
                values=(
                    project.name,
                    score_obj.status.capitalize(),
                    planned,
                    done,
                    remaining,
                    score_obj.score,
                ),
            )
            if score_obj.status_note:
                notes_lines.append(f"• {project.name}: {score_obj.status_note}")

        self._portfolio_score_label.configure(
            text=(
                f"Score: {portfolio_score}  |  "
                f"Planned: {total_planned}  "
                f"Done: {total_done}  "
                f"Remaining: {total_remaining}"
            )
        )
        self._portfolio_status_badge.set_status(portfolio_status)

        notes_text = "\n".join(notes_lines) if notes_lines else "No status notes."
        self._notes_text.configure(state="normal")
        self._notes_text.delete("1.0", tk.END)
        self._notes_text.insert("1.0", notes_text)
        self._notes_text.configure(state="disabled")
