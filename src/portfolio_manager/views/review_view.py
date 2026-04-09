"""Weekly review form view."""

import logging
import tkinter as tk
from datetime import timedelta
from tkinter import messagebox, ttk
from typing import Any

from portfolio_manager.utils.date_utils import to_week_key, week_key_to_date_range

logger = logging.getLogger(__name__)

# Fields in the weekly review form: (attribute_name, label_text, multiline)
_FIELDS = [
    ("what_moved", "What moved:", True),
    ("what_stalled", "What stalled:", True),
    ("signals", "Signals:", True),
    ("decision_next_week", "Decision for next week:", True),
    ("primary_focus", "Primary focus:", False),
    ("project_to_deprioritize", "Project to deprioritize:", False),
    ("risk_to_watch", "Risk to watch:", False),
    ("first_session_target", "First session target:", False),
]


class ReviewView(ttk.Frame):
    """Weekly review tab — form for capturing structured weekly reflections.

    :param parent: Parent widget.
    :param controller: :class:`~portfolio_manager.controllers.review_controller.ReviewController`.
    :param kwargs: Forwarded to :class:`ttk.Frame`.
    """

    def __init__(self, parent: tk.Widget, controller: Any, **kwargs: object) -> None:
        super().__init__(parent, **kwargs)  # type: ignore[arg-type]
        self._controller = controller
        self._review: Any = None
        self._vars: dict[str, tk.StringVar | tk.Text] = {}
        self._build_ui()
        self._load_review()

    def _build_ui(self) -> None:
        """Build the review form layout."""
        # Week selector toolbar
        top = ttk.Frame(self)
        top.pack(fill="x", padx=8, pady=4)

        ttk.Label(top, text="Week:").pack(side="left")
        ttk.Button(top, text="<", command=self._prev_week, width=2).pack(side="left")
        self._week_var = tk.StringVar(value=self._controller._weeks.current_week_key())
        ttk.Entry(top, textvariable=self._week_var, width=10).pack(side="left", padx=2)
        ttk.Button(top, text=">", command=self._next_week, width=2).pack(side="left")
        ttk.Button(top, text="Load", command=self._load_review).pack(side="left", padx=4)
        ttk.Button(top, text="Save Review", command=self._save_review).pack(
            side="right", padx=4
        )

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=8)

        # Two-column layout: left = past reviews list, right = form
        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, padx=8, pady=4)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        # Left: past reviews listbox
        left = ttk.Frame(body, width=150)
        left.grid(row=0, column=0, sticky="nswe", padx=(0, 6))
        left.grid_propagate(False)
        left.rowconfigure(1, weight=1)
        ttk.Label(left, text="Past Reviews", font=("", 9, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 2)
        )
        self._history_listbox = tk.Listbox(left, selectmode="single", width=14, exportselection=False)
        hist_scroll = ttk.Scrollbar(left, orient="vertical", command=self._history_listbox.yview)
        self._history_listbox.configure(yscrollcommand=hist_scroll.set)
        self._history_listbox.grid(row=1, column=0, sticky="nswe")
        hist_scroll.grid(row=1, column=1, sticky="ns")
        left.columnconfigure(0, weight=1)
        self._history_listbox.bind("<<ListboxSelect>>", self._on_history_select)
        self._history_keys: list[str] = []

        # Right: scrollable form
        right = ttk.Frame(body)
        right.grid(row=0, column=1, sticky="nswe")
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)

        canvas = tk.Canvas(right)
        scroll = ttk.Scrollbar(right, orient="vertical", command=canvas.yview)
        self._form = ttk.Frame(canvas)
        self._form.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=self._form, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        for attr, label, multiline in _FIELDS:
            ttk.Label(self._form, text=label).pack(anchor="w", padx=4, pady=(6, 0))
            if multiline:
                text = tk.Text(self._form, height=3, wrap="word")
                text.pack(fill="x", padx=4, pady=(0, 2))
                self._vars[attr] = text
            else:
                var = tk.StringVar()
                ttk.Entry(self._form, textvariable=var).pack(
                    fill="x", padx=4, pady=(0, 2)
                )
                self._vars[attr] = var

    def _load_review(self) -> None:
        """Load (or create) the review for the selected week."""
        week_key = self._week_var.get().strip()
        self._review = self._controller.get_or_create_review(week_key)
        for attr, _label, multiline in _FIELDS:
            value = getattr(self._review, attr, "")
            widget = self._vars[attr]
            if multiline:
                assert isinstance(widget, tk.Text)
                widget.delete("1.0", tk.END)
                widget.insert("1.0", value)
            else:
                assert isinstance(widget, tk.StringVar)
                widget.set(value)
        self._refresh_history()

    def _refresh_history(self) -> None:
        """Reload the past-reviews listbox from the controller."""
        self._history_listbox.delete(0, tk.END)
        self._history_keys = []
        for review in self._controller.list_reviews():
            self._history_listbox.insert(tk.END, review.week_key)
            self._history_keys.append(review.week_key)
        # Highlight the currently displayed week
        current = self._week_var.get().strip()
        for i, key in enumerate(self._history_keys):
            if key == current:
                self._history_listbox.selection_set(i)
                self._history_listbox.see(i)
                break

    def _on_history_select(self, _event: object) -> None:
        """Load the review selected in the history listbox."""
        sel = self._history_listbox.curselection()
        if not sel:
            return
        week_key = self._history_keys[sel[0]]
        self._week_var.set(week_key)
        self._load_review()

    def _save_review(self) -> None:
        """Read form values and persist the review."""
        if self._review is None:
            return
        for attr, _label, multiline in _FIELDS:
            widget = self._vars[attr]
            if multiline:
                assert isinstance(widget, tk.Text)
                setattr(self._review, attr, widget.get("1.0", tk.END).strip())
            else:
                assert isinstance(widget, tk.StringVar)
                setattr(self._review, attr, widget.get())
        try:
            self._review = self._controller.save_review(self._review)
            messagebox.showinfo("Saved", "Weekly review saved.")
            self._refresh_history()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def navigate_to_week(self, week_key: str) -> None:
        """Navigate to *week_key* and reload the review form.

        :param week_key: Week key in ``YYYY.W`` format.
        """
        self._week_var.set(week_key)
        self._load_review()

    def _prev_week(self) -> None:
        """Step back one week."""
        try:
            monday, _ = week_key_to_date_range(self._week_var.get().strip())
            self._week_var.set(to_week_key(monday - timedelta(weeks=1)))
            self._load_review()
        except ValueError:
            pass

    def _next_week(self) -> None:
        """Step forward one week."""
        try:
            monday, _ = week_key_to_date_range(self._week_var.get().strip())
            self._week_var.set(to_week_key(monday + timedelta(weeks=1)))
            self._load_review()
        except ValueError:
            pass

    def refresh(self) -> None:
        """Public refresh hook."""
        pass  # review form doesn't auto-refresh on external events
