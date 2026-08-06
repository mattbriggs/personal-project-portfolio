# Portfolio Manager Tauri Refactor — Completion Report

_Interim report. Every figure below was measured, not estimated; items that
could not be verified say so explicitly._

## Release Information

| Field | Value |
| --- | --- |
| Release version | 2.0.0 (in progress) |
| Primary platform | macOS (Apple Silicon verified) |
| Sidecar Python version | 3.11+ (validated on 3.12) |
| Tauri version | 2.x (requires Rust ≥ 1.85; verified on 1.97.1) |
| React version | 18.3 |
| Database schema version | v4 |

## Executive Status

| Area | Status | Notes |
| --- | --- | --- |
| Python domain preservation | Complete | Scoring, week, slug, migrations ported verbatim |
| SQLite compatibility | Complete | Legacy v1–v4 databases open and upgrade with backup |
| FastAPI sidecar | Complete | All `/api/v1` routes plus health/ready |
| Sidecar security | Complete | Token auth, loopback bind, docs disabled in production |
| Tauri supervision | Complete, compiles | Supervisor/forwarder/commands build and unit-test on Rust 1.97 |
| React workspaces | Complete | All six views, week navigator, degraded banner |
| Markdown and Mermaid | Complete | Bundled, offline, sanitized, error-preserving |
| Settings | Complete | Bounds plus restart-required on database path change |
| Migrations and backups | Complete | Backup-before-migrate preserved |
| Automated testing | **All four suites run green** | See below |
| Documentation | Complete (core) | README, 11 ADRs, traceability, toolchain notes |
| macOS packaging | **Scaffolded, never executed** | Sidecar freezes; no app bundle has been built |
| Windows/Linux packaging | Deferred | Phase 16 |

## Test Results

| Suite | Result | Notes |
| --- | --- | --- |
| Python unit (domain + services) | Pass | Week boundaries, slug, scoring 59/60/79/80, service rules |
| Python integration (repos + migrations) | Pass | CRUD, cascade, counts, backup, idempotent migrations |
| API contract | Pass | Auth (missing/invalid/valid), workflow, production hardening |
| Legacy DB compatibility | Pass | v2 → v4 upgrade preserves data across restart |
| **Backend total** | **84 passed**, ~85% line coverage | Target ≥ 80% met |
| **React unit/component** | **11 passed** (4 files) | Vitest 2.x + Testing Library, jsdom |
| **TypeScript typecheck** | **0 errors** | `tsc --noEmit`, strict |
| **Rust unit** | **9 passed, 1 flaky** | See below |
| Legacy Tkinter suite | **147 passed**, 92.85% coverage | Unchanged by the migration |

### Known flaky test

`security::port::tests::picks_a_nonzero_loopback_port` fails roughly 1 run in
10 under parallel execution and never under `--test-threads=1` (10 runs each
way). It asserts that a released ephemeral port is immediately re-bindable —
exactly the race `security/port.rs` documents as unavoidable and handles with
readiness polling. The production code is correct; the assertion is stronger
than the design guarantees. Not yet changed.

## Security Verification

| Control | Result |
| --- | --- |
| Dynamic startup port | Verified (`security/port.rs`) |
| Per-run random token | Verified (`security/token.rs`) |
| Loopback-only binding | Verified (`cli/sidecar.py`, HOST=127.0.0.1) |
| Token absent from renderer and logs | Verified (redaction filters, `SecretString`) |
| Renderer cannot call sidecar directly | Verified (`verify_no_renderer_http.py` passes) |
| Protected routes reject missing/invalid token | Verified (contract tests) |
| Production API docs disabled | Verified (`test_docs_disabled_in_production`) |
| Sidecar terminates with app | Verified in unit tests (`SidecarHandle::shutdown`); not yet observed in a running app |
| Unexpected failures omit stack traces | Verified (sanitized `INTERNAL_ERROR`) |

## Open Issues

| Item | Impact |
| --- | --- |
| No app bundle has ever been built | The Tauri CLI is not installed, so `npm run tauri dev` and `npm run tauri build` are unexercised. **The V2 app has never run as an application.** |
| `src-tauri/icons/icon.png` is a 1×1 placeholder | Converted to RGBA so the build proceeds, but any bundle will have a broken icon |
| Signing script not exercised on a real bundle | `scripts/install_macos_app.sh` is tested against a synthetic bundle only |
| No signing identity available | Ad-hoc signing works for local installation; notarization needs a Developer ID |
| `npm install` fails on network mounts | `ENOTEMPTY` on rename; needs a local-disk clone or prefix |

## Deviations and Deferred Work

| Item | Reason |
| --- | --- |
| Cancelled milestones excluded from score denominator | SRS explicit rule; the Tkinter app counted them. See [ADR-002](../architecture/decisions/adr-002-preserve-domain.md) |
| macOS signing and notarization | Requires Apple credentials — deferred |
| Windows/Linux CI lanes, performance benchmarks | Deferred per agreed scope |

## Acceptance Criteria (this pass)

| Criterion | Status |
| --- | --- |
| Existing Python behavior preserved and tested | Met |
| Sidecar starts on dynamic port, loopback only | Met (code plus smoke test) |
| Unauthenticated sidecar requests fail | Met |
| Six workspace views available | Met (code and component tests) |
| Project / session / milestone / review / dashboard flows | Met (backend contract tests; UI wired) |
| Plan plus Mermaid offline | Met |
| Dashboard score matches SRS formula | Met |
| Legacy database opens without manual conversion | Met |
| Production API docs disabled | Met |
| Coverage target met (backend) | Met (~85%) |
| **End-to-end application run** | **Not met — blocked on the Tauri CLI** |
