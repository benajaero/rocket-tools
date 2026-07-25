"""Tests for the expanded router intent coverage across the MCP tool surface."""

import pytest

from rocket_tools.router import route_query
from rocket_tools.router.engine import ClarificationRequest, ToolCall


class TestRouterCompressibleFlow:
    def test_isentropic_flow(self):
        result = route_query("What is the isentropic pressure ratio at Mach 2.5 with gamma 1.4?")
        assert isinstance(result, ToolCall)
        assert result.tool_name == "isentropic_flow"
        assert result.params["mach"] == pytest.approx(2.5)
        assert result.params["gamma"] == pytest.approx(1.4)

    def test_normal_shock(self):
        result = route_query("Normal shock relations for Mach 3")
        assert isinstance(result, ToolCall)
        assert result.tool_name == "normal_shock"
        assert result.params["mach1"] == pytest.approx(3.0)

    def test_oblique_shock(self):
        result = route_query("Oblique shock for Mach 2.5 deflection 10 degrees")
        assert isinstance(result, ToolCall)
        assert result.tool_name == "oblique_shock"
        assert result.params["mach1"] == pytest.approx(2.5)
        assert result.params["deflection_deg"] == pytest.approx(10.0)

    def test_prandtl_meyer(self):
        result = route_query("Prandtl Meyer angle at Mach 2")
        assert isinstance(result, ToolCall)
        assert result.tool_name == "prandtl_meyer"
        assert result.params["mach"] == pytest.approx(2.0)


class TestRouterAircraft:
    def test_lift_curve_slope(self):
        result = route_query("Lift curve slope for Mach 0.8 aspect ratio 8")
        assert isinstance(result, ToolCall)
        assert result.tool_name == "lift_curve_slope"
        assert result.params["mach"] == pytest.approx(0.8)
        assert result.params["aspect_ratio"] == pytest.approx(8.0)

    def test_wing_loading(self):
        result = route_query("Wing loading for 5000N on wing area 10 m2")
        assert isinstance(result, ToolCall)
        assert result.tool_name == "wing_loading"
        assert result.params["weight_n"] == pytest.approx(5000.0)
        assert result.params["wing_area_m2"] == pytest.approx(10.0)


class TestRouterMissionDesign:
    def test_rocket_delta_v(self):
        result = route_query(
            "Rocket delta-v for Isp 320, initial mass 10000 kg, final mass 2000 kg"
        )
        assert isinstance(result, ToolCall)
        assert result.tool_name == "rocket_delta_v"
        assert result.params["specific_impulse_s"] == pytest.approx(320.0)

    def test_orbital_velocity(self):
        result = route_query("Orbital velocity at 400 km altitude")
        assert isinstance(result, ToolCall)
        assert result.tool_name == "orbital_velocity"
        assert result.params["altitude_m"] == pytest.approx(400000.0)

    def test_thrust_to_weight(self):
        result = route_query("Thrust to weight for 10000N thrust and 500kg mass")
        assert isinstance(result, ToolCall)
        assert result.tool_name == "thrust_to_weight"
        assert result.params["thrust_n"] == pytest.approx(10000.0)
        assert result.params["mass_kg"] == pytest.approx(500.0)

    def test_propellant_tank_sizing(self):
        result = route_query("Size a propellant tank for 5 m3")
        assert isinstance(result, ToolCall)
        assert result.tool_name == "propellant_tank_sizing"
        assert result.params["propellant_volume_m3"] == pytest.approx(5.0)


class TestRouterStructural:
    def test_column_buckling(self):
        result = route_query("Column buckling for 2m column")
        if isinstance(result, ClarificationRequest):
            assert "column_buckling" in result.possible_tools
        else:
            assert result.tool_name == "column_buckling"

    def test_margin_of_safety(self):
        result = route_query(
            "Margin of safety with allowable stress 300 MPa and actual stress 200 MPa"
        )
        assert isinstance(result, ToolCall)
        assert result.tool_name == "margin_of_safety"

    def test_von_mises_stress(self):
        result = route_query("Von Mises stress for sigma x 200 MPa")
        assert isinstance(result, ToolCall)
        assert result.tool_name == "von_mises_stress"


class TestRouterAstrodynamics:
    def test_hohmann_routes_to_correct_tool(self):
        # Previously the greedy unit_convert "N unit to unit" pattern hijacked this.
        result = route_query("hohmann transfer from 300km to GEO")
        assert isinstance(result, ClarificationRequest)
        assert result.possible_tools == ["hohmann_transfer"]

    def test_bi_elliptic(self):
        result = route_query("bi-elliptic transfer")
        assert isinstance(result, ClarificationRequest)
        assert result.possible_tools == ["bi_elliptic_transfer"]

    def test_plane_change_extracts_params(self):
        result = route_query("plane change at 7500 m/s with 20 degree inclination change")
        assert isinstance(result, ToolCall)
        assert result.tool_name == "plane_change_delta_v"
        assert result.params["velocity_ms"] == pytest.approx(7500.0)
        assert result.params["inclination_change_deg"] == pytest.approx(20.0)

    def test_vis_viva_names_correct_tool(self):
        result = route_query("vis-viva velocity")
        assert isinstance(result, ClarificationRequest)
        assert result.possible_tools == ["vis_viva_velocity"]
