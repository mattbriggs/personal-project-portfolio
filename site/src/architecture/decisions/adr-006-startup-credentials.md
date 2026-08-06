# ADR-006: Sidecar startup credential transport

**Status:** Accepted

## Context

Open Question 9: pass the token by command-line argument or environment variable?
They differ in process-inspection exposure.

## Decision

Pass the token via the `PORTFOLIO_SIDECAR_TOKEN` environment variable (with a
stdin fallback), never as a command-line argument. The port — non-secret — is an
argument. `SidecarCommand::argv` deliberately excludes the token, verified by a
Rust unit test.

## Consequences

- The token never appears in `ps`/process listings.
- The sidecar reads the token via `read_startup_token()`.
