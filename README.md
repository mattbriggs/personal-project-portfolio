# Portfolio Manager

A personal, **local-first desktop application** for managing, scheduling, and
executing work across a portfolio of creative and technical projects using
time-boxed sessions.

This repository is mid-migration from a Python/Tkinter desktop app to a **Tauri
+ React + Python (FastAPI) architecture**. The new stack lives in `backend/`,
`frontend/`, and `src-tauri/`; the original Tkinter app remains in `src/` until
feature parity is confirmed (see [design report](design/Portfolio-Manager-Tauri-React-Python-SRS-Design-Report.md)
and [implementation plan](design/Portfolio-Manager-Tauri-React-Python-Implementation.md)).

## Status

| | Legacy app | V2 app |
| --- | --- | --- |
| Stack | Python + Tkinter | Tauri (Rust) + React + FastAPI sidecar |
| Source | `src/portfolio_manager/` | `backend/`, `frontend/`, `src-tauri/` |
| Tests | 147 passing, 92.85% coverage | 84 backend + 14 React + 10 Rust |
| State | Working | **Working — built, signed, installed, running** |
| Launch | `bash launch.sh` | `/Applications/Portfolio Manager.app` |

The V2 app builds to a signed `.app` and `.dmg`, installs to `/Applications`,
and loads real data from the existing database. The Tkinter app remains until
parity is formally accepted. Full detail in the
[completion report](site/src/release/completion-report.md).

## Target architecture

```
React renderer
  → typed Tauri command client         (frontend/src/command-client)
  → allowlisted Tauri command          (src-tauri/src/commands)
  → authenticated Rust HTTP forwarder  (src-tauri/src/http)
  → loopback-only FastAPI route        (backend/.../api/routes)
  → Pydantic contract                  (backend/.../contracts)
  → application service                (backend/.../application/services)
  → repository port → SQLite           (backend/.../infrastructure/db)
```

The renderer never contacts the sidecar directly. The sidecar binds only to
`127.0.0.1` on a dynamic port and requires a per-launch `X-API-Key` token that
lives solely in Rust in-memory state — it is never written to disk, sent to the
renderer, or logged.

## Supported platforms

macOS is the first release target (Apple Silicon verified; Intel supported by
building the sidecar for `x86_64-apple-darwin`). Windows and Linux follow after
macOS parity. Core Python logic runs on any platform.

## Prerequisites

- Python 3.11+
- Node 18+ and npm
- Rust **≥ 1.85** — a hard floor set by Tauri 2.x's edition-2024 dependencies.
  Install through rustup so it stays upgradable:

  ```bash
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
  . "$HOME/.cargo/env"      # add to your shell profile
  ```

  See [rust-toolchain.md](site/src/development/rust-toolchain.md).
- The Tauri CLI (`cargo install tauri-cli`, or `npm run tauri` once npm
  dependencies install cleanly).

## Development

### Backend (FastAPI sidecar)

```bash
python -m venv .venv
.venv/bin/pip install -e "backend[dev]"
cd backend && ../.venv/bin/pytest      # 84 tests, ~85% coverage
```

Run the sidecar directly (loopback + token auth):

```bash
PORTFOLIO_SIDECAR_TOKEN=dev-token \
  .venv/bin/python -m portfolio_manager.cli.sidecar --port 8765
curl -s 127.0.0.1:8765/health
curl -s -H "X-API-Key: dev-token" 127.0.0.1:8765/api/v1/projects
```

### Frontend (React renderer)

Run these from the **repository root**. The Vite and TypeScript configs live in
`frontend/`, and the npm scripts pass that root through — invoking `vitest` or
`tsc` bare from the root picks up no config and reports misleading failures.

```bash
npm install
npm test            # Vitest — 11 tests
npm run typecheck   # tsc --noEmit
npm run build       # typecheck + production bundle
```

### Tauri shell

```bash
cd src-tauri && cargo test    # 10 unit tests: security, supervisor, forwarder
npm run tauri dev             # from repo root — runs the full stack
```

`cargo test` compiles the Tauri context, so it needs the frozen sidecar binary
and an **RGBA** `src-tauri/icons/icon.png` to exist before it will build.

### Contract types

```bash
python scripts/generate_openapi.py          # regenerate frontend/src/contracts/generated
python scripts/verify_no_renderer_http.py   # assert renderer has no direct HTTP
```

## Packaging (macOS)

```bash
pip install -e "backend[dev,package]"
python scripts/build_sidecar.py
npm run tauri build
scripts/install_macos_app.sh                # sign, verify, install to /Applications
```

`install_macos_app.sh` signs nested Mach-O code before the bundle, verifies the
signature, then stages and swaps the install so a failed copy cannot destroy a
working app. It uses a **Developer ID Application** certificate when the
keychain has one (hardened runtime + `src-tauri/entitlements.plist`) and
otherwise falls back to **ad-hoc signing** — enough to run locally, but not
notarizable or distributable. `--help` lists the options.

## Default local paths

| Purpose | Path |
| --- | --- |
| Config | `~/.portfolio_manager/config.toml` |
| Database | `~/.portfolio_manager/portfolio.db` |
| Backups | `~/.portfolio_manager/portfolio.db.bak` |
| Logs | `~/.portfolio_manager/logs/` |

Existing Tkinter-created databases (schema v1–v4) open without manual conversion;
a backup is written before any pending migration.

## Security boundary summary

- Dynamic loopback port + cryptographically random per-launch token.
- Token in Rust in-memory state only (`secrecy::SecretString`); never persisted,
  sent to the renderer, or logged.
- Every non-health route requires `X-API-Key`; `/health` and `/ready` are
  unauthenticated and expose no sensitive data (ADR-007).
- Production builds disable Swagger/ReDoc/OpenAPI and WebView devtools.
- No generic renderer command; the Tauri command allowlist is the full surface.

See [the ADRs](site/src/architecture/decisions/) and the
[traceability matrix](site/src/requirements/traceability.md) for the
requirement-to-test mapping.

## Documentation

Sources live in **`site/src/`**. `docs/` is generated output — `mkdocs.yml` sets
`docs_dir: site/src` and `site_dir: docs`, so every build wipes and rewrites
`docs/`. Never edit files there. The user guide under `site/src/guide/` is also
generated, from the DITA sources in `guide/`.

```bash
mkdocs serve            # live preview
mkdocs build --strict   # writes docs/ — the GitHub Pages root
```

## Known issues

- **`npm install` fails on network mounts** with `ENOTEMPTY`, leaving a partial
  `node_modules` and no `.bin`. Use a local-disk clone or a local prefix.
- **One flaky Rust test.** `security::port::tests::picks_a_nonzero_loopback_port`
  fails about 1 run in 10 in parallel, never under `--test-threads=1`. It
  asserts an immediate port re-bind that the module documents as racy by
  design; the production code is correct.
- **Ad-hoc signing only.** With no Developer ID in the keychain, `spctl` reports
  `rejected`. That is expected and does not stop the app running locally, but it
  cannot be notarized or opened on another Mac without clearing quarantine.
- **Two apps share the name "Portfolio Manager"** — the legacy launcher in
  `~/Applications` (a shell script calling `launch.sh`) and the V2 bundle in
  `/Applications`. Spotlight and the Dock will show both.
- **Build the `.app` last if you plan to sign it.** `--bundles dmg` deletes the
  staged `.app` after packing it, so the install script finds nothing.

## Legacy Tkinter app

The original app still runs from `src/` via `bash launch.sh`. It will be retired
once the Tauri app reaches accepted parity (implementation plan, Phase 17).

## License

See [LICENSE](LICENSE).
