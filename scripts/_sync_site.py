#!/usr/bin/env python3
"""Patch the live rocket-tools counts into the Human Engine marketing site.

Called by `ship.sh site`. Reads TOOLS / TESTS / BENCHMARKS / SITE_DIR from the
environment and rewrites only the count digits (via anchored patterns), never the
surrounding copy — and only in the live product files, never the historical
`content/releases/*` entries, which are point-in-time snapshots.

Every substitution is printed. A file that yields zero changes prints a warning
so a drifted template can't fail silently.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

# The only files that carry live counts. Release-feed JSON is deliberately excluded.
FILES = [
    "app/rocket-tools/page.tsx",
    "app/rocket-tools/layout.tsx",
    "app/tools/page.tsx",
    "app/data/content.ts",
    "content/case-notes/case-06.json",
]

# (regex, count-key). The digit run is the whole match (lookaround anchors the noun)
# or group 2 (a prefix key in group 1 is preserved). Applied to every file; a rule
# that doesn't apply simply matches nothing.
SUFFIX_RULES = [
    (r"\d+(?=\s+validated aerospace tools\b)", "TOOLS"),
    (r"\d+(?=\s+validated tools\b)", "TOOLS"),
    (r"\d+(?=\s+MCP tools\b)", "TOOLS"),
    (r"\d+(?=\s+precision tools\b)", "TOOLS"),
    (r"(?<=all )\d+(?=\s+tools\b)", "TOOLS"),
    (r"\d+(?=\s+Tests\b)", "TESTS"),
    (r"\d+(?=\s+tests\b)", "TESTS"),
    (r"\d+(?=\s+Benchmarks\b)", "BENCHMARKS"),
    (r"\d+(?=\s+reference benchmarks\b)", "BENCHMARKS"),
    (r"\d+(?=\s+benchmarks\b)", "BENCHMARKS"),
]
# (regex with prefix group 1 + digit group 2, count-key)
PREFIX_RULES = [
    (r'(value: ")(\d+)(?=", label: "MCP tools")', "TOOLS"),
    (r'(value: ")(\d+)(?=", label: "Tests")', "TESTS"),
    (r'("metric":\s*"MCP Tools",\s*"value":\s*")(\d+)', "TOOLS"),
    (r'("metric":\s*"Tests",\s*"value":\s*")(\d+)', "TESTS"),
]


def apply_rules(text: str, counts: dict[str, str]) -> tuple[str, int]:
    changes = 0

    def suffix_repl(key: str):
        def _r(m: re.Match[str]) -> str:
            nonlocal changes
            if m.group(0) != counts[key]:
                changes += 1
            return counts[key]

        return _r

    def prefix_repl(key: str):
        def _r(m: re.Match[str]) -> str:
            nonlocal changes
            if m.group(2) != counts[key]:
                changes += 1
            return m.group(1) + counts[key]

        return _r

    for pat, key in SUFFIX_RULES:
        text = re.sub(pat, suffix_repl(key), text)
    for pat, key in PREFIX_RULES:
        text = re.sub(pat, prefix_repl(key), text, flags=re.DOTALL)
    return text, changes


def main() -> None:
    site = Path(os.environ["SITE_DIR"]).expanduser()
    counts = {k: os.environ[k] for k in ("TOOLS", "TESTS", "BENCHMARKS")}
    total = 0
    for rel in FILES:
        path = site / rel
        if not path.exists():
            print(f"warn: {rel} not found — skipping")
            continue
        new, n = apply_rules(path.read_text(), counts)
        if n:
            path.write_text(new)
            print(f"  {rel}: {n} count(s) updated")
        else:
            print(f"  {rel}: no change")
        total += n
    print(f"sync complete: {total} substitution(s) → {counts}")


if __name__ == "__main__":
    main()
