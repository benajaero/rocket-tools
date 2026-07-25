"""Packaging integrity: version single-sourcing, importable modules, tool inventory.

These guard the release surface so it cannot silently drift — a version mismatch
between pyproject and the package, a subpackage that fails to import from a clean
install, or an accidentally dropped tool would all fail here.
"""

import asyncio
import tomllib
from pathlib import Path

import pytest

import rocket_tools

_PYPROJECT = Path(__file__).resolve().parent.parent / "pyproject.toml"


def _pyproject() -> dict:
    with _PYPROJECT.open("rb") as fh:
        return tomllib.load(fh)


def test_version_is_single_sourced():
    """pyproject version must equal rocket_tools.__version__ (drift is a release footgun)."""
    assert _pyproject()["project"]["version"] == rocket_tools.__version__


@pytest.mark.parametrize(
    "module",
    [
        "rocket_tools.server",
        "rocket_tools.provenance",
        "rocket_tools.aerodynamics.aerothermo",
        "rocket_tools.aerodynamics.propulsion",
        "rocket_tools.design.orbital",
        "rocket_tools.uncertainty.engine",
        "rocket_tools.validation.benchmarks",
        "rocket_tools.workflows.engine",
    ],
)
def test_public_modules_import(module):
    __import__(module)


def test_tool_and_resource_inventory():
    """The MCP surface must not silently lose tools/resources."""
    from rocket_tools.server import mcp

    tools = asyncio.run(mcp.list_tools())
    resources = asyncio.run(mcp.list_resources())
    templates = asyncio.run(mcp.list_resource_templates())
    assert len(tools) >= 73
    assert len(resources) >= 5  # concrete resources; templated materials/{name} listed separately
    assert len(templates) >= 1
    # Tool names are unique.
    names = [t.name for t in tools]
    assert len(names) == len(set(names))


def test_console_script_entry_point():
    eps = _pyproject()["project"]["scripts"]
    assert eps["rocket-tools"] == "rocket_tools.cli:main"


def test_typed_marker_shipped():
    """py.typed must be declared so downstream type-checkers trust the package."""
    pkg_data = _pyproject()["tool"]["setuptools"]["package-data"]["rocket_tools"]
    assert "py.typed" in pkg_data
