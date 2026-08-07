# Portfolio Manager Release Repository Prep

Date: 2026-08-07

## Goal

Prepare this repository to publish installable macOS releases of Portfolio
Manager through GitHub Releases. The immediate public artifact should be a
downloadable macOS DMG. Windows and Linux are out of scope.

## Current Repo Shape

Portfolio Manager is now a Tauri 2 desktop app with:

- React/Vite frontend in `frontend/`.
- Rust/Tauri shell in `src-tauri/`.
- Python FastAPI sidecar in `backend/`.
- Legacy Tkinter app still present in `src/`.
- macOS bundle config in `src-tauri/tauri.conf.json`, currently targeting
  `app` and `dmg`.
- Frozen Python sidecar build script at `scripts/build_sidecar.py`.
- Local app signing/install script at `scripts/install_macos_app.sh`.

The app is already structurally close to a distributable macOS app. The main
remaining work is release hygiene, signing/notarization, reproducibility, and
multi-architecture packaging.

## Readiness Assessment

| Area | Status | Notes |
| --- | --- | --- |
| Tauri bundle config | Mostly ready | `tauri.conf.json` has product name, bundle identifier, icons, minimum macOS 11.0, and DMG target. |
| Sidecar packaging | Needs release decision | Current edited state uses PyInstaller `onedir` under `src-tauri/binaries/portfolio-sidecar/` and bundles it as a Tauri resource. Older docs/ADR still describe `externalBin` with target-triple suffixes. |
| macOS signing | Not public-ready | `install_macos_app.sh` can sign with Developer ID if present, but current docs say ad-hoc signing was the only verified path. Public downloads should be Developer ID signed and notarized. |
| Notarization | Missing | No notarization/stapling release script or GitHub Actions workflow exists. |
| GitHub release automation | Missing | There is no `.github/` workflow. Releases can be manual with `gh release create`, but CI-based artifacts are not wired. |
| Versioning | Needs cleanup | `package.json`, root `pyproject.toml`, `backend/pyproject.toml`, `src-tauri/Cargo.toml`, and `src-tauri/tauri.conf.json` say `2.0.0`; `CHANGELOG.md` already has a `2.1.0` entry. |
| Reproducible frontend install | Needs cleanup | No `package-lock.json` is present. `npm install` works as a moving dependency solve; `npm ci` cannot be used until a lockfile is committed. |
| Rust toolchain | Needs cleanup | Local `cargo test` failed under Cargo 1.83 because Tauri dependencies require edition 2024 support. Repo docs say Rust >= 1.85, but `src-tauri/Cargo.toml` still says `rust-version = "1.77"`. |
| Test environment | Needs bootstrap | Frontend tests failed because `tsc`/`vitest` were missing. Backend tests failed because the selected venv lacks FastAPI. These are setup gaps in the current checkout, not necessarily product regressions. |
| Release docs | Needs update | User guide pages still describe the Tkinter install path and say the V2 desktop app is not yet available. |
| Artifact hygiene | Mostly ready | `.gitignore` now excludes `src-tauri/binaries/`, `src-tauri/gen/`, and `src-tauri/target/`; keep generated binaries out of git and attach release artifacts to GitHub releases. |

## Release Blockers

1. **Decide the release version.**

   Pick either `2.0.0` for the first Tauri public app release or `2.1.0` to
   match the current changelog. Then update every version-bearing file:

   - `package.json`
   - `pyproject.toml`
   - `backend/pyproject.toml`
   - `src-tauri/Cargo.toml`
   - `src-tauri/tauri.conf.json`
   - `CHANGELOG.md`

2. **Make the build reproducible.**

   Commit a lockfile for the frontend. For npm, that means generating and
   committing `package-lock.json`, then using `npm ci` in release steps.

3. **Fix the Rust version contract.**

   Align the declared Rust requirement with reality. Recommended:

   - Add `rust-toolchain.toml` with a stable toolchain new enough for Tauri 2.
   - Change `src-tauri/Cargo.toml` from `rust-version = "1.77"` to at least
     `1.85`, or to the version you validate in CI.

4. **Choose macOS architecture strategy.**

   Since this is macOS-only, decide what "other people can install" means:

   - Apple Silicon only: one `macos-arm64` DMG. Fastest first release.
   - Apple Silicon plus Intel: two DMGs, `macos-arm64` and `macos-x64`.
   - Universal app: one DMG, more work because the PyInstaller sidecar must also
     be universal or packaged in an architecture-aware way.

   Recommendation: publish separate ARM64 and x64 DMGs if you want to support
   current and older Macs. Do not claim Intel support unless the frozen Python
   sidecar is built and tested on x64.

