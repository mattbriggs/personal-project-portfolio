# Mermaid Diagrams Not Rendering in Plan Documents

Mermaid diagram blocks in a project plan document display as raw text instead of rendered diagrams.

In the plan document preview panel, a fenced code block tagged as `mermaid` is displayed as plain text rather than as a visual diagram.

**The `tkinterweb` library is not installed.** Without `tkinterweb`, the plan document preview falls back to a plain-text renderer that does not execute JavaScript or Mermaid.

1.  Activate the virtual environment and install `tkinterweb`:

    ```
    source .venv/bin/activate
    pip install tkinterweb
    ```

2.  Restart Portfolio Manager.

3.  Open the plan document and click **Preview**.

    Mermaid diagrams should now render in the preview panel.


**Internet access is unavailable.** Mermaid rendering uses the Mermaid.js library loaded from a CDN. If the host machine has no internet access, the diagram cannot render.

1.  Verify internet connectivity from the machine running Portfolio Manager.

2.  If the machine is offline intentionally, use the plan document in edit mode. Diagrams are preserved as source text and render correctly when connectivity is restored.


**The Mermaid diagram contains a syntax error.**

1.  Click **Edit** to open the plan document editor.

2.  Review the Mermaid code block for syntax errors. Common issues include:

    -   Missing opening keyword \(`flowchart TD`, `sequenceDiagram`, and so on\)
    -   Arrows written as `->` instead of `-->`
    -   Node labels containing unescaped special characters
3.  Correct the syntax, then click **Preview** to verify the diagram renders.


