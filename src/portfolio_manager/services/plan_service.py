"""Service for managing per-project plan documents.

Handles persistence of Markdown content and converts it to an HTML page
ready for display in an embedded WebKit renderer (``tkinterweb``).

Rendering pipeline (Appendix B of the SRS):

    plan_content (Markdown TEXT)
        → markdown.convert()          — produces HTML body fragment
        → inject Mermaid.js CDN tag   — enables diagram rendering
        → wrap in minimal HTML shell  — full <html> document
        → caller passes to tkinterweb HtmlFrame.load_html()
"""

import logging

from portfolio_manager.repositories.project_repo import ProjectRepository

logger = logging.getLogger(__name__)

# Mermaid.js loaded from CDN with startOnLoad: true so diagrams render on page load.
_MERMAID_SCRIPT = """\
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
  mermaid.initialize({ startOnLoad: true });
</script>"""

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         font-size: 14px; line-height: 1.6; padding: 12px 16px;
         color: #1a1a1a; background: #ffffff; }}
  h1, h2, h3 {{ margin-top: 1.2em; margin-bottom: 0.4em; }}
  code {{ background: #f4f4f4; padding: 0.1em 0.3em; border-radius: 3px; }}
  pre  {{ background: #f4f4f4; padding: 12px; border-radius: 4px; overflow-x: auto; }}
  blockquote {{ border-left: 3px solid #ccc; margin: 0; padding-left: 12px; color: #555; }}
  .mermaid {{ text-align: center; }}
</style>
{mermaid_script}
</head>
<body>
{body}
</body>
</html>"""


class PlanService:
    """Manages the plan document for a project.

    :param project_repo: Repository used to read and write plan content.
    :type project_repo: ProjectRepository
    """

    def __init__(self, project_repo: ProjectRepository) -> None:
        self._projects = project_repo
        self._md = self._make_markdown_converter()

    @staticmethod
    def _make_markdown_converter() -> object:
        """Initialise a :mod:`markdown` converter with useful extensions.

        Returns a bare :class:`str` converter as fallback when ``markdown``
        is not installed (should not happen after ``pip install``).

        :rtype: object with a ``.convert(text) -> str`` method
        """
        try:
            import markdown  # type: ignore[import-untyped]

            return markdown.Markdown(
                extensions=["fenced_code", "tables", "toc", "nl2br"],
                extension_configs={},
            )
        except ImportError:
            logger.warning("'markdown' library not installed — plain-text fallback.")

            class _Passthrough:
                def convert(self, text: str) -> str:  # noqa: D102
                    return f"<pre>{text}</pre>"

                def reset(self) -> None:  # noqa: D102
                    pass

            return _Passthrough()

    def get_plan(self, project_id: int) -> str:
        """Return the raw Markdown plan content for a project.

        :param project_id: Target project.
        :type project_id: int
        :returns: Markdown text (may be empty string).
        :rtype: str
        """
        project = self._projects.get(project_id)
        return project.plan_content

    def save_plan(self, project_id: int, content: str) -> None:
        """Persist updated plan Markdown to the database.

        Updating the plan content triggers the ``project_updated_at`` database
        trigger, refreshing ``updated_at`` automatically.

        :param project_id: Target project.
        :type project_id: int
        :param content: New Markdown text.
        :type content: str
        """
        self._projects.update_plan(project_id, content)
        logger.debug("Saved plan for project %d (%d chars)", project_id, len(content))

    def render_html(self, markdown_text: str) -> str:
        """Convert Markdown text to a full HTML page with Mermaid support.

        :param markdown_text: Raw Markdown text (may contain fenced Mermaid blocks).
        :type markdown_text: str
        :returns: Complete HTML document string suitable for ``load_html()``.
        :rtype: str
        """
        self._md.reset()  # type: ignore[attr-defined]
        body_html = self._md.convert(markdown_text)  # type: ignore[attr-defined]
        return _HTML_TEMPLATE.format(
            mermaid_script=_MERMAID_SCRIPT,
            body=body_html,
        )
