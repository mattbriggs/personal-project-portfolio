# ADR-003: Query/cache library

**Status:** Accepted

## Context

The Tkinter app refreshed views via an event bus. The renderer needs an
equivalent that keeps server-backed state fresh.

## Decision

Use **TanStack Query** for all server-backed state. Mutations trigger explicit
query invalidation through `useInvalidate` (`frontend/src/hooks/useInvalidate.ts`),
mapping each mutation to its dependent queries (SRS §4.9). No global event bus is
recreated.

## Consequences

- Server state, form-draft state, and workspace state are cleanly separated.
- Invalidation rules are centralized and testable.
