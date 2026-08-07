#!/usr/bin/env bash
#
# Sign the built macOS app bundle and install it into /Applications.
#
# The bundle embeds the PyInstaller sidecar as an external binary, so nested
# Mach-O code is signed inside-out before the bundle itself — macOS rejects a
# bundle whose nested code was signed after the outer seal.
#
# Signing identity is chosen automatically:
#   * a "Developer ID Application" certificate, if the keychain has one
#     (adds the hardened runtime + entitlements, required for notarization)
#   * otherwise ad-hoc ("-"), which is enough to run the app locally
#
# Usage:
#   scripts/install_macos_app.sh [--bundle PATH] [--dest DIR]
#                                [--identity NAME] [--yes] [--no-install]
#
# Environment overrides: BUNDLE_PATH, DEST_DIR, SIGN_IDENTITY, ENTITLEMENTS.
#
# Build the bundle first with:  npm run tauri build

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

BUNDLE_PATH="${BUNDLE_PATH:-}"
DEST_DIR="${DEST_DIR:-/Applications}"
SIGN_IDENTITY="${SIGN_IDENTITY:-}"
ENTITLEMENTS="${ENTITLEMENTS:-$REPO_ROOT/src-tauri/entitlements.plist}"
ASSUME_YES=0
DO_INSTALL=1

die() { printf 'error: %s\n' "$*" >&2; exit 1; }
note() { printf '  %s\n' "$*"; }
step() { printf '\n==> %s\n' "$*"; }

# Print the header comment block (everything after the shebang, up to the first
# line of actual code) as help text.
usage() {
  awk 'NR == 1 { next }
       /^#/    { sub(/^# ?/, ""); print; next }
                { exit }' "${BASH_SOURCE[0]}"
  exit 0
}

while [ $# -gt 0 ]; do
  case "$1" in
    --bundle)     BUNDLE_PATH="${2:-}"; shift 2 ;;
    --dest)       DEST_DIR="${2:-}"; shift 2 ;;
    --identity)   SIGN_IDENTITY="${2:-}"; shift 2 ;;
    --yes|-y)     ASSUME_YES=1; shift ;;
    --no-install) DO_INSTALL=0; shift ;;
    --help|-h)    usage ;;
    *)            die "unknown argument: $1 (try --help)" ;;
  esac
done

[ "$(uname -s)" = "Darwin" ] || die "this script only runs on macOS"

# ---------------------------------------------------------------- locate bundle

if [ -z "$BUNDLE_PATH" ]; then
  step "Locating app bundle"
  found=()
  for base in "${CARGO_TARGET_DIR:-}" "$REPO_ROOT/src-tauri/target"; do
    [ -n "$base" ] || continue
    dir="$base/release/bundle/macos"
    [ -d "$dir" ] || continue
    while IFS= read -r app; do
      found+=("$app")
    done < <(find "$dir" -maxdepth 1 -name '*.app' 2>/dev/null)
  done

  case ${#found[@]} in
    0) die "no .app bundle found. Build one first:
    npm run tauri build
  then re-run this script (or pass --bundle PATH).
  If you build with a custom CARGO_TARGET_DIR, export it here too." ;;
    1) BUNDLE_PATH="${found[0]}" ;;
    *) printf 'error: multiple bundles found; pass --bundle PATH:\n' >&2
       printf '  %s\n' "${found[@]}" >&2; exit 1 ;;
  esac
  note "found $BUNDLE_PATH"
fi

[ -d "$BUNDLE_PATH" ] || die "not a bundle directory: $BUNDLE_PATH"
APP_NAME="$(basename "$BUNDLE_PATH")"

# -------------------------------------------------------------- pick an identity

if [ -z "$SIGN_IDENTITY" ]; then
  SIGN_IDENTITY="$(security find-identity -v -p codesigning 2>/dev/null \
    | awk -F'"' '/Developer ID Application/ { print $2; exit }')"
fi

