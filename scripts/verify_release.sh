#!/usr/bin/env bash
# Reproducible release gate: build the artifacts, check them, install the wheel in
# a throwaway virtualenv (no repo on sys.path), and smoke-test the public surface.
# Run from the repo root: scripts/verify_release.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> Clean previous build artifacts"
rm -rf dist build src/rocket_tools.egg-info

echo "==> Build sdist + wheel"
python -m build

echo "==> twine check"
python -m twine check dist/*

wheels=(dist/*.whl)
WHEEL="${wheels[0]}"
CLEAN="$(mktemp -d)/venv"
echo "==> Clean-room install into ${CLEAN}"
python -m venv "${CLEAN}"
"${CLEAN}/bin/pip" install --quiet --upgrade pip
"${CLEAN}/bin/pip" install --quiet "${WHEEL}"

echo "==> Smoke test the installed package (repo not on sys.path)"
( cd /tmp && "${CLEAN}/bin/python" - <<'PY'
import asyncio
import rocket_tools
from rocket_tools.server import mcp
from rocket_tools.design import hohmann_transfer
from rocket_tools.materials import isa_atmosphere
from rocket_tools.provenance import get_provenance

tools = asyncio.run(mcp.list_tools())
resources = asyncio.run(mcp.list_resources())
assert len(tools) >= 81, f"expected >=81 tools, got {len(tools)}"
assert len(resources) >= 5, f"expected >=5 resources, got {len(resources)}"
# A couple of reference-validated computations must survive packaging.
assert abs(hohmann_transfer(6678137.0, 42164137.0)["total_delta_v_kms"] - 3.8926) < 1e-3
assert abs(isa_atmosphere(84852.0)["pressure_pa"] - 0.3733) < 1e-3
assert get_provenance("normal_shock")["validated"] is True
print(f"OK: rocket-tools {rocket_tools.__version__} - {len(tools)} tools, {len(resources)} resources")
PY
)

echo "==> Release verification PASSED"
