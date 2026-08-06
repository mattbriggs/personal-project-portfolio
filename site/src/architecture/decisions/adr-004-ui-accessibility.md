# ADR-004: UI and accessibility approach

**Status:** Accepted

## Decision

Use hand-authored, accessible components rather than a heavy UI kit: labelled
inputs, a focus-trapped `Dialog` that restores focus on close, non-color status
indicators (`StatusIndicator` pairs color with text and a glyph), and keyboard
operability. This keeps the bundle small and offline-friendly.

## Consequences

- Full control over accessibility semantics.
- More component code to maintain, covered by React Testing Library tests.