sign_args=(--force --sign "${SIGN_IDENTITY:=-}")
if [ "$SIGN_IDENTITY" = "-" ]; then
  sign_args+=(--timestamp=none)
else
  # Hardened runtime + a trusted timestamp are prerequisites for notarization.
  sign_args+=(--timestamp --options runtime)
  [ -f "$ENTITLEMENTS" ] && sign_args+=(--entitlements "$ENTITLEMENTS")
fi

step "Signing as: $SIGN_IDENTITY"
if [ "$SIGN_IDENTITY" = "-" ]; then
  note "ad-hoc signature — fine for running locally on this Mac, but the app"
  note "cannot be notarized or distributed to other machines."
fi

# ------------------------------------------------------------------------ sign

# The main executable is sealed by signing the bundle itself, so skip it here.
MAIN_EXE="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleExecutable' \
  "$BUNDLE_PATH/Contents/Info.plist" 2>/dev/null || true)"

# Nested Mach-O first, sorted by path depth descending, so inner code is sealed
# before anything that contains it.
nested=()
while IFS= read -r -d '' f; do
  [ -n "$MAIN_EXE" ] && [ "$f" = "$BUNDLE_PATH/Contents/MacOS/$MAIN_EXE" ] && continue
  if file -b "$f" 2>/dev/null | grep -q 'Mach-O'; then
    nested+=("$f")
  fi
done < <(find "$BUNDLE_PATH/Contents" -type f -print0 2>/dev/null)

if [ ${#nested[@]} -gt 0 ]; then
  step "Signing ${#nested[@]} nested binar$([ ${#nested[@]} -eq 1 ] && echo y || echo ies)"
  while IFS= read -r f; do
    note "${f#"$BUNDLE_PATH"/}"
    codesign "${sign_args[@]}" "$f"
  done < <(printf '%s\n' "${nested[@]}" | awk '{ print gsub(/\//,"/") "\t" $0 }' | sort -rn | cut -f2-)
fi

step "Signing bundle"
codesign "${sign_args[@]}" "$BUNDLE_PATH"

step "Verifying signature"
codesign --verify --deep --strict --verbose=2 "$BUNDLE_PATH"
note "signature valid"

# Gatekeeper will reject an ad-hoc signature; report it without failing the run.
if ! spctl --assess --type exec "$BUNDLE_PATH" >/dev/null 2>&1; then
  note "note: Gatekeeper does not accept this signature (expected when ad-hoc)."
  note "first launch will need right-click > Open, or: xattr -dr com.apple.quarantine <app>"
fi

[ "$DO_INSTALL" -eq 1 ] || { step "Done (--no-install; bundle left in place)"; exit 0; }

# --------------------------------------------------------------------- install

[ -d "$DEST_DIR" ] || die "destination does not exist: $DEST_DIR"
DEST="$DEST_DIR/$APP_NAME"

if [ -e "$DEST" ]; then
  if [ "$ASSUME_YES" -ne 1 ]; then
    printf '\nReplace existing %s? [y/N] ' "$DEST"
    read -r reply </dev/tty || reply=""
    case "$reply" in [yY]|[yY][eE][sS]) ;; *) die "aborted; nothing was installed" ;; esac
  fi
fi

step "Installing to $DEST"
SUDO=""
if [ ! -w "$DEST_DIR" ]; then
  note "$DEST_DIR is not writable; using sudo"
  SUDO="sudo"
fi

# Stage next to the target, then swap, so a failed copy cannot leave a half
# written bundle where the old working one used to be.
STAGE="$DEST_DIR/.$APP_NAME.incoming.$$"
$SUDO rm -rf "$STAGE"
$SUDO ditto "$BUNDLE_PATH" "$STAGE"
$SUDO rm -rf "$DEST"
$SUDO mv "$STAGE" "$DEST"

$SUDO xattr -dr com.apple.quarantine "$DEST" 2>/dev/null || true

step "Installed"
note "$DEST"
note "open it with:  open -a \"$DEST\""
