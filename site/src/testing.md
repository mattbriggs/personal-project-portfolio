# Testing

Four suites cover the two applications. All figures below were measured on
macOS with Python 3.12, Node 22, and Rust 1.97.

| Suite | Command | Tests | Coverage |
| --- | --- | ---: | --- |
| Sidecar backend | `cd backend && pytest` | 84 | ~85% line |
| React renderer | `npm test` | 11 | — |
| Tauri shell | `cd src-tauri && cargo test` | 10 | — |
| Legacy Tkinter app | `pytest tests` | 147 | 92.85% |

Coverage target is **80%** for Python, enforced with `--cov-fail-under=80` on
the legacy suite.

---

## Sidecar backend

```bash
python -m venv .venv
.venv/bin/pip install -e "backend[dev]"
cd backend
../.venv/bin/pytest                          # all 84
../.venv/bin/pytest tests/unit               # domain + services
../.venv/bin/pytest --cov=portfolio_manager  # with coverage
```

### Tiers

| Tier | Path | What it covers |
| --- | --- | --- |
| Unit — domain | `tests/unit/domain/` | Scoring thresholds (59/60/79/80), ISO week boundaries, slug rules |
| Unit — services | `tests/unit/application/` | Project, session, milestone, review, and scoring service rules |
| Integration | `tests/integration/` | Repository CRUD and cascade, migration idempotency, backup-before-migrate |
| Contract | `tests/contract/` | Auth (missing / invalid / valid token), full workflow, production hardening |
| Compatibility | `tests/compatibility/` | A v2-schema legacy database upgrades to v4 and preserves data across restart |

The contract tests drive the API through FastAPI's `TestClient` in-process.
That is deliberate: it needs no running server and no network, so the suite
works in sandboxes where a cross-process request to a locally started sidecar
would be blocked.

`test_production_hardening.py` asserts the things that must *not* be present in
a production build — Swagger, ReDoc, and the OpenAPI schema all return 404.

---

## React renderer

```bash
npm test                # Vitest, jsdom
npm run test:watch
npm run test:coverage
npm run typecheck       # tsc --noEmit, strict
```

Component tests use Testing Library and drive real user interactions
(`@testing-library/user-event`) rather than calling handlers directly.

!!! warning "Run the scripts, not the tools"
    `vite.config.ts` and `tsconfig.json` live in `frontend/`, but the npm
    scripts live in the root `package.json`. The scripts pass the correct root
    through. Invoking `vitest` or `tsc` bare from the repository root finds no
    config, silently skips the jsdom environment and setup file, and reports
    failures that have nothing to do with your code.

### Timezone sensitivity

`src/utils/week.test.ts` covers the week-key helpers, which convert between
local wall-clock time and the UTC-based dates the rest of the module uses. A
mismatch there produces an off-by-one week **only** in timezones behind UTC — a
suite that runs in UTC will pass with the bug present. When touching
`utils/week.ts`, run the suite under at least one negative-offset zone:

```bash
TZ=America/Los_Angeles npm test
TZ=UTC npm test
TZ=Asia/Tokyo npm test
```

---

## Tauri shell

```bash
cd src-tauri
cargo test
cargo test -- --test-threads=1   # deterministic; see below
```

Ten unit tests cover token entropy and redaction, loopback port selection, the
sidecar launch plan (asserting the token never appears in `argv`), readiness
timeout, and child-process shutdown.

The build requires a frozen sidecar binary and an RGBA icon to exist before it
will compile at all — see [Development](development.md#tauri-shell).

!!! bug "Known flaky test"
    `security::port::tests::picks_a_nonzero_loopback_port` fails roughly 1 run
    in 10 under parallel execution, and never under `--test-threads=1`. It
    asserts that a released ephemeral port is immediately re-bindable, which is
    exactly the race `security/port.rs` documents as unavoidable and mitigates
    with readiness polling. The production code is correct; the assertion is
    stronger than the design guarantees.

---

## Legacy Tkinter app

```bash
pytest tests                       # 147 tests, 92.85% coverage
pytest tests/unit
pytest tests/integration
pytest tests/e2e                   # requires a Tk-capable Python
```

Views and controllers are excluded from coverage — Tkinter GUI code cannot be
tested reliably headlessly. The e2e startup test calls `Tk.withdraw()` to
suppress the window and skips itself when no display is available:

```python
def test_builds_without_error(headless_settings):
    try:
        window = build_app(settings=headless_settings)
        window.withdraw()
        window.update()
        window.destroy()
    except tk.TclError as exc:
        pytest.skip(f"No display available: {exc}")
```

A Python built without `_tkinter` will skip the whole tier rather than fail.

### Shared fixtures (`tests/conftest.py`)

| Fixture | Type | Description |
| --- | --- | --- |
| `reset_singletons` | autouse | Resets `DatabaseConnection` and `EventBus` around each test |
| `in_memory_db` | `DatabaseConnection` | Fully migrated in-memory SQLite connection |
| `test_config` | `Settings` | Settings pointing at a `:memory:` database |
| `sample_project` | `Project` | A persisted active project with `plan_content` |
| `sample_sessions` | `list[Session]` | Three sessions (planned, completed, cancelled) |

---

## Guard rails

Beyond the test suites, two checks enforce architectural invariants:

```bash
python scripts/verify_no_renderer_http.py   # renderer makes no direct HTTP calls
python scripts/generate_openapi.py          # regenerate types; diff to detect drift
```

The first backs [ADR-001](architecture/decisions/adr-001-tauri-mediated-sidecar.md);
the second backs [ADR-005](architecture/decisions/adr-005-openapi-typescript.md).
Run both before a release.

See the [Traceability Matrix](requirements/traceability.md) for the
requirement-to-test mapping.
