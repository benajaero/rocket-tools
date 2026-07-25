#!/usr/bin/env python3
"""Bump the version across the three pinned files and finalize the changelog.

Called by ship.sh; safe to run directly:  python scripts/_bump_version.py X.Y.Z 2026-07-26

Edits are idempotent-ish and fail loudly if an expected anchor is missing, so a
half-applied bump never slips through.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _sub_once(path: Path, pattern: str, repl: str, *, flags: int = 0) -> None:
    text = path.read_text()
    new, n = re.subn(pattern, repl, text, count=1, flags=flags)
    if n != 1:
        raise SystemExit(f"error: {path.name}: expected exactly one match for /{pattern}/, got {n}")
    path.write_text(new)


def bump(version: str, date: str) -> None:
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise SystemExit(f"error: bad version {version!r} (want X.Y.Z)")

    _sub_once(ROOT / "pyproject.toml", r'(?m)^version = "[^"]+"', f'version = "{version}"')
    _sub_once(
        ROOT / "src/rocket_tools/__init__.py",
        r'(?m)^__version__ = "[^"]+"',
        f'__version__ = "{version}"',
    )
    _sub_once(ROOT / "CITATION.cff", r'(?m)^version: "[^"]+"', f'version: "{version}"')
    _sub_once(ROOT / "CITATION.cff", r'(?m)^date-released: "[^"]+"', f'date-released: "{date}"')

    _finalize_changelog(version, date)
    print(f"bumped to {version} ({date})")


def _finalize_changelog(version: str, date: str) -> None:
    path = ROOT / "CHANGELOG.md"
    text = path.read_text()
    if f"[{version}]" in text:
        print(f"changelog already has [{version}] — leaving as is")
        return
    # Rename the current [Unreleased] to [version] — date and open a fresh empty one above it.
    marker = "## [Unreleased]"
    if marker not in text:
        raise SystemExit("error: CHANGELOG.md has no '## [Unreleased]' section to finalize")
    replacement = f"## [Unreleased]\n\n## [{version}] — {date}"
    path.write_text(text.replace(marker, replacement, 1))
    print(f"finalized changelog: [Unreleased] -> [{version}] — {date}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: _bump_version.py X.Y.Z YYYY-MM-DD")
    bump(sys.argv[1], sys.argv[2])
