# Write a Project Plan Document

Use the project plan editor to capture outlines, research notes, diagrams, and any reference material that supports your work on a project.

Each project includes a Markdown plan document. The editor offers a preview panel that renders formatted text and Mermaid diagrams. All changes save automatically as you type.

1.  Click the **Projects** tab and select the project you want to edit.

2.  Click **Edit Project**.

    The Project dialog opens. The lower half of the dialog shows the plan document in preview mode.

3.  Click **Edit** to switch the plan document to edit mode.

    A Markdown text editor replaces the preview panel.

4.  Write your plan document using standard Markdown syntax.

    The plan document has no required structure. Common approaches include:

    -   An outline or table of contents
    -   A goals or objectives section
    -   Reference notes or research summaries
    -   A decision log
    -   Tables of characters, chapters, modules, or tasks
    To include a Mermaid diagram, use a fenced code block with the `mermaid` language tag:

    ```
    ```mermaid
    flowchart TD
        A[Draft] --> B[Revision]
        B --> C[Final]
    ```
    ```

5.  Click **Preview** to review the rendered output.

    The editor switches to preview mode. Markdown formatting and Mermaid diagrams render automatically. Click **Edit** to return to edit mode at any time.


Your plan document is saved automatically. There is no separate save action for plan document content.

See [Markdown and Mermaid Syntax Reference](r_markdown_syntax.md) for the full list of supported Markdown elements and Mermaid diagram types.

