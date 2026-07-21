"""End-to-end validation of nozzle_performance against ideal 1-D nozzle theory.

Cross-checks the composite tool (which chains exit-Mach, exit conditions, thrust,
Cf, Isp, c*, and choked mass flow) against an independent implementation of the
ideal 1-D relations (Sutton & Biblarz Ch. 3; Anderson Ch. 4), then asserts the
internal-consistency and monotonicity invariants that must always hold.
"""

import math

import pytest

from rocket_tools.aerodynamics import nozzle_performance

# Reference case: LOX/RP-1-like, Ae/At = 8.
PC, TC, PA, AT, AE, GAMMA, MW = 7.0e6, 3500.0, 101325.0, 0.01, 0.08, 1.22, 23.3
R_SPECIFIC = 8314.0 / MW  # matches nozzle.py's universal-gas constant


def _independent_exit_mach(area_ratio: float, gamma: float) -> float:
    def ar(m: float) -> float:
        return (1.0 / m) * ((2.0 / (gamma + 1.0)) * (1.0 + (gamma - 1.0) / 2.0 * m**2)) ** (
            (gamma + 1.0) / (2.0 * (gamma - 1.0))
        )

    lo, hi = 1.0001, 50.0
    for _ in range(200):
        m = (lo + hi) / 2.0
        if ar(m) < area_ratio:
            lo = m
        else:
            hi = m
    return (lo + hi) / 2.0


class TestNozzleAgainstTheory:
    def setup_method(self):
        self.out = nozzle_performance(PC, TC, PA, AT, AE, GAMMA, MW)

    def test_exit_mach_matches_area_mach_relation(self):
        me = _independent_exit_mach(AE / AT, GAMMA)
        assert self.out["exit_mach"] == pytest.approx(me, rel=1e-3)
        assert me == pytest.approx(3.1725, rel=1e-3)  # tabulated value

    def test_exit_pressure_and_temperature(self):
        me = self.out["exit_mach"]
        pe = PC * (1.0 + (GAMMA - 1.0) / 2.0 * me**2) ** (-GAMMA / (GAMMA - 1.0))
        te = TC / (1.0 + (GAMMA - 1.0) / 2.0 * me**2)
        assert self.out["exit_pressure_pa"] == pytest.approx(pe, rel=1e-3)
        assert self.out["exit_temperature_k"] == pytest.approx(te, rel=1e-3)

    def test_exit_velocity(self):
        te = self.out["exit_temperature_k"]
        ve = self.out["exit_mach"] * math.sqrt(GAMMA * R_SPECIFIC * te)
        assert self.out["exit_velocity_ms"] == pytest.approx(ve, rel=1e-3)


class TestNozzleInternalConsistency:
    def setup_method(self):
        self.out = nozzle_performance(PC, TC, PA, AT, AE, GAMMA, MW)

    def test_thrust_equals_momentum_plus_pressure(self):
        o = self.out
        expected = o["mass_flow_rate_kg_s"] * o["exit_velocity_ms"] + (
            o["exit_pressure_pa"] - PA
        ) * AE
        assert o["thrust_n"] == pytest.approx(expected, rel=1e-4)

    def test_cf_isp_cstar_relations(self):
        o = self.out
        assert o["thrust_coefficient_cf"] == pytest.approx(o["thrust_n"] / (PC * AT), rel=1e-4)
        assert o["specific_impulse_s"] == pytest.approx(
            o["thrust_n"] / (o["mass_flow_rate_kg_s"] * 9.80665), rel=1e-4
        )
        assert o["characteristic_velocity_ms"] == pytest.approx(
            PC * AT / o["mass_flow_rate_kg_s"], rel=1e-4
        )
        # Identity: Isp * g0 = Cf * c* (from F = Cf*pc*At = Isp*g0*mdot, c* = pc*At/mdot).
        assert o["specific_impulse_s"] * 9.80665 == pytest.approx(
            o["thrust_coefficient_cf"] * o["characteristic_velocity_ms"], rel=1e-4
        )


class TestNozzleMonotonicityAndState:
    def test_larger_expansion_raises_mach_lowers_pressure(self):
        small = nozzle_performance(PC, TC, PA, AT, 0.08, GAMMA, MW)
        large = nozzle_performance(PC, TC, PA, AT, 0.16, GAMMA, MW)
        assert large["exit_mach"] > small["exit_mach"]
        assert large["exit_pressure_pa"] < small["exit_pressure_pa"]

    def test_expansion_state_labels(self):
        # Small nozzle: pe (112 kPa) > pa (101 kPa) -> underexpanded.
        assert nozzle_performance(PC, TC, PA, AT, 0.08, GAMMA, MW)["expansion_state"] == (
            "underexpanded"
        )
        # Large nozzle: pe (~45 kPa) < pa -> overexpanded.
        assert nozzle_performance(PC, TC, PA, AT, 0.16, GAMMA, MW)["expansion_state"] == (
            "overexpanded"
        )