5. **Add Developer ID signing and notarization.**

   Ad-hoc signing is fine for your own machine, but not for public GitHub
   downloads. For public releases outside the Mac App Store, Apple expects a
   Developer ID certificate and notarization ticket. Apple states that Developer
   ID distribution requires Apple Developer Program membership, a Developer ID
   certificate, and notarization:
   https://developer.apple.com/support/developer-id/

   Tauri's macOS signing docs also note that Developer ID is the certificate type
   for shipping outside the App Store, and that notarization is required when
   using Developer ID:
   https://v2.tauri.app/distribute/sign/macos/

6. **Create a release smoke-test checklist.**

   At minimum, validate a freshly downloaded DMG on a clean-ish macOS user
   account:

   - DMG opens.
   - App copies to `/Applications`.
   - Gatekeeper opens it without manual quarantine removal.
   - First launch creates/opens `~/.portfolio_manager`.
   - Existing legacy database migrates after making a backup.
   - Dashboard, Projects, Sessions, Milestones, Weekly Review, and Settings load.
   - App quit terminates the sidecar.

## Recommended Repo Changes Before First Public Release

### Must Do

- Commit frontend lockfile and switch release docs/workflows to `npm ci`.
- Update Rust toolchain declaration.
- Update all package versions to one release value.
- Update `CHANGELOG.md` for the exact public release.
- Update user docs so public users see the V2 macOS install path, not only the
  legacy Tkinter setup.
- Build with a Developer ID Application identity.
- Notarize and staple the DMG before uploading.
- Add `SHA256SUMS.txt` for release assets.

### Should Do

- Add `.github/workflows/ci.yml` for backend, frontend, and Rust tests.
- Add `.github/workflows/release.yml` later for signed/notarized release
  artifacts.
- Add a `scripts/release_macos.sh` wrapper so the manual release is repeatable.
- Add a small packaged-app smoke test script that launches the `.app`, polls for
  readiness, then quits it.
- Decide whether to keep the legacy Tkinter launcher in public docs or move it
  to "legacy/developer only."

### Could Do Later

- Add Tauri updater support. This is separate from GitHub Releases. Tauri updater
  artifacts require update signatures, key management, and updater config.
- Produce a universal macOS app.
- Add GitHub artifact attestations.
- Add a Homebrew cask after releases stabilize.

## Suggested First Release Artifact Set

For a public macOS-only release:

- `Portfolio-Manager-vX.Y.Z-macos-arm64.dmg`
- `Portfolio-Manager-vX.Y.Z-macos-x64.dmg`, if Intel support is validated
- `SHA256SUMS.txt`
- Release notes copied from `CHANGELOG.md`, with an install note:
  "Download the DMG for your Mac architecture, open it, and drag Portfolio
  Manager to Applications."

Avoid uploading raw `.app` bundles. A DMG is the expected direct-download macOS
install experience and is already configured in Tauri.

## Manual Verification Attempted During This Review

These commands were run from the current checkout:

- `npm run typecheck`: failed because `tsc` is not installed in `node_modules`.
- `npm test`: failed because `vitest` is not installed in `node_modules`.
- `cd backend && ../.venv/bin/pytest`: failed because the venv lacks FastAPI.
- `cd src-tauri && cargo test -- --test-threads=1`: failed under Cargo 1.83
  because a Tauri transitive dependency requires edition 2024 support.

This means the current machine is not release-bootstrap-ready. After dependency
and toolchain setup, rerun all suites before cutting a release.

## Current Working Tree Note

The repo already had unrelated modified files before these release docs were
written. Do not tag a release from a dirty tree. The public tag should point to
a reviewed commit on the intended release branch, with generated binaries and
Tauri schema files kept out of git.

## Sources

- GitHub Releases documentation:
  https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository
- GitHub CLI `gh release create` manual:
  https://cli.github.com/manual/gh_release_create
- Tauri macOS signing and notarization:
  https://v2.tauri.app/distribute/sign/macos/
- Tauri GitHub release workflow guidance:
  https://v2.tauri.app/distribute/pipelines/github/
- Apple Developer ID overview:
  https://developer.apple.com/support/developer-id/
