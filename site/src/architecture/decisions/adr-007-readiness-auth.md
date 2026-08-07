# ADR-007: Readiness endpoint authentication

**Status:** Accepted

## Context

Open Question 8: should `/ready` require the token?

## Decision

Treat `/health` and `/ready` as unauthenticated health routes. Neither returns
sensitive data (`/health` → `{"status":"ok"}`; `/ready` → `{"status":"ready"}`
after a trivial `SELECT 1`). Every other route requires `X-API-Key`. This lets
the Rust supervisor poll readiness before the token handshake is relevant.

## Consequences

- The supervisor distinguishes liveness (`/health`) from readiness (`/ready`).
- Contract tests assert both are reachable without a token and that business
  routes are not.
