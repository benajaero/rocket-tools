"""Table-driven validation against NACA Report 1135.

"Equations, Tables, and Charts for Compressible Flow" (Ames Research Staff,
NACA TR 1135, 1953) is the canonical reference for perfect-gas (gamma=1.4)
isentropic, normal-shock, and Prandtl-Meyer relations. These tests pin the
tools to its published table values at multiple Mach numbers with tight
tolerances, and check the physical invariants that must hold across a sweep.
"""

import math

import pytest

from rocket_tools.aerodynamics import (
    isentropic_flow,
    normal_shock,
    oblique_shock,
    prandtl_meyer,
)
from rocket_tools.utils.validation import ToolError

# --- NACA 1135 tables, gamma = 1.4 ---------------------------------------------

# Mach -> (T/T0, p/p0, rho/rho0, A/A*)
ISENTROPIC = {
    1.5: (0.6897, 0.2724, 0.3950, 1.1762),
    2.0: (0.5556, 0.1278, 0.2301, 1.6875),
    3.0: (0.3571, 0.02722, 0.07623, 4.2346),
    4.0: (0.2381, 0.006586, 0.02766, 10.719),
    5.0: (0.1667, 0.001890, 0.01134, 25.000),
}

# M1 -> (M2, p2/p1, rho2/rho1, T2/T1, p02/p01)
NORMAL_SHOCK = {
    1.5: (0.7011, 2.4583, 1.8621, 1.3202, 0.9298),
    2.0: (0.5774, 4.5000, 2.6667, 1.6875, 0.7209),
    3.0: (0.4752, 10.333, 3.8571, 2.6790, 0.32834),
    4.0: (0.4350, 18.500, 4.5714, 4.0469, 0.13876),
    5.0: (0.41523, 29.000, 5.0000, 5.8000, 0.06172),
}

# Mach -> Prandtl-Meyer angle nu (degrees)
PRANDTL_MEYER = {1.5: 11.905, 2.0: 26.380, 3.0: 49.757, 4.0: 65.785, 5.0: 76.920}

# Weak-solution oblique shock (Anderson, Fundamentals of Aerodynamics, Ch. 9;
# theta-beta-M chart): (M1, theta_deg) -> (beta_weak_deg, M2, p2/p1).
OBLIQUE_WEAK = {
    (2.0, 15.0): (45.34, 1.4457, 2.1947),
    (2.0, 10.0): (39.31, 1.6405, 1.7066),
    (3.0, 20.0): (37.76, 1.9941, 3.7713),
    (5.0, 30.0): (42.34, 2.1357, 13.0666),
}

# Maximum deflection for an attached shock (Anderson Fig. 9.9): M1 -> theta_max_deg.
THETA_MAX = {2.0: 22.97, 3.0: 34.07, 5.0: 41.12}


@pytest.mark.parametrize("mach", sorted(ISENTROPIC))
def test_isentropic_matches_naca1135(mach: float) -> None:
    t, p, rho, area = ISENTROPIC[mach]
    out = isentropic_flow(mach=mach, gamma=1.4)
    assert out["temperature_ratio"] == pytest.approx(t, rel=2e-3)
    assert out["pressure_ratio"] == pytest.approx(p, rel=2e-3)
    assert out["density_ratio"] == pytest.approx(rho, rel=2e-3)
    assert out["area_ratio"] == pytest.approx(area, rel=2e-3)
    # Mach angle mu = asin(1/M).
    assert out["mach_angle_deg"] == pytest.approx(math.degrees(math.asin(1.0 / mach)), abs=0.02)


@pytest.mark.parametrize("mach1", sorted(NORMAL_SHOCK))
def test_normal_shock_matches_naca1135(mach1: float) -> None:
    m2, p, rho, t, p0 = NORMAL_SHOCK[mach1]
    out = normal_shock(mach1=mach1, gamma=1.4)
    assert out["mach_downstream"] == pytest.approx(m2, rel=2e-3)
    assert out["pressure_ratio"] == pytest.approx(p, rel=2e-3)
    assert out["density_ratio"] == pytest.approx(rho, rel=2e-3)
    assert out["temperature_ratio"] == pytest.approx(t, rel=2e-3)
    assert out["stagnation_pressure_ratio"] == pytest.approx(p0, rel=2e-3)


