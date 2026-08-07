# Rust toolchain requirement

The Tauri 2.x dependency tree now transitively requires crates built with
**edition2024** (`toml` 1.x, `serde_spanned` 1.x, `zeroize` 1.9). Those require a
**Rust toolchain ≥ 1.85**.

## Install

If `rustup` is not already present, install it and put Cargo on your `PATH`.
A Rust installed from a source tarball or a package manager is not managed by
rustup and will not upgrade with `rustup update`.

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
. "$HOME/.cargo/env"          # add to your shell profile to make it permanent
rustc --version               # expect >= 1.85
```

## Build / test

```bash
rustup update stable          # ensure >= 1.85
cd src-tauri
cargo test                    # security/http/sidecar unit tests
cargo build                   # debug shell build
```

Verified on **Rust 1.97.1**: the shell compiles and 10 unit tests run
(`security::token`, `security::port`, `sidecar::readiness`, `sidecar::launcher`,
`sidecar::shutdown`, `sidecar::supervisor`, `logging`). On Rust 1.83 the build
fails while parsing the `serde_spanned 1.1.1` manifest with "feature
`edition2024` is required" — a toolchain-version limitation, not a code error.

### Two prerequisites that are not Rust

`cargo test` compiles the Tauri context, so the build fails before reaching any
test unless both of these exist:

| Requirement | Failure if missing |
| --- | --- |
| `src-tauri/binaries/portfolio-sidecar/` | `resource path ... doesn't exist` from the build script. Create it with `python scripts/build_sidecar.py` |
| `src-tauri/icons/icon.png` in RGBA | `proc macro panicked: icon ... is not RGBA` at `tauri::generate_context!`. The message does not name the fix — convert the PNG to RGBA |

### Building off a network volume

Cargo writes a large number of small files. On an SMB or NFS mount that is slow
and can fail outright. Point the target directory at local disk:

```bash
CARGO_TARGET_DIR=/tmp/portfolio-target cargo test
```

If you do this, export the same `CARGO_TARGET_DIR` when running
`scripts/install_macos_app.sh` so it can find the resulting bundle.

## What the Rust unit tests cover

- Dynamic loopback port selection returns a bindable port.
- Token generation has the expected length/entropy and differs each call.
- Readiness polling times out against a dead port.
- Launch argv excludes the token (token passed via env only).
- Shutdown terminates a long-running child; exit detection works.
- The supervisor state machine serializes to snake_case; a launch plan yields a
  port and a 64-char token.
- Secret redaction never reveals the tail of a token.
