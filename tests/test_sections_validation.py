"""Validation of section_properties for all 7 shapes against closed-form formulas.

Cross-checks area, second moment of area (I), and section modulus (S) against
independent implementations of the Roark Table A.1 formulas, including the
composite shapes (I-beam, C-channel, T-section) that use the parallel-axis
theorem. Also checks the shape-parameter error contract.
"""

import asyncio
import json
import math

import pytest

from rocket_tools.structural import section_properties

PI = math.pi


def _rect(b, h):
    return {"area_m2": b * h, "i_xx_m4": b * h**3 / 12, "s_xx_m3": b * h**2 / 6}


def _circle(d):
    return {"area_m2": PI * d**2 / 4, "i_xx_m4": PI * d**4 / 64, "s_xx_m3": PI * d**3 / 32}


def _ibeam(bf, h, tf, tw):
    hw = h - 2 * tf
    a = 2 * bf * tf + hw * tw
    i = tw * hw**3 / 12 + 2 * (bf * tf**3 / 12 + bf * tf * ((hw + tf) / 2) ** 2)
    return {"area_m2": a, "i_xx_m4": i, "s_xx_m3": i / (h / 2)}


def _tsection(bf, h, tf, tw):
    hw = h - tf
    a = bf * tf + hw * tw
    yc = (bf * tf * (h - tf / 2) + hw * tw * (hw / 2)) / a
    i_flange = bf * tf**3 / 12 + bf * tf * (h - tf / 2 - yc) ** 2
    i_web = tw * hw**3 / 12 + hw * tw * (yc - hw / 2) ** 2
    i = i_flange + i_web
    return {"area_m2": a, "i_xx_m4": i, "s_xx_m3": i / max(yc, h - yc)}


CASES = [
    (dict(shape="rectangle", width=0.1, height=0.2), _rect(0.1, 0.2)),
    (dict(shape="circle", diameter=0.05), _circle(0.05)),
    (
        dict(shape="hollow_rectangle", width=0.1, height=0.2, wall_thickness=0.01),
        {"area_m2": 0.1 * 0.2 - 0.08 * 0.18, "i_xx_m4": (0.1 * 0.2**3 - 0.08 * 0.18**3) / 12},
    ),
    (
        dict(shape="hollow_circle", outer_diameter=0.05, inner_diameter=0.04),
        {"area_m2": PI * (0.05**2 - 0.04**2) / 4, "i_xx_m4": PI * (0.05**4 - 0.04**4) / 64},
    ),
    (
        dict(
            shape="ibeam", flange_width=0.1, height=0.2, flange_thickness=0.01, web_thickness=0.008
        ),
        _ibeam(0.1, 0.2, 0.01, 0.008),
    ),
    (
        dict(
            shape="tsection",
            flange_width=0.1,
            height=0.15,
            flange_thickness=0.02,
            web_thickness=0.01,
        ),
        _tsection(0.1, 0.15, 0.02, 0.01),
    ),
]


@pytest.mark.parametrize(("kw", "expected"), CASES)
def test_section_matches_formula(kw, expected):
    out = section_properties(**kw)
    for key, value in expected.items():
        assert out[key] == pytest.approx(value, rel=1e-6), f"{kw['shape']}.{key}"


def test_cchannel_ixx_equals_ibeam_formula():
    # A channel is symmetric about the strong (x) bending axis, so I_xx uses the
    # same 2-flange + web expression as an I-beam of the same dimensions.
    out = section_properties(
        shape="cchannel", flange_width=0.05, height=0.1, flange_thickness=0.008, web_thickness=0.006
    )
    assert out["i_xx_m4"] == pytest.approx(_ibeam(0.05, 0.1, 0.008, 0.006)["i_xx_m4"], rel=1e-9)


class TestShapeParamContract:
    def _call(self, params):
        from rocket_tools.server import mcp

        return json.loads(asyncio.run(mcp.call_tool("section_properties", params))[0].text)

    def test_missing_param_is_invalid_parameter(self):
        # Passing `width` (rectangle param) for an ibeam must name the real requirement.
        data = self._call(
            {
                "shape": "ibeam",
                "width": 0.1,
                "height": 0.2,
                "flange_thickness": 0.01,
                "web_thickness": 0.008,
            }
        )
        assert data["error_code"] == "INVALID_PARAMETER"
        assert data["parameter"] == "flange_width"

    def test_unknown_shape_is_invalid_parameter(self):
        data = self._call({"shape": "triangle", "width": 0.1})
        assert data["error_code"] == "INVALID_PARAMETER"
        assert "triangle" in data["message"]