@pytest.mark.parametrize("mach", sorted(PRANDTL_MEYER))
def test_prandtl_meyer_matches_naca1135(mach: float) -> None:
    out = prandtl_meyer(mach=mach, gamma=1.4)
    assert out["prandtl_meyer_angle_deg"] == pytest.approx(PRANDTL_MEYER[mach], abs=0.02)


@pytest.mark.parametrize(("mach1", "theta"), sorted(OBLIQUE_WEAK))
def test_oblique_shock_weak_solution(mach1: float, theta: float) -> None:
    beta, m2, p = OBLIQUE_WEAK[(mach1, theta)]
    out = oblique_shock(mach1=mach1, deflection_deg=theta, gamma=1.4)
    assert out["solution"] == "weak"
    assert out["wave_angle_deg"] == pytest.approx(beta, abs=0.05)  # NOT the strong root
    assert out["mach_downstream"] == pytest.approx(m2, rel=2e-3)
    assert out["pressure_ratio"] == pytest.approx(p, rel=2e-3)


@pytest.mark.parametrize("mach1", sorted(THETA_MAX))
def test_oblique_shock_theta_max(mach1: float) -> None:
    out = oblique_shock(mach1=mach1, deflection_deg=1.0, gamma=1.4)
    assert out["max_deflection_deg"] == pytest.approx(THETA_MAX[mach1], abs=0.05)


def test_oblique_shock_detaches_above_theta_max() -> None:
    # M1=2 detaches beyond ~22.97 deg; 25 deg must be a structured INVALID_PARAMETER.
    with pytest.raises(ToolError) as exc:
        oblique_shock(mach1=2.0, deflection_deg=25.0, gamma=1.4)
    assert exc.value.error_code == "INVALID_PARAMETER"
    assert exc.value.parameter == "deflection_deg"


class TestCompressibleInvariants:
    """Physical invariants that must hold across a Mach sweep (gamma=1.4)."""

    SWEEP = [1.2, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 8.0]

    def test_isentropic_ratios_bounded_and_monotonic(self) -> None:
        prev_p = 1.0
        prev_area = 0.0
        for m in self.SWEEP:
            o = isentropic_flow(mach=m, gamma=1.4)
            for key in ("temperature_ratio", "pressure_ratio", "density_ratio"):
                assert 0.0 < o[key] < 1.0  # static/total ratios are in (0, 1)
            assert o["pressure_ratio"] < prev_p  # decreases with Mach
            assert o["area_ratio"] > max(prev_area, 1.0)  # A/A* >= 1 and increasing
            prev_p, prev_area = o["pressure_ratio"], o["area_ratio"]

    def test_normal_shock_entropy_and_jumps(self) -> None:
        prev_p0 = 1.0
        for m in self.SWEEP:
            o = normal_shock(mach1=m, gamma=1.4)
            assert o["mach_downstream"] < 1.0 < m  # subsonic behind the shock
            assert o["pressure_ratio"] > 1.0  # compression
            assert o["density_ratio"] > 1.0
            assert o["temperature_ratio"] > 1.0
            assert 0.0 < o["stagnation_pressure_ratio"] <= 1.0  # total pressure loss (entropy)
            assert o["stagnation_pressure_ratio"] < prev_p0  # loss grows with Mach
            prev_p0 = o["stagnation_pressure_ratio"]

    def test_prandtl_meyer_monotonic(self) -> None:
        prev = 0.0
        for m in self.SWEEP:
            nu = prandtl_meyer(mach=m, gamma=1.4)["prandtl_meyer_angle_deg"]
            assert nu > prev  # turning angle increases with Mach
            prev = nu
