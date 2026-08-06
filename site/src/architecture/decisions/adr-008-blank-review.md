# ADR-008: Blank weekly review persistence

**Status:** Accepted

## Context

Open Question 2: does `GET /reviews/{week_key}` persist a blank review or return
a transient one?

## Decision

Preserve the Tkinter behavior: `ReviewService.get_or_create` returns a
**transient** blank review (with the derived date range and `id == 0`) that is
**not** written to the database until the user explicitly saves it. Verified by
`test_get_or_create_returns_transient_blank`.

## Consequences

- No empty review rows accumulate for merely-viewed weeks.
- The renderer shows "(not yet saved)" until the first save.
