# ADR-010: macOS sidecar architecture strategy

**Status:** Accepted (initial)

## Context

Open Question 12: universal macOS artifact or separate Apple Silicon / Intel?

## Decision

For the first release, build the PyInstaller sidecar per host architecture and
bundle it as a Tauri `externalBin` with a target-triple suffix. A universal
(`lipo`-merged) binary is deferred until multi-arch CI is in place.

## Consequences

- `scripts/build_sidecar.py` names output by target triple.
- Cross-arch universal packaging is future work (Phase 16).
