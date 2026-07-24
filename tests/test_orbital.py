"""Tests for orbital-mechanics tools, validated against textbook worked examples."""

import math

import pytest

from rocket_tools.design import (
    hohmann_transfer,
    orbital_period,
    plane_change_delta_v,
    vis_viva_velocity,
)

MU_EARTH = 3.986004418e14
RE = 6_378_137.0  # equatorial radius (m)


class TestVisViva:
    def test_circular_matches_sqrt_mu_over_r(self):
        r = RE + 300e3
        got = vis_viva_velocity(r, r)["velocity_ms"]
        assert got == pytest.approx(math.sqrt(MU_EARTH / r), rel=1e-6)

    def test_apoapsis_raises_when_radius_exceeds_orbit(self):
        with pytest.raises(ValueError):
            vis_viva_velocity(2.0 * RE, RE)  # 2/r - 1/a < 0


class TestHohmann:
    def test_leo_to_geo(self):
        # Curtis, "Orbital Mechanics for Engineering Students": 300 km LEO -> GEO.
        r1 = RE + 300e3
        r2 = RE + 35_786e3
        res = hohmann_transfer(r1, r2)
        assert res["delta_v1_ms"] == pytest.approx(2425.7, rel=2e-4)
        assert res["delta_v2_ms"] == pytest.approx(1466.8, rel=2e-4)
        assert res["total_delta_v_ms"] == pytest.approx(3892.5, rel=2e-4)
        assert res["transfer_time_hr"] == pytest.approx(5.275, rel=1e-3)
        assert res["raising_orbit"] is True

    def test_symmetry_of_total_delta_v(self):
        r1, r2 = RE + 300e3, RE + 35_786e3
        up = hohmann_transfer(r1, r2)["total_delta_v_ms"]
        down = hohmann_transfer(r2, r1)["total_delta_v_ms"]
        assert up == pytest.approx(down, rel=1e-9)

    def test_equal_radii_rejected(self):
        with pytest.raises(ValueError):
            hohmann_transfer(RE + 300e3, RE + 300e3)


class TestPlaneChange:
    def test_geo_28p5_deg(self):
        v_geo = math.sqrt(MU_EARTH / (RE + 35_786e3))
        res = plane_change_delta_v(v_geo, 28.5)
        assert res["delta_v_ms"] == pytest.approx(1513.7, rel=1e-3)

    def test_zero_change_is_zero(self):
        assert plane_change_delta_v(7000.0, 0.0)["delta_v_ms"] == 0.0


class TestOrbitalPeriod:
    def test_geo_is_one_sidereal_day(self):
        # GEO semi-major axis ~42,164 km -> ~23.934 h (one sidereal day).
        res = orbital_period(RE + 35_786e3)
        assert res["period_hr"] == pytest.approx(23.934, rel=1e-3)

    def test_leo_300km(self):
        assert orbital_period(RE + 300e3)["period_min"] == pytest.approx(90.52, rel=1e-3)
