"""Tests for the provenance registry and the research citation tools."""

import asyncio
import json

import pytest

from rocket_tools.provenance import (
    _PROVENANCE,
    get_provenance,
    list_documented_tools,
    list_references,
)
from rocket_tools.server import mcp

# Meta/research tools that describe or orchestrate rather than compute a physical result,
# plus visualization tools (presentation, not composable physics — see viz/).
META_TOOLS = {
    "cite_tool",
    "list_references",
    "propagate_uncertainty",
    "list_validation_benchmarks",
    "validate_result",
    "parameter_sweep",
    "list_standards",
    "plot_beam_diagrams",
    "plot_drag_polar",
    "plot_nozzle_contour",
    "plot_isa_profile",
    "plot_trajectory",
}


def _registered_tool_names() -> set[str]:
    return {t.name for t in asyncio.run(mcp.list_tools())}


class TestRegistryIntegrity:
    def test_every_physics_tool_has_provenance(self):
        """Every registered tool (except meta tools) must be documented, so the
        registry cannot silently fall out of sync as tools are added."""
        registered = _registered_tool_names() - META_TOOLS
        missing = sorted(registered - set(_PROVENANCE))
        assert not missing, f"tools without provenance: {missing}"

    def test_no_provenance_for_unknown_tools(self):
        registered = _registered_tool_names()
        stale = sorted(set(_PROVENANCE) - registered)
        assert not stale, f"provenance for non-existent tools: {stale}"

    def test_entries_are_well_formed(self):
        for name, entry in _PROVENANCE.items():
            assert entry["references"], f"{name} has no references"
            assert entry["formula"].strip(), f"{name} has no formula"
            assert entry["assumptions"], f"{name} has no assumptions"

    def test_bibliography_nonempty_and_deduped(self):
        refs = list_references()
        assert len(refs) > 10
        assert len(refs) == len(set(refs))


class TestGetProvenance:
    def test_validated_tool_links_benchmark(self):
        p = get_provenance("normal_shock")
        assert p["domain"] == "compressible flow"
        assert any("NACA" in r for r in p["references"])
        assert p["validated"] is True
        assert p["validation_benchmarks"]  # cross-linked from the benchmark set

    def test_unvalidated_tool_reports_false(self):
        # A correct tool that simply has no curated benchmark yet.
        p = get_provenance("orbital_period")
        assert p["validated"] is False
        assert p["validation_benchmarks"] == []

    def test_unknown_tool_raises(self):
        with pytest.raises(ValueError):
            get_provenance("does_not_exist")

    def test_documented_tools_sorted(self):
        tools = list_documented_tools()
        assert tools == sorted(tools)


class TestResearchToolsViaMCP:
    def _call(self, name, params):
        result = asyncio.run(mcp.call_tool(name, params))
        return json.loads(result[0].text)

    def test_cite_tool(self):
        data = self._call("cite_tool", {"tool_name": "hohmann_transfer"})
        assert data["tool"] == "hohmann_transfer"
        assert any("Curtis" in r for r in data["references"])
        assert "formula" in data and "assumptions" in data

    def test_cite_tool_unknown_is_structured_error(self):
        data = self._call("cite_tool", {"tool_name": "flux_capacitor"})
        assert data["error"] is True
        assert data["error_code"] == "INTERNAL_ERROR"  # library ValueError -> internal
        assert "flux_capacitor" in data["message"]

    def test_list_references(self):
        data = self._call("list_references", {})
        assert data["documented_tool_count"] == len(_PROVENANCE)
        assert any("NIST" in r for r in data["references"])
