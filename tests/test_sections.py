"""Tests for section properties."""

import pytest

from rocket_tools.structural.sections import section_properties


class TestSectionProperties:
    def test_rectangle(self):
        result = section_properties("rectangle", width=0.1, height=0.2)
        assert result["shape"] == "rectangle"
        assert result["area_m2"] == pytest.approx(0.02, rel=1e-6)
        assert result["i_xx_m4"] == pytest.approx(6.6667e-5, rel=1e-4)
        assert result["s_xx_m3"] == pytest.approx(6.6667e-4, rel=1e-4)

    def test_hollow_rectangle(self):
        result = section_properties("hollow_rectangle", width=0.1, height=0.2, wall_thickness=0.01)
        assert result["shape"] == "hollow_rectangle"
        assert result["area_m2"] > 0
        assert result["i_xx_m4"] > 0

    def test_circle(self):
        result = section_properties("circle", diameter=0.1)
        assert result["shape"] == "circle"
        assert result["area_m2"] == pytest.approx(7.85398e-3, rel=1e-4)
        assert result["i_xx_m4"] == pytest.approx(4.9087e-6, rel=1e-4)

    def test_hollow_circle(self):
        result = section_properties("hollow_circle", outer_diameter=0.1, inner_diameter=0.08)
        assert result["shape"] == "hollow_circle"
        assert result["area_m2"] > 0
        assert result["i_xx_m4"] > 0

    def test_ibeam(self):
        result = section_properties(
            "ibeam", flange_width=0.1, height=0.2, flange_thickness=0.01, web_thickness=0.008
        )
        assert result["shape"] == "ibeam"
        assert result["area_m2"] > 0
        assert result["i_xx_m4"] > 0

    def test_cchannel(self):
        result = section_properties(
            "cchannel", flange_width=0.05, height=0.1, flange_thickness=0.008, web_thickness=0.006
        )
        assert result["shape"] == "cchannel"
        assert result["area_m2"] > 0

    def test_tsection(self):
        result = section_properties(
            "tsection", flange_width=0.08, height=0.1, flange_thickness=0.01, web_thickness=0.008
        )
        assert result["shape"] == "tsection"
        assert result["area_m2"] > 0

    def test_invalid_shape(self):
        with pytest.raises(ValueError, match="Unknown shape"):
            section_properties("invalid", width=0.1)

    def test_negative_dimension(self):
        with pytest.raises(ValueError):
            section_properties("rectangle", width=-0.1, height=0.2)

    def test_all_shapes_have_positive_properties(self):
        shapes = [
            ("rectangle", {"width": 0.1, "height": 0.2}),
            ("hollow_rectangle", {"width": 0.1, "height": 0.2, "wall_thickness": 0.01}),
            ("circle", {"diameter": 0.1}),
            ("hollow_circle", {"outer_diameter": 0.1, "inner_diameter": 0.08}),
            (
                "ibeam",
                {
                    "flange_width": 0.1,
                    "height": 0.2,
                    "flange_thickness": 0.01,
                    "web_thickness": 0.008,
                },
            ),
            (
                "cchannel",
                {
                    "flange_width": 0.05,
                    "height": 0.1,
                    "flange_thickness": 0.008,
                    "web_thickness": 0.006,
                },
            ),
            (
                "tsection",
                {
                    "flange_width": 0.08,
                    "height": 0.1,
                    "flange_thickness": 0.01,
                    "web_thickness": 0.008,
                },
            ),
        ]
        for shape, kwargs in shapes:
            result = section_properties(shape, **kwargs)
            assert result["area_m2"] > 0, shape
            assert result["i_xx_m4"] > 0, shape
            assert result["s_xx_m3"] > 0, shape
            assert result["r_xx_m"] > 0, shape
