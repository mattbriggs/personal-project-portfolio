# Portfolio Manager GitHub Release Process

Date: 2026-08-07

## Release Strategy

Use GitHub Releases as the public distribution page and attach notarized macOS
DMG files as release assets. Start with a manual release process, then automate
once the signing, notarization, and architecture decisions are stable.

Recommended tag format: `vX.Y.Z`

Recommended asset names:

- `Portfolio-Manager-vX.Y.Z-macos-arm64.dmg`
- `Portfolio-Manager-vX.Y.Z-macos-x64.dmg`
- `SHA256SUMS.txt`

GitHub automatically provides source archives for each release, but users should
install from the attached DMG, not from the source ZIP/tarball.

## One-Time Setup

1. Install the required local tools:

   ```bash
   xcode-select --install
   rustup update
   node --version
   npm --version
   gh auth status
   ```

2. Set up Apple distribution credentials:

   - Join the Apple Developer Program.
   - Create/install a `Developer ID Application` certificate.
   - Configure notarization credentials for `notarytool` or Tauri.
   - Confirm the identity appears:

   ```bash
   security find-identity -v -p codesigning
   ```

3. Make the repo release-ready:

   - Commit `package-lock.json`.
   - Add or update `rust-toolchain.toml`.
   - Align all version fields.
   - Update `CHANGELOG.md`.
   - Update install docs for the V2 macOS app.

## Per-Release Checklist

Set the release version:

```bash
export VERSION=2.0.0
export TAG=v$VERSION
export RELEASE_DIR=dist/release/$TAG
mkdir -p "$RELEASE_DIR"
```

Verify the release branch:

```bash
git status --short
git branch --show-current
git fetch origin --tags
```

Do not continue unless `git status --short` only shows intentional release
changes.

## Build And Test

Bootstrap dependencies:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e "backend[dev,package]"
npm ci
```

Run the validation suite:

```bash
python scripts/generate_openapi.py
python scripts/verify_no_renderer_http.py
cd backend && ../.venv/bin/pytest && cd ..
npm run typecheck
npm test
cd src-tauri && cargo test -- --test-threads=1 && cd ..
```

Build the sidecar and Tauri app on the target Mac architecture:

```bash
python scripts/build_sidecar.py
npm run tauri build -- --bundles dmg
```

For two-architecture distribution, repeat the build on both architectures or
add CI/native runners that can build the matching PyInstaller sidecar. Do not
cross-build the Tauri shell and assume the Python sidecar is also cross-built.

## Sign And Notarize

For public releases, use Developer ID signing and notarization. Ad-hoc signing
is only acceptable for local testing or a private preview.

Preferred end state: configure Tauri signing/notarization and let the release
build produce signed, notarized, stapled DMGs. Tauri documents the relevant
Apple signing identity and notarization environment variables here:
https://v2.tauri.app/distribute/sign/macos/

If continuing with the current local script, use it to sign the `.app` with the
Developer ID identity before creating the final DMG, or add a small release
script that performs:

```bash
codesign --verify --deep --strict --verbose=2 "Portfolio Manager.app"
xcrun notarytool submit "Portfolio-Manager-v$VERSION-macos-arm64.dmg" --wait
xcrun stapler staple "Portfolio-Manager-v$VERSION-macos-arm64.dmg"
spctl --assess --type open --context context:primary-signature --verbose "Portfolio-Manager-v$VERSION-macos-arm64.dmg"
```

Exact credential flags depend on whether you use Apple ID/app-specific password
or App Store Connect API keys.

## Stage Assets

Copy/rename the DMG into the release directory:

```bash
cp "src-tauri/target/release/bundle/dmg/Portfolio Manager_$VERSION"_*.dmg \
  "$RELEASE_DIR/Portfolio-Manager-$TAG-macos-arm64.dmg"
```

Adjust the source filename to the exact file Tauri produces.

Create checksums:

```bash
cd "$RELEASE_DIR"
shasum -a 256 *.dmg > SHA256SUMS.txt
cd -
```

Create release notes:

```bash
cat > "$RELEASE_DIR/release-notes.md" <<EOF
# Portfolio Manager $TAG

