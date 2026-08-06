# ADR-005: OpenAPI → TypeScript generation

**Status:** Accepted

## Decision

`scripts/generate_openapi.py` builds the FastAPI app in-process, emits a
deterministic `openapi.json`, and generates `frontend/src/contracts/generated/
types.ts`. Generated files are build artifacts; a CI drift check regenerates and
fails on any diff. Hand-authored types in `frontend/src/contracts/index.ts` keep
the renderer type-checking without requiring the generated file at dev time.

## Consequences

- Contract drift between backend and renderer is caught in CI.
- The generator is dependency-free; swap for `openapi-typescript` later if richer
  output is needed.
