# Portfolio Manager

A personal, **local-first desktop application** for managing, scheduling, and
executing work across a portfolio of creative and technical projects using
time-boxed sessions.

This repository is being migrated from a Python/Tkinter desktop app to a **Tauri
+ React + Python (FastAPI) architecture**. The new stack lives in `backend/`,
`frontend/`, and `src-tauri/`; the original Tkinter app remains in `src/` until
feature parity is confirmed (see [design report](design/Portfolio-Manager-Tauri-React-Python-SRS-Design-Report.md)
and [implementation plan](design/Portfolio-Manager-Tauri-React-Python-Implementation.md)).

## Target architecture

```
React renderer
  → typed Tauri command client        (frontend/src/command-client)
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

macOS is the first release target (Apple Silicon / Intel). Windows and Linux
follow after macOS parity. Core Python logic runs on any platform.

## Prerequisites

- Python 3.11+
- Node 18+ and npm
- Rust **≥ 1.85** and the Tauri CLI (`cargo install tauri-cli` or `npm run tauri`).
  Rust 1.85 is required by the current Tauri 2.x dependency tree — see
  [docs/development/rust-toolchain.md](docs/development/rust-toolchain.md).

## Development

### Backend (FastAPI sidecar)

```bash
cd backend
python -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest                       # 84 tests, ~85% coverage
```

Run the sidecar directly (loopback + token auth):

```bash
PORTFOLIO_SIDECAR_TOKEN=dev-token \
  .venv/bin/python -m portfolio_manager.cli.sidecar --port 8765
curl -s 127.0.0.1:8765/health
curl -s -H "X-API-Key: dev-token" 127.0.0.1:8765/api/v1/projects
```

### Frontend (React renderer)

```bash
npm install
npm run test        # Vitest component tests
npm run build       # type-check + production bundle
```

### Tauri shell

```bash
cd src-tauri
cargo test          # security / supervisor / forwarder unit tests (Rust >= 1.85)
npm run tauri dev   # from repo root — runs the full stack
```

### Contract types

```bash
python scripts/generate_openapi.py     # regenerate frontend/src/contracts/generated
python scripts/verify_no_renderer_http.py   # assert renderer has no direct HTTP
```

### Package the sidecar

```bash
pip install -e "backend[dev,package]"
python scripts/build_sidecar.py --target-triple x86_64-apple-darwin
```

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

See [docs/architecture/decisions](docs/architecture/decisions) for the ADRs and
[docs/requirements/traceability.md](docs/requirements/traceability.md) for the
requirement-to-test matrix.

## Legacy Tkinter app

The original app still runs from `src/` via `bash launch.sh`. It will be retired
once the Tauri app reaches accepted parity (implementation plan, Phase 17).

## License

See [LICENSE](LICENSE).
