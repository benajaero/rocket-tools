# Working in rocket-tools

A multi-domain aerospace engineering library exposed three ways from one core: a Python
library, a `rocket-tools` CLI, and an MCP server. There are 81 computational tools across
structures, aerodynamics, compressible flow, propulsion, orbital mechanics, trajectory,
optimization, and reliability.

## The one rule

A number is only worth shipping if you can trace it to a source and check it against a known
answer. Every tool validates its inputs, rejects NaN and infinity at the boundary (via
`StrictModel`), carries a provenance entry, and is pinned to a textbook value or an exact
hand computation in a test. Do not add a tool you cannot validate.

## Commands

Use the project virtualenv (`.venv`). `tests/conftest.py` sets `NUMBA_DISABLE_JIT=1` so
coverage traces the Numba kernels honestly.

```bash
.venv/bin/pytest -q                         # full suite
.venv/bin/ruff check src/ tests/            # lint (add --fix to sort imports)
.venv/bin/ruff format --check src/ tests/   # format (drop --check to apply)
.venv/bin/mypy src/                          # types
bash scripts/verify_release.sh              # clean-room build + install (before a release)
```

`scripts/ship.sh` is the update/release pipeline — one command for the whole loop:

```bash
scripts/ship.sh check                 # full gauntlet only
scripts/ship.sh counts                # live tool/test/benchmark counts (single source of truth)
scripts/ship.sh merge [BRANCH]        # gauntlet, ff-merge into main, push
scripts/ship.sh release X.Y.Z         # bump, changelog, clean-room build, tag, push, wait for PyPI
scripts/ship.sh site                  # sync counts into the marketing site, build, deploy
scripts/ship.sh ship X.Y.Z            # release + site in one shot   (DRY_RUN=1 to preview)
```

## Skills for common tasks

- **`add-tool`** — the seven-file pattern for adding a new validated MCP tool.
- **`verify`** — the full check gauntlet, and what each failure means.
- **`release`** — bump the version, tag, and publish to PyPI (maintainer go-ahead only).

## Gotchas

- Cast numpy scalars and booleans in domain-function outputs (`float(...)`, `bool(...)`);
  a raw `np.True_` fails an `is True` assertion and `np.float64` trips mypy.
- Adding a tool means bumping the count in `README.md`, `tests/test_packaging.py`, and
  `scripts/verify_release.sh`, and adding a `CHANGELOG.md` `[Unreleased]` bullet.
- Keep import blocks isort-ordered in `server.py` and `schemas/__init__.py`.
- The version must match across `pyproject.toml`, `src/rocket_tools/__init__.py`, and
  `CITATION.cff` (a test enforces it).
- Commit and push as the maintainer, with no AI attribution trailers.

## Scope

This is a preliminary-design and education library, not certification software. See
`docs/scientific-validity.md` for what "validated" means and the known limits, and
`ROADMAP.md` for what is coming. Promotion is on hold until the maintainer says otherwise.
