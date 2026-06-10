"""Comprehensive tests for imperial and aerospace unit conversions."""

import pytest

from rocket_tools.utils.units import (
    _normalize_unit,
    convert_to_si,
    ft_to_m,
    knots_to_mps,
    lbf_to_n,
    mph_to_mps,
    mps_to_knots,
    mps_to_mph,
    n_to_lbf,
    pa_to_psi,
    psi_to_pa,
    unit_convert,
)


class TestNormalizeUnit:
    def test_length_aliases(self):
        assert _normalize_unit("feet") == "ft"
        assert _normalize_unit("foot") == "ft"
        assert _normalize_unit("inches") == "inch"
        assert _normalize_unit("miles") == "mi"
        assert _normalize_unit("nautical miles") == "nm"

    def test_pressure_aliases(self):
        assert _normalize_unit("PSI") == "psi"
        assert _normalize_unit("pounds per square inch") == "psi"
        assert _normalize_unit("atmospheres") == "atm"
        assert _normalize_unit("bar") == "bar"

    def test_force_aliases(self):
        assert _normalize_unit("pounds force") == "lbf"
        assert _normalize_unit("kips") == "kip"

    def test_speed_aliases(self):
        assert _normalize_unit("mph") == "mph"
        assert _normalize_unit("knots") == "knot"
        assert _normalize_unit("feet per second") == "fps"

    def test_temperature_aliases(self):
        assert _normalize_unit("Fahrenheit") == "f"
        assert _normalize_unit("Rankine") == "r"
        assert _normalize_unit("Celsius") == "c"


class TestLengthConversions:
    def test_ft_to_m(self):
        assert ft_to_m(1) == pytest.approx(0.3048)
        assert ft_to_m(10) == pytest.approx(3.048)

    def test_inch_to_m(self):
        result = unit_convert(12, "inch", "m")
        assert result["converted_value"] == pytest.approx(0.3048)

    def test_yd_to_m(self):
        result = unit_convert(1, "yd", "m")
        assert result["converted_value"] == pytest.approx(0.9144)

    def test_mi_to_m(self):
        result = unit_convert(1, "mi", "m")
        assert result["converted_value"] == pytest.approx(1609.344)

    def test_nm_to_m(self):
        result = unit_convert(1, "nm", "m")
        assert result["converted_value"] == pytest.approx(1852)

    def test_ft_to_inch(self):
        result = unit_convert(1, "ft", "inch")
        assert result["converted_value"] == pytest.approx(12)


class TestPressureConversions:
    def test_psi_to_pa(self):
        assert psi_to_pa(1) == pytest.approx(6894.757, rel=1e-5)

    def test_pa_to_psi(self):
        assert pa_to_psi(6894.757) == pytest.approx(1.0, rel=1e-4)

    def test_atm_to_pa(self):
        result = unit_convert(1, "atm", "pa")
        assert result["converted_value"] == pytest.approx(101325)

    def test_bar_to_pa(self):
        result = unit_convert(1, "bar", "pa")
        assert result["converted_value"] == pytest.approx(100000)

    def test_ksi_to_pa(self):
        result = unit_convert(1, "ksi", "pa")
        assert result["converted_value"] == pytest.approx(6_894_757, rel=1e-5)

    def test_torr_to_pa(self):
        result = unit_convert(760, "torr", "pa")
        assert result["converted_value"] == pytest.approx(101325, rel=1e-4)

    def test_psf_to_pa(self):
        result = unit_convert(1, "psf", "pa")
        # 1 psi = 144 psf, so 1 psf = 6894.757/144 Pa
        assert result["converted_value"] == pytest.approx(47.880, rel=1e-4)


class TestForceConversions:
    def test_lbf_to_n(self):
        assert lbf_to_n(1) == pytest.approx(4.44822, rel=1e-5)

    def test_n_to_lbf(self):
        assert n_to_lbf(4.44822) == pytest.approx(1.0, rel=1e-4)

    def test_kip_to_n(self):
        result = unit_convert(1, "kip", "n")
        assert result["converted_value"] == pytest.approx(4448.22, rel=1e-5)

    def test_tonf_to_n(self):
        result = unit_convert(1, "tonf", "n")
        assert result["converted_value"] == pytest.approx(8896.44, rel=1e-5)

    def test_lbf_to_kip(self):
        result = unit_convert(1000, "lbf", "kip")
        assert result["converted_value"] == pytest.approx(1.0)


