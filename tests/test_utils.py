"""Tests for utility functions."""

import pytest

from rocket_tools.utils import ValidationError, unit_convert, validate_positive


class TestUnitConvert:
    def test_identity_conversion(self):
        result = unit_convert(10.0, "m", "m")
        assert result["converted_value"] == 10.0
        assert result["conversion_factor"] == 1.0

    def test_m_to_mm(self):
        result = unit_convert(1.0, "m", "mm")
        assert result["converted_value"] == 1000.0

    def test_inch_to_m(self):
        result = unit_convert(1.0, "inch", "m")
        assert pytest.approx(result["converted_value"], 1e-6) == 0.0254

    def test_psi_to_pa(self):
        result = unit_convert(1.0, "psi", "pa")
        assert pytest.approx(result["converted_value"], 1e-1) == 6894.757293168361

    def test_unsupported_conversion(self):
        with pytest.raises(ValueError, match="Unsupported conversion"):
            unit_convert(1.0, "m", "kg")

    def test_temperature_c_to_k(self):
        result = unit_convert(0.0, "c", "k")
        assert result["converted_value"] == 273.15


class TestValidation:
    def test_validate_positive_pass(self):
        validate_positive(1.0, "test_param")

    def test_validate_positive_fail(self):
        with pytest.raises(ValidationError, match="must be greater than 0"):
            validate_positive(-1.0, "test_param")

    def test_validation_error_dict(self):
        err = ValidationError(
            "msg",
            error_code="VALIDATION_ERROR",
            parameter="p",
            constraint="c",
            suggestion="s",
        )
        d = err.to_dict()
        assert d["error_code"] == "VALIDATION_ERROR"
        assert d["error_type"] == "validation_error"
        assert d["parameter"] == "p"