## Install

Download the DMG for your Mac architecture, open it, and drag Portfolio Manager
to Applications.

## Changes

See CHANGELOG.md for the full change list.
EOF
```

## Create The GitHub Release

Create an annotated tag from the reviewed release commit:

```bash
git tag -a "$TAG" -m "Portfolio Manager $TAG"
git push origin "$TAG"
```

Create a draft release and upload assets:

```bash
gh release create "$TAG" "$RELEASE_DIR"/*.dmg "$RELEASE_DIR"/SHA256SUMS.txt \
  --repo mattbriggs/personal-project-portfolio \
  --title "Portfolio Manager $TAG" \
  --notes-file "$RELEASE_DIR/release-notes.md" \
  --draft \
  --verify-tag
```

Review the draft release in GitHub, confirm every asset downloaded from the
draft works, then publish it from the GitHub UI.

GitHub's release docs support draft releases, attached binary files, generated
release notes, prerelease markers, and the "latest" label. The GitHub CLI can
also create releases from an existing tag and attach assets directly:
https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository
https://cli.github.com/manual/gh_release_create

## Post-Publish Verification

After publishing:

1. Download the DMG from the public release page.
2. Open it on a Mac that did not build the app.
3. Drag the app to `/Applications`.
4. Launch it normally, not by clearing quarantine.
5. Confirm Gatekeeper accepts it.
6. Confirm all main screens load.
7. Confirm no sidecar process remains after quitting.
8. Run:

   ```bash
   shasum -a 256 ~/Downloads/Portfolio-Manager-$TAG-macos-arm64.dmg
   ```

9. Compare the checksum with `SHA256SUMS.txt`.

## Automation Path

Once the manual flow works twice, add a GitHub Actions workflow. Tauri's GitHub
workflow guide shows a tag or release-branch trigger, a macOS x64/ARM64 matrix,
`contents: write`, dependency installation, Rust setup, and `tauri-apps/tauri-action`
creating a draft release:
https://v2.tauri.app/distribute/pipelines/github/

For this repo, the workflow needs extra steps before `tauri-action`:

- Set up Python 3.11+.
- Install `backend[package]`.
- Run `python scripts/build_sidecar.py` on the same architecture as the app.
- Run backend/frontend/Rust tests.
- Import the Apple Developer certificate from GitHub Secrets.
- Provide notarization secrets.

Required GitHub Secrets will likely include:

- `APPLE_CERTIFICATE`
- `APPLE_CERTIFICATE_PASSWORD`
- `KEYCHAIN_PASSWORD`
- `APPLE_SIGNING_IDENTITY`
- `APPLE_ID` plus app-specific password and `APPLE_TEAM_ID`, or App Store
  Connect API key equivalents

Keep release publishing as a draft until the downloaded assets have been tested.

## Other Considerations

- **No auto-update yet:** GitHub Releases gives users a download page. It does
  not automatically update installed apps. Tauri updater support is a separate
  feature and requires signed update metadata.
- **Database safety:** Release notes should tell existing users that the app uses
  `~/.portfolio_manager/portfolio.db` and backs up before migration.
- **Minimum macOS:** Current config says macOS 11.0. Keep that in the release
  notes.
- **Intel support:** Only publish an x64 DMG after testing it on Intel macOS or
  under an equivalent release validation path.
- **Private preview:** If Developer ID/notarization is not ready, publish as a
  prerelease or keep the release private. Public users should not need terminal
  commands to bypass Gatekeeper.
- **Immutable releases:** If repository release immutability is enabled, use
  draft releases and attach/test all assets before publishing.

## Sources

- GitHub Releases documentation:
  https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository
- GitHub CLI `gh release create` manual:
  https://cli.github.com/manual/gh_release_create
- Tauri macOS signing and notarization:
  https://v2.tauri.app/distribute/sign/macos/
- Tauri GitHub Actions release guide:
  https://v2.tauri.app/distribute/pipelines/github/
- Apple Developer ID overview:
  https://developer.apple.com/support/developer-id/
