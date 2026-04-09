"""Markdown plan editor — shows preview by default, with an Edit toggle."""

import logging
import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

logger = logging.getLogger(__name__)

# Debounce delay in milliseconds (REQ-PLN-005).
_DEBOUNCE_MS = 500


class PlanEditor(ttk.Frame):
    """A Markdown plan editor that defaults to a rendered preview.

    Clicking **Edit** reveals the raw Markdown editor.  Clicking **Preview**
    returns to the rendered view.  Plan content auto-saves whenever the editor
    text changes.

    :param parent: Parent Tk widget.
    :param on_save: Callback invoked with the current Markdown text when content
        changes (used to persist to the database).
    :param render_fn: Callable that converts Markdown text to an HTML string.
    :param kwargs: Additional keyword arguments forwarded to :class:`ttk.Frame`.
    """

    def __init__(
        self,
        parent: tk.Widget,
        on_save: Callable[[str], None],
        render_fn: Callable[[str], str],
        **kwargs: object,
    ) -> None:
        super().__init__(parent, **kwargs)  # type: ignore[arg-type]

        self._on_save = on_save
        self._render_fn = render_fn
        self._debounce_id: str | None = None
        self._editing = False

        # Toolbar row
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=4, pady=(4, 0))
        self._toggle_btn = ttk.Button(toolbar, text="Edit", command=self._toggle_mode)
        self._toggle_btn.pack(side="left")

        # Editor pane (hidden by default)
        self._editor_pane = ttk.Frame(self)
        ttk.Label(self._editor_pane, text="Markdown source").pack(
            anchor="w", padx=4, pady=(4, 0)
        )
        self._editor = tk.Text(self._editor_pane, wrap="word", undo=True)
        editor_scroll = ttk.Scrollbar(self._editor_pane, command=self._editor.yview)
        self._editor.configure(yscrollcommand=editor_scroll.set)
        editor_scroll.pack(side="right", fill="y")
        self._editor.pack(fill="both", expand=True, padx=4, pady=4)
        self._editor.bind("<<Modified>>", self._on_modified)

        # Preview pane (shown by default)
        self._preview_pane = ttk.Frame(self)
        self._preview_frame = self._build_preview(self._preview_pane)

        # Start in preview mode
        self._show_preview()

    # ------------------------------------------------------------------
    # Mode switching
    # ------------------------------------------------------------------

    def _show_preview(self) -> None:
        """Switch to preview-only mode."""
        self._editing = False
        self._toggle_btn.configure(text="Edit")
        self._editor_pane.pack_forget()
        self._preview_pane.pack(fill="both", expand=True)

    def _show_edit(self) -> None:
        """Switch to editor mode."""
        self._editing = True
        self._toggle_btn.configure(text="Preview")
        self._preview_pane.pack_forget()
        self._editor_pane.pack(fill="both", expand=True)

    def _toggle_mode(self) -> None:
        """Toggle between preview and edit modes."""
        if self._editing:
            # Refresh preview with current editor content before switching.
            self._refresh_preview(self.get_content())
            self._show_preview()
        else:
            self._show_edit()

    # ------------------------------------------------------------------
    # Preview construction
    # ------------------------------------------------------------------

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
