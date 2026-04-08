"""Split-pane Markdown plan editor with debounced live preview."""

import logging
import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

logger = logging.getLogger(__name__)

# Debounce delay in milliseconds (REQ-PLN-005).
_DEBOUNCE_MS = 500


class PlanEditor(ttk.PanedWindow):
    """A split-pane widget with a Markdown text editor on the left and an
    HTML preview on the right.

    The preview auto-refreshes with a debounce delay of ≤500ms after the
    user stops typing.  Plan content auto-saves on every edit.

    :param parent: Parent Tk widget.
    :param on_save: Callback invoked with the current Markdown text when content
        changes (used to persist to the database).
    :param render_fn: Callable that converts Markdown text to an HTML string.
    :param kwargs: Additional keyword arguments forwarded to :class:`ttk.PanedWindow`.
    """

    def __init__(
        self,
        parent: tk.Widget,
        on_save: Callable[[str], None],
        render_fn: Callable[[str], str],
        **kwargs: object,
    ) -> None:
        kwargs.setdefault("orient", tk.HORIZONTAL)  # type: ignore[arg-type]
        super().__init__(parent, **kwargs)  # type: ignore[arg-type]

        self._on_save = on_save
        self._render_fn = render_fn
        self._debounce_id: str | None = None

        # Left pane: raw Markdown editor
        left = ttk.Frame(self)
        self.add(left, weight=1)
        ttk.Label(left, text="Markdown source").pack(anchor="w", padx=4, pady=(4, 0))
        self._editor = tk.Text(left, wrap="word", undo=True)
        editor_scroll = ttk.Scrollbar(left, command=self._editor.yview)
        self._editor.configure(yscrollcommand=editor_scroll.set)
        editor_scroll.pack(side="right", fill="y")
        self._editor.pack(fill="both", expand=True, padx=4, pady=4)
        self._editor.bind("<<Modified>>", self._on_modified)

        # Right pane: rendered HTML preview
        right = ttk.Frame(self)
        self.add(right, weight=1)
        ttk.Label(right, text="Preview").pack(anchor="w", padx=4, pady=(4, 0))
        self._preview_frame = self._build_preview(right)

    def _build_preview(self, parent: ttk.Frame) -> tk.Widget:
        """Attempt to build a tkinterweb HtmlFrame; fall back to a Text widget.

        :param parent: Parent frame for the preview pane.
        :returns: The created preview widget.
        :rtype: tk.Widget
        """
        try:
            from tkinterweb import HtmlFrame  # type: ignore[import-untyped]

            frame = HtmlFrame(parent, messages_enabled=False)
            frame.pack(fill="both", expand=True, padx=4, pady=4)
            self._html_frame: HtmlFrame | None = frame
            return frame
        except ImportError:
            logger.warning(
                "tkinterweb not installed — falling back to plain-text preview."
            )
            self._html_frame = None
            text = tk.Text(parent, wrap="word", state="disabled")
            scroll = ttk.Scrollbar(parent, command=text.yview)
            text.configure(yscrollcommand=scroll.set)
            scroll.pack(side="right", fill="y")
            text.pack(fill="both", expand=True, padx=4, pady=4)
            return text

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_content(self, markdown_text: str) -> None:
        """Load Markdown content into the editor without triggering auto-save.

        :param markdown_text: The Markdown text to display.
        :type markdown_text: str
        """
        self._editor.edit_modified(False)
        self._editor.delete("1.0", tk.END)
        self._editor.insert("1.0", markdown_text)
        self._editor.edit_modified(False)
        self._refresh_preview(markdown_text)

    def get_content(self) -> str:
        """Return the current raw Markdown text from the editor.

        :rtype: str
        """
        return self._editor.get("1.0", tk.END).rstrip("\n")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _on_modified(self, _event: object) -> None:
        """Handle the Tk ``<<Modified>>`` virtual event."""
        if not self._editor.edit_modified():
            return
        self._editor.edit_modified(False)

        text = self.get_content()

        # Auto-save immediately (REQ-PLN-006)
        try:
            self._on_save(text)
        except Exception:
            logger.exception("Error saving plan content")

        # Debounce preview refresh (REQ-PLN-005)
        if self._debounce_id:
            self.after_cancel(self._debounce_id)
        self._debounce_id = self.after(_DEBOUNCE_MS, self._refresh_preview, text)

    def _refresh_preview(self, text: str) -> None:
        """Render *text* and update the preview pane.

        :param text: Current Markdown content.
        """
        try:
            html = self._render_fn(text)
        except Exception:
            logger.exception("Error rendering plan preview")
            html = "<p><em>Preview unavailable.</em></p>"

        if self._html_frame is not None:
            self._html_frame.load_html(html)
        else:
            # Fallback: show raw HTML in a disabled Text widget
            preview = self._preview_frame
            if isinstance(preview, tk.Text):
                preview.configure(state="normal")
                preview.delete("1.0", tk.END)
                preview.insert("1.0", html)
                preview.configure(state="disabled")
