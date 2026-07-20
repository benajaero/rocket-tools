"""Tests for the MCP resources (readable research datasets)."""

import asyncio
import json

from rocket_tools.server import mcp


def _read(uri: str) -> str:
    contents = list(asyncio.run(mcp.read_resource(uri)))
    return contents[0].content


class TestResourceListing:
    def test_static_resources_registered(self):
        uris = {str(r.uri) for r in asyncio.run(mcp.list_resources())}
        assert {
            "rocket-tools://references",
            "rocket-tools://benchmarks",
            "rocket-tools://provenance",
            "rocket-tools://materials",
        } <= uris

    def test_material_template_registered(self):
        templates = {t.uriTemplate for t in asyncio.run(mcp.list_resource_templates())}
        assert "rocket-tools://materials/{name}" in templates


class TestResourceContent:
    def test_references(self):
        data = json.loads(_read("rocket-tools://references"))
        assert len(data["references"]) > 10
        assert "normal_shock" in data["documented_tools"]

    def test_benchmarks(self):
        data = json.loads(_read("rocket-tools://benchmarks"))
        assert "normal_shock_mach_2" in data
        bm = data["normal_shock_mach_2"]
        assert "expected" in bm and "reference" in bm and "tolerance" in bm

    def test_provenance(self):
        data = json.loads(_read("rocket-tools://provenance"))
        assert len(data) == 50  # every computational tool documented
        assert data["hohmann_transfer"]["validated"] in (True, False)
        assert data["normal_shock"]["references"]

    def test_materials(self):
        data = json.loads(_read("rocket-tools://materials"))
        assert len(data) >= 45
        assert data["6061-T6"]["yield_strength_mpa"] == 276.0

    def test_material_template(self):
        data = json.loads(_read("rocket-tools://materials/Ti-6Al-4V"))
        assert data["material_name"] == "Ti-6Al-4V"
        assert data["youngs_modulus_gpa"] > 0

    def test_material_template_unknown_returns_error(self):
        data = json.loads(_read("rocket-tools://materials/unobtanium"))
        assert data["error"] is True
