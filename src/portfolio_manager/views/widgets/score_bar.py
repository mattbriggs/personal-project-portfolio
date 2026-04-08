"""Score progress bar widget."""

import tkinter as tk
from tkinter import ttk


class ScoreBar(ttk.Frame):
    """A labelled progress bar showing a project score (0–100).

    :param parent: Parent Tk widget.
    :param score: Initial score value (0–100).
    :param kwargs: Additional keyword arguments forwarded to :class:`ttk.Frame`.
    """

    def __init__(
        self,
        parent: tk.Widget,
        score: int = 0,
        **kwargs: object,
    ) -> None:
        super().__init__(parent, **kwargs)  # type: ignore[arg-type]
        self._score_var = tk.IntVar(value=score)
        self._label_var = tk.StringVar(value=f"{score}")

        self._bar = ttk.Progressbar(
            self,
            variable=self._score_var,
            maximum=100,
            length=100,
            mode="determinate",
        )
        self._label = ttk.Label(self, textvariable=self._label_var, width=4, anchor="e")

        self._bar.pack(side="left", fill="x", expand=True)
        self._label.pack(side="left", padx=(4, 0))

    def set_score(self, score: int) -> None:
        """Update the displayed score.

        :param score: New score value (0–100).
        :type score: int
        """
        clamped = max(0, min(100, score))
        self._score_var.set(clamped)
        self._label_var.set(str(clamped))
