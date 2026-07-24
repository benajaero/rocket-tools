# Release Checklist

Use this checklist before publishing a rocket-tools release or announcing the repository for wider
adoption.

## Scope

- Confirm the release version in `pyproject.toml` and `src/rocket_tools/__init__.py`
- Update `CHANGELOG.md` with user-facing additions, changes, fixes, and known limitations
- Check that README claims match the current package status and do not imply certification,
  external validation, or production readiness beyond what has been tested
- Confirm public examples cover the Python library, workflows, MCP stdio server, ASGI/SSE server,
  and CLI subcommands

## Local Validation

```bash
python -m pip install -e ".[dev,release]"
python -m pytest --cov=src --cov-report=xml --cov-fail-under=80
python -m ruff check src/ tests/
python -m ruff format --check src/ tests/
python -m mypy src/
```

Run benchmarks when numerical performance is part of the release note:

```bash
python -m pytest --benchmark-only -q
```

## Package Artifacts

The whole build → `twine check` → clean-room install → smoke-test sequence is
automated as a single reproducible gate:

```bash
scripts/verify_release.sh
```

It exits non-zero on any failure and prints `Release verification PASSED` on
success. The equivalent manual steps are below.

```bash
rm -rf dist
python -m build
python -m twine check dist/*
```

Install the built wheel in a clean environment before publishing:

```bash
python -m venv /tmp/rocket-tools-release
/tmp/rocket-tools-release/bin/python -m pip install dist/*.whl
/tmp/rocket-tools-release/bin/python - <<'PY'
from rocket_tools.aerodynamics import mach_number
from rocket_tools.workflows import list_builtin_workflows

print(mach_number(250.0, 10_000.0))
print(list_builtin_workflows())
PY
```

## MCP and CLI Smoke Tests

The `rocket-tools serve` command starts the stdio MCP server. Verify it from an MCP client using a
minimal configuration:

```json
{
  "mcpServers": {
    "rocket-tools": {
      "command": "rocket-tools",
      "args": ["serve"]
    }
  }
}
```

Verify the ASGI/SSE endpoint starts:

```bash
rocket-tools serve --transport sse --host 127.0.0.1 --port 8000
```

Stop the server after confirming the endpoint is reachable from the intended MCP client.

## Documentation Review

- README install command works from a fresh checkout
- Local validation commands match `.github/workflows/test.yml`
- Python examples use public imports and current response keys
- Workflow examples use `load_builtin_workflow` for packaged examples
- MCP examples distinguish stdio from ASGI/SSE usage
- CLI examples match `rocket-tools --help`
- Known limitations are visible enough that users do not confuse this package with certified
  aerospace analysis software

## Publish

- Create the release commit after validation passes
- Tag the release with the same version as package metadata
- Publish package artifacts only after `twine check` passes
- Attach changelog notes and any validation caveats to the release
