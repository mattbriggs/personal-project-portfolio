#!/usr/bin/env python3
"""Freeze the FastAPI sidecar into a standalone binary with PyInstaller.

Produces a single-file binary named `portfolio-sidecar` (Tauri external binary),
optionally suffixed with the Rust target triple for `externalBin` bundling.

Usage::

    python scripts/build_sidecar.py [--target-triple x86_64-apple-darwin]

The output is written to `src-tauri/binaries/`. Requires the backend's
`package` extra (PyInstaller): `pip install -e "backend[dev,package]"`.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_SRC = REPO_ROOT / "backend" / "src"
ENTRY = BACKEND_SRC / "portfolio_manager" / "cli" / "sidecar.py"
OUT_DIR = REPO_ROOT / "src-tauri" / "binaries"

# Non-Python files that must ship inside the binary. ``--collect-submodules``
# gathers modules only, so anything read from disk at runtime has to be listed
# here or the frozen sidecar dies on startup with FileNotFoundError.
#
# Each entry is a path relative to ``backend/src``; it is bundled at the same
# relative location, which is what the ``Path(__file__).parents[...]`` lookups
# in the package resolve to once PyInstaller unpacks itself.
DATA_FILES = [
    Path("portfolio_manager/infrastructure/db/schema.sql"),
]


def main() -> int:
    """Build the frozen sidecar binary.

    :returns: Process exit code.
    :rtype: int
    """
    parser = argparse.ArgumentParser(description="Build the frozen sidecar binary")
    parser.add_argument(
        "--target-triple",
        default="",
        help="Rust target triple suffix for the output name (Tauri externalBin).",
    )
    args = parser.parse_args()

    name = "portfolio-sidecar"
    if args.target_triple:
        name = f"{name}-{args.target_triple}"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--name",
        name,
        "--distpath",
        str(OUT_DIR),
        "--paths",
        str(BACKEND_SRC),
        "--collect-submodules",
        "portfolio_manager",
        "--hidden-import",
        "uvicorn.logging",
    ]

    for rel in DATA_FILES:
        source = BACKEND_SRC / rel
        if not source.is_file():
            print(f"error: required data file is missing: {source}", file=sys.stderr)
            return 1
        cmd += ["--add-data", f"{source}{os.pathsep}{rel.parent}"]

    cmd.append(str(ENTRY))
    print("Running:", " ".join(cmd))
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
