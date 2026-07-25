"""Tests for the bi-elliptic transfer (Batch 8)."""

import math

import pytest

from rocket_tools.design import bi_elliptic_transfer, hohmann_transfer, vis_viva_velocity

MU_EARTH = 3.986004418e14


class TestBiEllipticTransfer:
    def test_hand_computed_case(self):
        # r1=7000, r2=105000, rb=210000 km: a known case where bi-elliptic beats Hohmann.
        r = bi_elliptic_transfer(7.0e6, 105.0e6, 210.0e6)
        assert r["total_delta_v_kms"] == pytest.approx(4.0285, abs=1e-3)
        assert r["delta_v1_ms"] == pytest.approx(2952.1, abs=1.0)
        assert r["delta_v2_ms"] == pytest.approx(775.0, abs=1.0)
        assert r["delta_v3_ms"] == pytest.approx(301.4, abs=1.0)
        assert r["cheaper_than_hohmann"] is True
        assert r["delta_v_saving_vs_hohmann_ms"] > 0

    def test_first_burn_matches_vis_viva(self):
        # delta_v1 = periapsis speed of ellipse-1 minus the initial circular speed.
        r1, r2, rb = 7.0e6, 105.0e6, 210.0e6
        be = bi_elliptic_transfer(r1, r2, rb)
        a1 = 0.5 * (r1 + rb)
        v_p1 = vis_viva_velocity(r1, a1)["velocity_ms"]
        v_c1 = math.sqrt(MU_EARTH / r1)
        assert be["delta_v1_ms"] == pytest.approx(v_p1 - v_c1, abs=1.0)

    def test_low_ratio_hohmann_wins(self):
        # For a small radius ratio, Hohmann is cheaper.
        be = bi_elliptic_transfer(7.0e6, 14.0e6, 20.0e6)
        assert be["cheaper_than_hohmann"] is False
        assert be["total_delta_v_ms"] > be["hohmann_total_delta_v_ms"]

    def test_longer_than_hohmann(self):
        r1, r2, rb = 7.0e6, 105.0e6, 210.0e6
        be = bi_elliptic_transfer(r1, r2, rb)
        hoh = hohmann_transfer(r1, r2)
        assert be["transfer_time_s"] > hoh["transfer_time_s"]

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"radius1_m": 0.0},
            {"radius2_m": -1.0},
            {"radius1_m": 7.0e6, "radius2_m": 7.0e6},  # equal orbits
            {"intermediate_radius_m": 50.0e6},  # rb below r2 (105e6)
        ],
    )
    def test_invalid_inputs_rejected(self, kwargs):
        args = {"radius1_m": 7.0e6, "radius2_m": 105.0e6, "intermediate_radius_m": 210.0e6}
        args.update(kwargs)
        with pytest.raises(ValueError):
            bi_elliptic_transfer(**args)
