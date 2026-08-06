# ADR-001: Tauri-mediated sidecar access

**Status:** Accepted

## Context

The SRS requires that the renderer never contact the Python sidecar directly and
that the sidecar port and token never reach the renderer.

## Decision

The renderer calls only explicit, allowlisted Tauri commands
(`src-tauri/src/commands/*`). Each command maps one operation to one fixed HTTP
method and path via an internal Rust forwarder that attaches the `X-API-Key`
token. There is no generic command accepting an arbitrary method/path. The port
and token live only in Rust in-memory `AppState` (token wrapped in
`secrecy::SecretString`).

## Consequences

- The renderer contains no HTTP code (enforced by
  `scripts/verify_no_renderer_http.py`).
- Adding an endpoint requires adding a command — a deliberate, auditable step.
- The command list in `src-tauri/src/lib.rs` is the complete renderer surface.
