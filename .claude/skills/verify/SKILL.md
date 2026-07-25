---
name: verify
description: Run the rocket-tools check gauntlet (tests, lint, format, types, and optionally the clean-room release build). Use before every commit and before cutting a release.
---

# Verify

The gates that CI enforces. Run them from the repo root with the project virtualenv
(`.venv`). `tests/conftest.py` already sets `NUMBA_DISABLE_JIT=1`, so coverage traces the
Numba kernels as pure Python.

## The standard gauntlet (before every commit)

```bash
.venv/bin/pytest -q                         # full suite, must be all green
.venv/bin/ruff check src/ tests/            # lint, must pass
.venv/bin/ruff format --check src/ tests/   # format, must pass
.venv/bin/mypy src/                          # types, must be clean
```

If `ruff check` reports an unsorted import block, fix it with `.venv/bin/ruff check --fix`.
If `ruff format --check` wants changes, apply them with `.venv/bin/ruff format`. A long
f-string line that the formatter cannot break has to be shortened by hand (pull the
expression into a variable above the `print`).

The coverage gate is `--cov-fail-under=80`. New code should not drop total coverage; cover
the validation-error branches with reject tests.

## The clean-room build (before a release, and worth running after adding tools)

```bash
export PATH="$PWD/.venv/bin:$PATH"
bash scripts/verify_release.sh
```

This builds the sdist and wheel, runs `twine check`, installs the wheel into a throwaway
virtualenv with the repo off `sys.path`, and smoke-tests the public surface. It prints
`OK: rocket-tools <version> - <N> tools, <M> resources` on success. `set -euo pipefail`
means any failing step aborts before that line. Afterwards, remove the build artifacts:

```bash
rm -rf dist build src/rocket_tools.egg-info
```

## When something fails

- A `test_provenance` failure means a new tool has no `_PROVENANCE` entry.
- A `test_all_tools_happy_path` failure means a new tool has no `VALID_CALLS` entry.
- A `test_packaging` inventory failure means the tool floor is stale (or a tool was dropped).
- A numpy `np.True_ is True` assertion failure means a boolean output was not cast with
  `bool(...)` in the domain function.
