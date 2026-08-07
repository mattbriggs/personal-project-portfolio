# Development Guide

The repository holds two applications. Pick the section for the one you are
working on; the [Architecture](architecture.md) page explains how they relate.

---

## Prerequisites

| Tool | Version | Needed for |
| --- | --- | --- |
| Python | 3.11+ | Sidecar backend, legacy app |
| Node + npm | 18+ | React renderer |
| Rust | **≥ 1.85** | Tauri shell |
| Tauri CLI | 2.x | Building and running the desktop app |

Rust 1.85 is a hard floor: the Tauri 2.x dependency tree pulls crates that use
edition 2024. Install via rustup and let it manage the toolchain — see
[Rust Toolchain](development/rust-toolchain.md) for the details and for what
goes wrong on an older compiler.

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
. "$HOME/.cargo/env"     # add this to your shell profile
rustc --version          # expect >= 1.85
```

---

## V2 stack

### Backend (FastAPI sidecar)

```bash
python -m venv .venv
.venv/bin/pip install -e "backend[dev]"
cd backend && ../.venv/bin/pytest        # 84 tests, ~85% coverage
```

`backend/pyproject.toml` sets `pythonpath = ["src"]`, so no editable install is
strictly required to run the tests.

Run the sidecar directly, the way the Tauri shell does:

```bash
PORTFOLIO_SIDECAR_TOKEN=dev-token \
  .venv/bin/python -m portfolio_manager.cli.sidecar --port 8765

curl -s 127.0.0.1:8765/health
curl -s -H "X-API-Key: dev-token" 127.0.0.1:8765/api/v1/projects
```

### Frontend (React renderer)

All npm scripts run from the **repository root**, even though the Vite and
TypeScript configs live in `frontend/`. The scripts pass the correct root
through; running `vite` or `tsc` bare from the root picks up no config.

```bash
npm install
npm test              # Vitest — 11 tests
npm run typecheck     # tsc --noEmit
npm run build         # typecheck + production bundle
```

### Tauri shell

```bash
cd src-tauri && cargo test    # 10 unit tests: security, supervisor, forwarder
npm run tauri dev             # from the repo root — runs the full stack
```

`cargo test` compiles the Tauri context, which requires two artifacts to exist
before it will build at all:

- `src-tauri/binaries/portfolio-sidecar/` — the frozen sidecar, shipped through
  `bundle.resources` in `tauri.conf.json`. Build it first (below).
- `src-tauri/icons/icon.png` in **RGBA** format. A non-RGBA PNG fails inside
  `tauri::generate_context!` with a message that does not obviously point at
  the icon.

### Contract types

```bash
python scripts/generate_openapi.py           # regenerate frontend/src/contracts/generated
python scripts/verify_no_renderer_http.py    # assert the renderer has no direct HTTP
```

The second script is a guard rail for [ADR-001](architecture/decisions/adr-001-tauri-mediated-sidecar.md):
the renderer must reach the sidecar only through Tauri commands.

---

## Packaging (macOS)

```bash
# 1. Freeze the sidecar for your architecture
pip install -e "backend[dev,package]"
python scripts/build_sidecar.py

# 2. Build the app bundle
npm run tauri build

# 3. Sign it and install into /Applications
scripts/install_macos_app.sh
```

Use `x86_64-apple-darwin` on Intel. Per
[ADR-010](architecture/decisions/adr-010-macos-arch.md) the sidecar is built
per-architecture; a universal binary comes later.

Add `--bundles dmg` for a distributable disk image. Build the `.app` **last**
if you intend to sign it — the DMG step deletes the staged `.app` after packing
it, so `install_macos_app.sh` will not find a bundle if `dmg` ran most recently.

Three things reliably go wrong on a first build:

| Symptom | Cause |
| --- | --- |
| `beforeBuildCommand ... failed`, `tsc: command not found` | `npm run build` runs from the repository root. If npm dependencies did not install (see network mounts below), pre-build `frontend/dist` and skip the hook with `--config '{"build":{"beforeBuildCommand":""}}'` |
| `feature 'edition2024' is required` | The Tauri CLI shells out to whichever `cargo` is on `PATH`. A non-rustup Rust will shadow the rustup toolchain — put `$HOME/.cargo/bin` first |
| `resource path ... doesn't exist` | The frozen sidecar has not been built for your target triple yet |

