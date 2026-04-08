"""Weekly review form view."""

import logging
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any

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
        # Week selector
        top = ttk.Frame(self)
        top.pack(fill="x", padx=8, pady=4)

        ttk.Label(top, text="Week:").pack(side="left")
        self._week_var = tk.StringVar(value=self._controller._weeks.current_week_key())
        ttk.Entry(top, textvariable=self._week_var, width=10).pack(side="left", padx=4)
        ttk.Button(top, text="Load", command=self._load_review).pack(side="left")
        ttk.Button(top, text="Save Review", command=self._save_review).pack(
            side="right", padx=4
        )

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=8)

        # Scrollable form
        canvas = tk.Canvas(self)
        scroll = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self._form = ttk.Frame(canvas)
        self._form.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=self._form, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True, padx=8)

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
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def refresh(self) -> None:
        """Public refresh hook."""
        pass  # review form doesn't auto-refresh on external events
