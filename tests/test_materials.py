"""Tests for materials and ISA."""

import pytest

from rocket_tools.materials import isa_atmosphere, material_lookup


class TestMaterialLookup:
    def test_6061_t6(self):
        result = material_lookup("6061-T6")
        assert result["material_name"] == "6061-T6"
        assert pytest.approx(result["youngs_modulus_pa"], 1e9) == 68.9e9
        assert pytest.approx(result["density_kg_m3"], 1.0) == 2700.0

    def test_case_insensitive(self):
        result = material_lookup("ti-6al-4v")
        assert result["material_name"] == "Ti-6Al-4V"

    def test_property_filter(self):
        result = material_lookup("7075-T6", property_filter="density")
        assert result["density"] == 2810.0

    def test_unknown_material(self):
        with pytest.raises(ValueError, match="not found"):
            material_lookup("FakeMaterial")


class TestISA:
    def test_sea_level(self):
        result = isa_atmosphere(0.0)
        assert pytest.approx(result["temperature_k"], 0.1) == 288.15
        assert pytest.approx(result["pressure_pa"], 1.0) == 101325.0
        assert pytest.approx(result["density_kg_m3"], 0.001) == 1.225

    def test_troposphere(self):
        result = isa_atmosphere(5000.0)
        assert result["temperature_k"] < 288.15
        assert result["pressure_pa"] < 101325.0
        assert result["density_kg_m3"] < 1.225

    def test_tropopause(self):
        result = isa_atmosphere(15000.0)
        assert pytest.approx(result["temperature_k"], 0.5) == 216.65

    def test_interpolation(self):
        result = isa_atmosphere(1234.5)
        assert result["altitude_m"] == 1234.5

    def test_out_of_range(self):
        with pytest.raises(ValueError):
            isa_atmosphere(-1.0)
        with pytest.raises(ValueError):
            isa_atmosphere(30000.0)