`install_macos_app.sh` signs nested Mach-O code before the bundle itself,
verifies the signature, then stages and swaps the install so a failed copy
cannot destroy a working app. It picks a **Developer ID Application**
certificate if the keychain has one — adding the hardened runtime and the
entitlements in `src-tauri/entitlements.plist` — and otherwise falls back to
**ad-hoc signing**, which runs locally but cannot be notarized or distributed.
Run `scripts/install_macos_app.sh --help` for the options.

!!! note "Gatekeeper and ad-hoc signatures"
    Without a Developer ID the app is signed ad-hoc. `spctl --assess` returns
    `rejected`, which is expected and does not stop it running. A locally built
    bundle carries no quarantine attribute, so it opens normally on the machine
    that built it. Copied to another Mac it would be quarantined and need
    right-click → Open, or `xattr -dr com.apple.quarantine`.

---

## Legacy Tkinter app

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
python -m portfolio_manager      # or: bash launch.sh
```

`create_shortcut.sh` builds a `.app` wrapper for the Dock that calls
`launch.sh` from the repo, so it never needs rebuilding after a `git pull`.

### Adding a migration

1. Open `src/portfolio_manager/db/migrations.py`.
2. Append a tuple to `_build_migrations()`:

```python
("v2", "Add color column to project", "ALTER TABLE project ADD COLUMN color TEXT;")
```

3. Run the app — the migration is applied on next startup, after a backup is
   written to `<name>.db.bak`.

The V2 sidecar runs the same migration set against the same database.

---

## Code style

| Tool | Purpose | Config |
| --- | --- | --- |
| `black` | Formatter (line length 88) | `pyproject.toml` |
| `ruff` | Linter | `pyproject.toml`, `backend/pyproject.toml` |
| `mypy` | Type checker (strict in `backend/`) | `pyproject.toml`, `backend/pyproject.toml` |
| `tsc` | TypeScript type checker (strict) | `frontend/tsconfig.json` |

```bash
black src/ tests/
ruff check src/ tests/
mypy src/
npm run typecheck
```

Public Python classes and functions use **reStructuredText** docstrings:

```python
def complete_session(self, session_id: int, notes: str = "") -> Session:
    """Mark a session as completed and record the completion timestamp.

    :param session_id: Primary key of the session to complete.
    :param notes: Optional session notes.
    :returns: The updated Session domain object.
    :rtype: Session
    :raises SessionStateError: If the session is already completed or cancelled.
    """
```

Optional pre-commit hooks run `black` and `ruff`:

```bash
pip install pre-commit && pre-commit install
```

---

## Logging

Both applications use the standard `logging` module — never `print()` for
diagnostics. Logs rotate at `~/.portfolio_manager/logs/app.log` (max 5 MB, 2
backups). The sidecar and the Rust shell both install redaction filters so the
per-launch API token cannot reach a log file.

---

## Building the docs

**`docs/` is generated output, not source.** `mkdocs.yml` sets
`docs_dir: site/src` and `site_dir: docs`, so every build wipes `docs/` and
rewrites it. Edit `site/src/`, never `docs/`.

`site/src/guide/` is *also* generated: the `tools/prepare_guide.py` hook copies
it from the DITA output in `guide/out/markdown/` on every build. To change the
user guide, edit the `.dita` sources in `guide/` and regenerate.

```bash
mkdocs serve             # live preview
mkdocs build --strict    # writes docs/ — the GitHub Pages root
```

---

## Known environment issues

**npm on a network mount.** If the repository lives on an SMB or NFS share,
`npm install` fails part-way with `ENOTEMPTY: directory not empty, rename ...`
and leaves a partial `node_modules` with no `.bin` directory. Symptoms are
imports that cannot be resolved and `npx` silently fetching a different package
version than the one pinned. Work on a local-disk clone, or install into a
local-disk prefix.

**Flaky port test.** `security::port::tests::picks_a_nonzero_loopback_port`
fails intermittently (roughly 1 run in 10) under parallel execution and never
under `cargo test -- --test-threads=1`. The test asserts that a released
ephemeral port is immediately re-bindable, which is precisely the race the
module documents as unavoidable and handles with readiness polling.