class TestSpeedConversions:
    def test_mph_to_mps(self):
        assert mph_to_mps(60) == pytest.approx(26.8224, rel=1e-5)

    def test_mps_to_mph(self):
        assert mps_to_mph(26.8224) == pytest.approx(60.0, rel=1e-4)

    def test_knots_to_mps(self):
        assert knots_to_mps(100) == pytest.approx(51.4444, rel=1e-5)

    def test_mps_to_knots(self):
        assert mps_to_knots(51.4444) == pytest.approx(100.0, rel=1e-4)

    def test_fps_to_mps(self):
        result = unit_convert(1, "fps", "m/s")
        assert result["converted_value"] == pytest.approx(0.3048)

    def test_kmh_to_mps(self):
        result = unit_convert(3.6, "km/h", "m/s")
        assert result["converted_value"] == pytest.approx(1.0)


class TestTemperatureConversions:
    def test_c_to_k(self):
        result = unit_convert(0, "c", "k")
        assert result["converted_value"] == pytest.approx(273.15)

    def test_k_to_c(self):
        result = unit_convert(273.15, "k", "c")
        assert result["converted_value"] == pytest.approx(0.0)

    def test_f_to_c(self):
        result = unit_convert(32, "f", "c")
        assert result["converted_value"] == pytest.approx(0.0)

    def test_c_to_f(self):
        result = unit_convert(100, "c", "f")
        assert result["converted_value"] == pytest.approx(212.0)

    def test_f_to_k(self):
        result = unit_convert(32, "f", "k")
        assert result["converted_value"] == pytest.approx(273.15)

    def test_r_to_k(self):
        result = unit_convert(491.67, "r", "k")
        assert result["converted_value"] == pytest.approx(273.15, rel=1e-4)

    def test_k_to_r(self):
        result = unit_convert(273.15, "k", "r")
        assert result["converted_value"] == pytest.approx(491.67, rel=1e-4)

    def test_f_to_r(self):
        result = unit_convert(32, "f", "r")
        assert result["converted_value"] == pytest.approx(491.67, rel=1e-4)


class TestAreaConversions:
    def test_sqft_to_sqm(self):
        result = unit_convert(1, "sqft", "m2")
        assert result["converted_value"] == pytest.approx(0.092903, rel=1e-5)

    def test_sqin_to_sqft(self):
        result = unit_convert(144, "sqin", "sqft")
        assert result["converted_value"] == pytest.approx(1.0)


class TestDensityConversions:
    def test_slug_per_ft3_to_kg_m3(self):
        result = unit_convert(1, "slug/ft3", "kg/m3")
        assert result["converted_value"] == pytest.approx(515.379, rel=1e-4)

    def test_lb_per_ft3_to_kg_m3(self):
        result = unit_convert(1, "lb/ft3", "kg/m3")
        assert result["converted_value"] == pytest.approx(16.018, rel=1e-4)


class TestEnergyConversions:
    def test_ftlbf_to_j(self):
        result = unit_convert(1, "ftlbf", "j")
        assert result["converted_value"] == pytest.approx(1.3558, rel=1e-4)

    def test_btu_to_j(self):
        result = unit_convert(1, "btu", "j")
        assert result["converted_value"] == pytest.approx(1055.06, rel=1e-4)


class TestConvertToSi:
    def test_ft_to_si(self):
        val, unit = convert_to_si(10, "ft")
        assert val == pytest.approx(3.048)
        assert unit == "m"

    def test_lbf_to_si(self):
        val, unit = convert_to_si(1000, "lbf")
        assert val == pytest.approx(4448.22, rel=1e-5)
        assert unit == "n"

    def test_psi_to_si(self):
        val, unit = convert_to_si(14.7, "psi")
        assert val == pytest.approx(101352.9, rel=1e-5)
        assert unit == "pa"

    def test_mph_to_si(self):
        val, unit = convert_to_si(60, "mph")
        assert val == pytest.approx(26.8224, rel=1e-5)
        assert unit == "m/s"

    def test_knots_to_si(self):
        val, unit = convert_to_si(100, "knot")
        assert val == pytest.approx(51.4444, rel=1e-5)
        assert unit == "m/s"

    def test_already_si(self):
        val, unit = convert_to_si(10, "m")
        assert val == 10.0
        assert unit == "m"

    def test_unknown_unit(self):
        with pytest.raises(ValueError, match="Unknown unit"):
            convert_to_si(10, "parsecs")


class TestIdentityConversion:
    def test_same_unit(self):
        result = unit_convert(42, "m", "m")
        assert result["converted_value"] == 42.0
        assert result["conversion_factor"] == 1.0

    def test_same_unit_pressure(self):
        result = unit_convert(100, "psi", "psi")
        assert result["converted_value"] == 100.0
