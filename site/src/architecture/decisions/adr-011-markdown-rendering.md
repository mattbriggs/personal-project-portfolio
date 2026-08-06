# ADR-011: Frontend-only Markdown/Mermaid rendering

**Status:** Accepted

## Context

Open Question 15: is `POST /plans/render` needed, or can rendering stay in React?

## Decision

Render Markdown and Mermaid **in the renderer** with bundled libraries
(`react-markdown`, `remark-gfm`, `mermaid`, `dompurify`) — no CDN, works offline.
The backend only persists raw plan text; there is no `/plans/render` endpoint.
Mermaid runs with `securityLevel: "strict"` and its SVG output is sanitized with
DOMPurify. Invalid Mermaid preserves the source and shows an explicit error.

## Consequences

- No duplicated rendering semantics across Python and React.
- Offline plan preview works with no network dependency.
