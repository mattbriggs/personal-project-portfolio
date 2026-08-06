# Architecture Decision Records

Records for decisions the SRS left open or that shape the Tauri refactor. Each
ADR states context, the decision, and consequences. Status is **Accepted**
unless noted.

| ADR | Title | Decision summary |
| --- | --- | --- |
| [001](adr-001-tauri-mediated-sidecar.md) | Tauri-mediated sidecar access | Renderer reaches the sidecar only through allowlisted Tauri commands |
| [002](adr-002-preserve-domain.md) | Preserve Python domain + SQLite | Port existing scoring/week/migrations verbatim |
| [003](adr-003-query-cache.md) | Query/cache library | TanStack Query with explicit invalidation |
| [004](adr-004-ui-accessibility.md) | UI + accessibility approach | Hand-rolled accessible components, no heavy UI kit |
| [005](adr-005-openapi-typescript.md) | OpenAPI → TypeScript | Generated types as build artifacts + drift check |
| [006](adr-006-startup-credentials.md) | Startup credential transport | Token via env var / stdin, never argv |
| [007](adr-007-readiness-auth.md) | Readiness endpoint auth | `/health` and `/ready` unauthenticated (no sensitive data) |
| [008](adr-008-blank-review.md) | Blank weekly review persistence | Get-or-create returns a transient blank, not persisted |
| [009](adr-009-zero-project-score.md) | Zero-active-project portfolio score | Portfolio score is 0 when no scores exist |
| [010](adr-010-macos-arch.md) | macOS sidecar architecture | Per-arch PyInstaller binaries, universal later |
| [011](adr-011-markdown-rendering.md) | Markdown/Mermaid rendering | Render in React with bundled libraries, offline |
