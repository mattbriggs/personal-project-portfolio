# Rust toolchain requirement

The Tauri 2.x dependency tree now transitively requires crates built with
**edition2024** (`toml` 1.x, `serde_spanned` 1.x, `zeroize` 1.9). Those require a
**Rust toolchain ≥ 1.85**.

## Build / test

```bash
rustup update stable          # ensure >= 1.85
cd src-tauri
cargo test                    # security/http/sidecar unit tests
cargo build                   # debug shell build
```

The Rust sources compile and the unit tests (`security::token`, `security::port`,
`sidecar::readiness`, `sidecar::launcher`, `sidecar::shutdown`,
`sidecar::supervisor`, `logging`) run on a ≥ 1.85 toolchain. On Rust 1.83 the
build fails while parsing the `serde_spanned 1.1.1` manifest with
"feature `edition2024` is required" — this is a toolchain-version limitation, not
a code error.

## What the Rust unit tests cover

- Dynamic loopback port selection returns a bindable port.
- Token generation has the expected length/entropy and differs each call.
- Readiness polling times out against a dead port.
- Launch argv excludes the token (token passed via env only).
- Shutdown terminates a long-running child; exit detection works.
- The supervisor state machine serializes to snake_case; a launch plan yields a
  port and a 64-char token.
- Secret redaction never reveals the tail of a token.
