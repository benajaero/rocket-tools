"""Tests for the MCP server exposing aerospace engineering tools."""

import asyncio
import json

from rocket_tools.server import mcp


async def _call_tool(name: str, params: dict):
    return await mcp.call_tool(name, params)


class TestServerUnitConvert:
    def test_m_to_mm(self):
        result = asyncio.run(
            _call_tool("unit_convert", {"value": 1.0, "from_unit": "m", "to_unit": "mm"})
        )
        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data["converted_value"] == 1000.0


class TestServerMaterialLookup:
    def test_6061_t6(self):
        result = asyncio.run(_call_tool("material_lookup", {"name": "6061-T6"}))
        data = json.loads(result[0].text)
        assert data["youngs_modulus_pa"] == 68.9e9


class TestServerISA:
    def test_sea_level(self):
        result = asyncio.run(_call_tool("isa_atmosphere", {"altitude_m": 0.0}))
        data = json.loads(result[0].text)
        assert data["temperature_k"] == 288.15


class TestServerBeamAnalysis:
    def test_simply_supported(self):
        result = asyncio.run(
            _call_tool(
                "beam_analysis",
                {
                    "load": 1000.0,
                    "length": 2.0,
                    "youngs_modulus": 68.9e9,
                    "cross_section": {"type": "rectangle", "width": 0.05, "height": 0.01},
                },
            )
        )
        data = json.loads(result[0].text)
        assert data["max_deflection_m"] > 0


class TestServerAeroAnalysis:
    def test_comprehensive(self):
        result = asyncio.run(
            _call_tool(
                "aero_analysis",
                {
                    "velocity": 100.0,
                    "altitude_m": 5000.0,
                    "characteristic_length": 2.0,
                    "reference_area": 10.0,
                    "lift": 50000.0,
                    "drag": 5000.0,
                },
            )
        )
        data = json.loads(result[0].text)
        assert "reynolds_number" in data
        assert "mach_number" in data
