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


class TestServerListMaterials:
    def test_list_materials(self):
        result = asyncio.run(_call_tool("list_materials", {}))
        if isinstance(result, tuple):
            data = [item.text for item in result[0]]
        elif (
            isinstance(result, list)
            and result
            and isinstance(result[0], list)
            and all(hasattr(item, "text") for item in result[0])
        ):
            data = [item.text for item in result[0]]
        elif isinstance(result, list) and all(isinstance(item, str) for item in result):
            data = result
        else:
            data = json.loads(result[0].text)
        assert len(data) >= 5
        assert "6061-T6" in data


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


# The error contract every tool must honour so an agent can branch on it reliably.
_ERROR_KEYS = {
    "error",
    "error_code",
    "error_type",
    "message",
    "parameter",
    "constraint",
    "suggestion",
}


class TestServerErrorContract:
    def _error(self, name: str, params: dict) -> dict:
        result = asyncio.run(_call_tool(name, params))
        return json.loads(result[0].text)

    def test_invalid_value_is_invalid_parameter_not_internal(self):
        # A negative velocity is the caller's mistake, not a server fault.
        data = self._error("mach_number", {"velocity": -5.0, "altitude_m": 0.0})
        assert data["error"] is True
        assert data["error_code"] == "INVALID_PARAMETER"
        assert data["error_type"] == "invalid_parameter"
        assert data["parameter"] == "velocity"
        assert "velocity" in data["message"]

    def test_invalid_enum_names_the_parameter(self):
        # A correctly-typed but out-of-set enum value reaches the tool's own
        # validation (gross type mismatches are rejected earlier by FastMCP).
        data = self._error(
            "beam_analysis",
            {
                "load": 100.0,
                "length": 2.0,
                "youngs_modulus": 200e9,
                "cross_section": {"type": "rectangle", "width": 0.05, "height": 0.01},
                "support_type": "floating",
            },
        )
        assert data["error_code"] == "INVALID_PARAMETER"
        assert data["parameter"] == "support_type"
        assert "simply_supported" in data["message"]

    def test_nested_field_error_reports_the_bad_input(self):
        data = self._error(
            "beam_analysis",
            {
                "load": -1.0,
                "length": 2.0,
                "youngs_modulus": 200e9,
                "cross_section": {"type": "rectangle", "width": 0.05, "height": 0.01},
            },
        )
        assert data["error_code"] == "INVALID_PARAMETER"
        assert data["parameter"] == "load"

    def test_error_schema_is_consistent_across_error_kinds(self):
        # Out-of-range value and out-of-set enum must share one schema.
        range_err = self._error("mach_number", {"velocity": -5.0, "altitude_m": 0.0})
        enum_err = self._error(
            "beam_analysis",
            {
                "load": 100.0,
                "length": 2.0,
                "youngs_modulus": 200e9,
                "cross_section": {"type": "rectangle", "width": 0.05, "height": 0.01},
                "support_type": "floating",
            },
        )
        assert set(range_err) == _ERROR_KEYS
        assert set(enum_err) == _ERROR_KEYS
