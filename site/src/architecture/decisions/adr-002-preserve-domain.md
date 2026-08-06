# ADR-002: Preserve Python domain and SQLite behavior

**Status:** Accepted

## Context

This is a runtime-shell migration, not a redesign. Existing databases (schema
v1–v4) and scoring semantics must keep working.

## Decision

Port the scoring policy, ISO week logic, slug generation, and migration runner
verbatim from the Tkinter app into `backend/src/portfolio_manager/domain` and
`.../infrastructure/db`. Keep domain entities as dataclasses; use Pydantic only
at the API/config boundary. Retain the `sqlite3` repositories (no ORM).

## Consequences

- Legacy databases open without manual conversion (verified by
  `tests/compatibility/test_legacy_db.py`).
- One intentional deviation: cancelled milestones are now excluded from the
  scoring denominator, per the SRS explicit rule (the Tkinter `COUNT(*)` counted
  them). Documented here and covered by tests.
