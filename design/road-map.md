# Design Roadmap

Design-level work items that are not yet scheduled into a release. Release
sequencing lives in [DEV-AND-ROADMAP.md](../DEV-AND-ROADMAP.md); this file
holds items that need a design or contract decision before they can be planned.

## UI Parity With The Legacy Tkinter App

The React views now match the Tkinter UI for scrolling, create/edit dialogs,
row selection, status actions, deletion, and the weekly-review expand editor.
Two gaps remain, each deferred for a specific reason rather than by oversight.

### Milestone and session counts in the Projects table

The Tkinter Projects tab shows a **Milestones (count)** and **Sessions (count)**
column per project. The React table cannot show them today because the
`Project` contract carries no counts — only the dashboard aggregates them, and
that aggregation is per-week rather than per-project lifetime.

Deciding this needs a contract choice:

- Add the two counts to the project list response, which costs a join on every
  project list call, or
- Add a separate counts endpoint the Projects view fetches alongside the list,
  which keeps the list response lean but adds a round trip, or
- Drop the columns and treat the dashboard as the only place counts appear.

Whichever is chosen, the change touches `contracts/`, the project repository,
the generated TypeScript types, and the traceability matrix.

### Week selector inside the Sessions tab

The Tkinter Sessions tab has its own week entry with previous/next/Load
buttons. The React app has a persistent week rail down the left side that
already drives the Sessions and Weekly Review views, so an in-tab selector
would be a second control for the same state.

This is a UX decision, not a technical one: either accept the rail as the
single week control and treat the Tkinter selector as superseded, or add the
in-tab selector back for users who navigate by typing a week key. If it is
added, it must write through to the same workspace state the rail uses so the
two cannot disagree.

## Notes

The `docs/` directory is generated output; edit `site/src/`. The user guide
under `site/src/guide/` is generated from the DITA sources in `guide/`. See the
development guide for the full build pipeline.
