"""Tests for rocket nozzle performance."""

import pytest

from rocket_tools.aerodynamics.nozzle import nozzle_performance, optimal_area_ratio


class TestNozzlePerformance:
    def test_basic(self):
        result = nozzle_performance(
            chamber_pressure_pa=5e6,
            chamber_temperature_k=3000.0,
            ambient_pressure_pa=1e5,
            throat_area_m2=0.01,
            exit_area_m2=0.05,
            gamma=1.2,
            molecular_weight=20.0,
        )
        assert result["thrust_n"] > 0
        assert result["specific_impulse_s"] > 0
        assert result["thrust_coefficient_cf"] > 0
        assert result["exit_mach"] > 1.0
        assert result["mass_flow_rate_kg_s"] > 0

    def test_underexpanded(self):
        result = nozzle_performance(
            chamber_pressure_pa=10e6,
            chamber_temperature_k=3000.0,
            ambient_pressure_pa=1e5,
            throat_area_m2=0.01,
            exit_area_m2=0.1,
            gamma=1.2,
            molecular_weight=20.0,
        )
        assert result["expansion_state"] == "underexpanded"

    def test_overexpanded(self):
        result = nozzle_performance(
            chamber_pressure_pa=2e6,
            chamber_temperature_k=3000.0,
            ambient_pressure_pa=1e5,
            throat_area_m2=0.01,
            exit_area_m2=0.2,
            gamma=1.2,
            molecular_weight=20.0,
        )
        assert result["expansion_state"] == "overexpanded"

    def test_invalid(self):
        with pytest.raises(ValueError):
            nozzle_performance(
                chamber_pressure_pa=-1,
                chamber_temperature_k=3000.0,
                ambient_pressure_pa=1e5,
                throat_area_m2=0.01,
                exit_area_m2=0.05,
            )


class TestOptimalAreaRatio:
    def test_basic(self):
        result = optimal_area_ratio(
            chamber_pressure_pa=5e6,
            ambient_pressure_pa=1e5,
            gamma=1.2,
        )
        assert result["optimal_exit_mach"] > 1.0
        assert result["optimal_area_ratio"] > 1.0
        assert result["pressure_ratio"] == 50.0
