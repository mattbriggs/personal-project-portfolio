#!/usr/bin/env python3
"""Fail if renderer production code performs direct HTTP or reads the sidecar port/token.

Enforces the SRS boundary rule: the renderer must reach the backend only through
the typed Tauri command client. This static check scans ``frontend/src`` for
forbidden patterns, excluding test files and the command-client module (which
legitimately calls ``invoke``).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_SRC = REPO_ROOT / "frontend" / "src"

FORBIDDEN = [
    re.compile(r"\bfetch\s*\("),
    re.compile(r"\bXMLHttpRequest\b"),
    re.compile(r"\baxios\b"),
    re.compile(r"127\.0\.0\.1"),
    re.compile(r"localhost:"),
    re.compile(r"X-API-Key", re.IGNORECASE),
]

EXCLUDE_DIRS = {"generated", "test", "__tests__"}
EXCLUDE_SUFFIXES = (".test.ts", ".test.tsx", ".spec.ts", ".spec.tsx")


def _iter_source_files() -> list[Path]:
    files: list[Path] = []
    for path in FRONTEND_SRC.rglob("*"):
        if path.suffix not in {".ts", ".tsx"}:
            continue
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        if path.name.endswith(EXCLUDE_SUFFIXES):
            continue
        files.append(path)
    return files


def main() -> int:
    """Scan renderer sources for forbidden network patterns.

    :returns: 0 when clean, 1 when a violation is found.
    :rtype: int
    """
    if not FRONTEND_SRC.exists():
        print(f"No frontend source at {FRONTEND_SRC}; nothing to check.")
        return 0

    violations: list[str] = []
    for path in _iter_source_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for line_no, line in enumerate(text.splitlines(), start=1):
            for pattern in FORBIDDEN:
                if pattern.search(line):
                    rel = path.relative_to(REPO_ROOT)
                    violations.append(f"{rel}:{line_no}: {line.strip()}")

    if violations:
        print("Renderer contains forbidden direct-network usage:")
        for v in violations:
            print(f"  {v}")
        return 1
    print("OK: renderer performs no direct HTTP.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
