"""Validation of column_buckling against Euler-Johnson theory.

Cross-checks both regimes against independent formulas (Timoshenko & Gere;
Shigley Eq. 4-45/4-46) and asserts the defining invariants of the Euler-Johnson
transition: the two curves are tangent at the transition slenderness Cc, meeting
at a critical stress of Sy/2.
"""

import math

import pytest

from rocket_tools.structural import column_buckling

_K = {"pinned_pinned": 1.0, "fixed_free": 2.0, "fixed_pinned": 0.699, "fixed_fixed": 0.5}


def _independent(e, i, a, length, sy, end):
    le = _K[end] * length
    r = math.sqrt(i / a)
    slenderness = le / r
    cc = math.sqrt(2.0 * math.pi**2 * e / sy)
    if slenderness < cc:
        sigma = sy - (sy**2 / (4.0 * math.pi**2 * e)) * slenderness**2
        return {"crit": sigma * a, "slenderness": slenderness, "cc": cc, "regime": "inelastic"}
    crit = math.pi**2 * e * i / le**2
    return {"crit": crit, "slenderness": slenderness, "cc": cc, "regime": "elastic"}


class TestBucklingTheory:
    @pytest.mark.parametrize(
        "kw",
        [
            {
                "youngs_modulus": 200e9,
                "area_moment": 1e-8,
                "area": 1e-3,
                "length": 2.0,
                "yield_strength": 250e6,
                "end_condition": "pinned_pinned",
            },
            {
                "youngs_modulus": 69e9,
                "area_moment": 5e-8,
                "area": 2e-3,
                "length": 0.3,
                "yield_strength": 276e6,
                "end_condition": "pinned_pinned",
            },
            {
                "youngs_modulus": 200e9,
                "area_moment": 1e-8,
                "area": 1e-3,
                "length": 2.0,
                "yield_strength": 250e6,
                "end_condition": "fixed_pinned",
            },
        ],
    )
    def test_matches_independent(self, kw):
        ref = _independent(
            kw["youngs_modulus"],
            kw["area_moment"],
            kw["area"],
            kw["length"],
            kw["yield_strength"],
            kw["end_condition"],
        )
        out = column_buckling(**kw)
        assert out["critical_load_n"] == pytest.approx(ref["crit"], rel=1e-4)
        assert out["slenderness_ratio"] == pytest.approx(ref["slenderness"], rel=1e-6)
        assert out["transition_slenderness"] == pytest.approx(ref["cc"], rel=1e-6)
        assert out["regime"] == ref["regime"]


class TestEulerJohnsonTransition:
    def test_curves_tangent_at_transition(self):
        # At slenderness == Cc, Euler and Johnson meet at sigma_cr = Sy/2.
        e, i, a, sy = 200e9, 1e-8, 1e-3, 250e6
        r = math.sqrt(i / a)
        cc = math.sqrt(2.0 * math.pi**2 * e / sy)
        length = cc * r  # K = 1 -> slenderness == Cc
        out = column_buckling(e, i, a, length, sy)
        assert out["slenderness_ratio"] == pytest.approx(out["transition_slenderness"], rel=1e-6)
        assert out["euler_load_n"] == pytest.approx(out["johnson_load_n"], rel=1e-6)
        assert out["critical_stress_pa"] == pytest.approx(sy / 2.0, rel=1e-6)


class TestBucklingMonotonicity:
    def test_longer_column_buckles_at_lower_load(self):
        base = dict(youngs_modulus=200e9, area_moment=1e-8, area=1e-3, yield_strength=250e6)
        short = column_buckling(length=1.5, **base)
        long = column_buckling(length=3.0, **base)
        assert long["critical_load_n"] < short["critical_load_n"]

    def test_stiffer_end_condition_raises_load(self):
        # Fixed-fixed (K=0.5) must carry more than pinned-pinned (K=1) at equal length.
        base = dict(
            youngs_modulus=200e9, area_moment=1e-8, area=1e-3, length=2.0, yield_strength=250e6
        )
        pinned = column_buckling(end_condition="pinned_pinned", **base)
        fixed = column_buckling(end_condition="fixed_fixed", **base)
        assert fixed["critical_load_n"] > pinned["critical_load_n"]
