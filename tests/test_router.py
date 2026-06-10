"""Tests for the natural language router."""

import pytest

from rocket_tools.router import ClarificationRequest, ToolCall, route_query


class TestRouterBeam:
    def test_beam_simple(self):
        result = route_query("Can a beam handle 500N over 2m?")
        assert isinstance(result, ToolCall)
        assert result.tool_name == "beam_analysis"
        assert result.params["load"] == 500.0
        assert result.params["length"] == 2.0
        assert result.confidence >= 0.6

    def test_beam_with_material(self):
        result = route_query("Design a 6061-T6 beam for 1000N, 1.5m")
        assert isinstance(result, ToolCall)
        assert result.tool_name == "beam_analysis"
        assert result.params["load"] == 1000.0
        assert result.params["length"] == 1.5
        assert result.params["youngs_modulus"] == 68.9e9

    def test_beam_missing_params(self):
        result = route_query("Beam analysis")
        assert isinstance(result, ClarificationRequest)


class TestRouterAero:
    def test_aero_analysis(self):
        result = route_query("What is the Reynolds number at 100 m/s and 5000m?")
        assert isinstance(result, ToolCall)
        assert result.tool_name == "aero_analysis"
        assert result.params["velocity"] == 100.0
        assert result.params["altitude_m"] == 5000.0


class TestRouterMaterial:
    def test_material_lookup(self):
        result = route_query("What are the properties of Ti-6Al-4V?")
        assert isinstance(result, ToolCall)
        assert result.tool_name == "material_lookup"
        assert result.params["name"] == "Ti-6Al-4V"


class TestRouterUnknown:
    def test_no_match(self):
        result = route_query("Hello world")
        assert isinstance(result, ClarificationRequest)


class TestRouterConfidence:
    def test_beam_partial_params(self):
        result = route_query("Can a beam handle 500N over 2m?")
        assert isinstance(result, ToolCall)
        assert result.confidence == pytest.approx(2 / 3, abs=0.01)

    def test_beam_full_params(self):
        result = route_query("Design a 6061-T6 beam for 1000N, 1.5m")
        assert isinstance(result, ToolCall)
        assert result.confidence == pytest.approx(1.0, abs=0.01)

    def test_material_full_params(self):
        result = route_query("What are the properties of Ti-6Al-4V?")
        assert isinstance(result, ToolCall)
        assert result.confidence == pytest.approx(1.0, abs=0.01)


class TestRouterUnitConvert:
    def test_convert_length(self):
        result = route_query("Convert 100 mm to m")
        assert isinstance(result, ToolCall)
        assert result.tool_name == "unit_convert"
        assert result.params["value"] == 100.0
        assert result.params["from_unit"] == "mm"
        assert result.params["to_unit"] == "m"

    def test_convert_pressure(self):
        result = route_query("Convert 14.7 psi to kPa")
        assert isinstance(result, ToolCall)
        assert result.tool_name == "unit_convert"
        assert result.params["value"] == 14.7
        assert result.params["from_unit"] == "psi"
        assert result.params["to_unit"] == "kpa"

    def test_convert_missing_value(self):
        result = route_query("Convert psi to kPa")
        assert isinstance(result, ClarificationRequest)


class TestRouterSessionMemory:
    def test_session_fills_missing_params(self):
        from rocket_tools.memory import SessionMemory

        session = SessionMemory(session_id="test-1")
        session.parameters["beam_analysis"] = {"load": 500.0, "length": 2.0}

        result = route_query("Beam analysis", session=session)
        assert isinstance(result, ToolCall)
        assert result.tool_name == "beam_analysis"
        assert result.params["load"] == 500.0
        assert result.params["length"] == 2.0

    def test_session_overridden_by_query(self):
        from rocket_tools.memory import SessionMemory

        session = SessionMemory(session_id="test-2")
        session.parameters["beam_analysis"] = {"load": 500.0, "length": 2.0}

        result = route_query("Beam analysis for 1000N", session=session)
        assert isinstance(result, ToolCall)
        assert result.params["load"] == 1000.0
        assert result.params["length"] == 2.0
