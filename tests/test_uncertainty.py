"""Tests for uncertainty propagation."""

import numpy as np
import pytest

from rocket_tools.uncertainty import Normal, Uniform, run_with_uncertainty


class TestDistributions:
    def test_uniform(self):
        d = Uniform(0, 10)
        samples = d.sample(1000, seed=42)
        assert len(samples) == 1000
        assert np.min(samples) >= 0
        assert np.max(samples) <= 10

    def test_normal(self):
        d = Normal(5, 1)
        samples = d.sample(10000, seed=42)
        assert pytest.approx(np.mean(samples), 0.1) == 5.0
        assert pytest.approx(np.std(samples), 0.1) == 1.0

    def test_serialization(self):
        d = Uniform(1, 2)
        assert d.to_dict() == {"distribution": "uniform", "low": 1, "high": 2}
        d2 = Uniform.from_dict(d.to_dict())
        assert d2.low == 1


class TestUncertaintyEngine:
    def test_beam_uncertainty(self):
        result = run_with_uncertainty(
            tool_name="beam_analysis",
            params={
                "load": {"distribution": "uniform", "low": 450, "high": 550},
                "length": 2.0,
                "youngs_modulus": 68.9e9,
                "cross_section": {"type": "rectangle", "width": 0.05, "height": 0.01},
            },
            samples=100,
            seed=42,
        )
        assert result["samples"] == 100
        assert "bending_stress_pa" in result["results"]
        stress = result["results"]["bending_stress_pa"]
        assert stress["mean"] > 0
        assert stress["ci_95"][0] < stress["ci_95"][1]

    def test_no_uncertainty(self):
        result = run_with_uncertainty(
            tool_name="beam_analysis",
            params={
                "load": 500.0,
                "length": 2.0,
                "youngs_modulus": 68.9e9,
                "cross_section": {"type": "rectangle", "width": 0.05, "height": 0.01},
            },
            samples=10,
            seed=42,
        )
        assert result["samples"] == 10
        stress = result["results"]["bending_stress_pa"]
        assert stress["std"] == pytest.approx(0, abs=1e-6)
