#!/usr/bin/env python3
"""Freeze the FastAPI sidecar with PyInstaller.

Two layouts are supported:

``onedir`` (default)
    A directory ``src-tauri/binaries/portfolio-sidecar/`` holding the launcher
    and its ``_internal`` tree. Tauri ships it via ``bundle.resources``. Starts
    in well under a second.

``onefile``
    A single ``src-tauri/binaries/portfolio-sidecar[-<target-triple>]``, suited
    to Tauri's ``externalBin``. Self-extracts to a temporary directory on every
    launch, which measured at roughly ten seconds — slow enough that the window
    opens before the backend is listening.

Usage::

    python scripts/build_sidecar.py
    python scripts/build_sidecar.py --mode onefile --target-triple x86_64-apple-darwin

Requires the backend's `package` extra (PyInstaller):
``pip install -e "backend[dev,package]"``.
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

# Development-only packages that dependency analysis otherwise sweeps in — most
# notably mypy, reached through pydantic's optional mypy plugin. None are
# imported at runtime, and together they are tens of megabytes.
EXCLUDED_MODULES = [
    "mypy",
    "pytest",
    "_pytest",
    "black",
    "bandit",
    "coverage",
    "IPython",
    "tkinter",
]


def main() -> int:
    """Build the frozen sidecar binary.

    :returns: Process exit code.
    :rtype: int
    """
    parser = argparse.ArgumentParser(description="Build the frozen sidecar")
    parser.add_argument(
        "--mode",
        choices=("onedir", "onefile"),
        default="onedir",
        help="Output layout (default: onedir, which starts far faster).",
    )
    parser.add_argument(
        "--target-triple",
        default="",
        help="Target triple suffix for the output name. onefile/externalBin only.",
    )
    args = parser.parse_args()

    name = "portfolio-sidecar"
    if args.target_triple:
        if args.mode == "onedir":
            # The onedir tree is bundled as a resource, not an externalBin, so
            # the triple suffix Tauri requires there would only break the path
            # the Rust shell looks for.
            print(
                "note: --target-triple is ignored in onedir mode "
                f"(output stays {OUT_DIR / name})",
                file=sys.stderr,
            )
        else:
            name = f"{name}-{args.target_triple}"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        f"--{args.mode}",
        "--noconfirm",
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

    for module in EXCLUDED_MODULES:
        cmd += ["--exclude-module", module]

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
