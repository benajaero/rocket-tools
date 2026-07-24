"""Tests for the visualization tools (dual-return contract + graceful degradation)."""

import base64

import pytest

from rocket_tools.viz import (
    plot_beam_diagrams,
    plot_drag_polar,
    plot_isa_profile,
    plot_nozzle_contour,
    plot_trajectory,
)

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def _assert_valid_png_dict(result: dict):
    assert result["mime_type"] == "image/png"
    assert result["format"] == "png"
    raw = base64.b64decode(result["image_base64"])
    assert raw[:8] == PNG_MAGIC
    assert isinstance(result["series"], dict)
    assert isinstance(result["meta"], dict)


class TestDataContract:
    def test_beam_diagrams_data(self):
        r = plot_beam_diagrams(
            load=1000.0,
            length=2.0,
            youngs_modulus=200e9,
            cross_section={"type": "rectangle", "width": 0.05, "height": 0.01},
        )
        _assert_valid_png_dict(r)
        s = r["series"]
        n = len(s["x_m"])
        assert n > 1 and all(len(v) == n for v in s.values())
        assert s["x_m"][0] == 0.0

    def test_drag_polar_data(self):
        r = plot_drag_polar(cd0=0.02, aspect_ratio=8.0)
        _assert_valid_png_dict(r)
        assert r["meta"]["ld_max"] > 0

    def test_nozzle_contour_data(self):
        r = plot_nozzle_contour(throat_radius_m=0.1, area_ratio=16.0)
        _assert_valid_png_dict(r)
        assert r["meta"]["exit_radius_m"] == pytest.approx(0.4, rel=1e-6)

    def test_isa_profile_data(self):
        r = plot_isa_profile(max_altitude_m=80000.0)
        _assert_valid_png_dict(r)
        assert r["series"]["temperature_k"][0] == pytest.approx(288.15, rel=1e-3)

    def test_trajectory_data(self):
        r = plot_trajectory(
            initial_mass_kg=1000.0,
            dry_mass_kg=400.0,
            specific_impulse_s=250.0,
            mass_flow_rate_kg_s=20.0,
            reference_area_m2=0.2,
            dt=0.2,
        )
        _assert_valid_png_dict(r)
        assert r["meta"]["apogee_m"] > 0


class TestImageContract:
    def test_render_image_returns_image_content(self):
        result = plot_isa_profile(max_altitude_m=50000.0, render="image")
        # FastMCP ImageContent, not a dict
        assert not isinstance(result, dict)
        assert getattr(result, "type", None) == "image"
        assert getattr(result, "mimeType", None) == "image/png"


class TestOutputPath:
    def test_writes_png_to_path(self, tmp_path):
        out = tmp_path / "beam.png"
        r = plot_beam_diagrams(
            load=500.0,
            length=1.0,
            youngs_modulus=70e9,
            cross_section={"type": "circle", "diameter": 0.02},
            output_path=str(out),
        )
        assert out.exists()
        assert out.read_bytes()[:8] == PNG_MAGIC
        assert r["output_path"] == str(out)


class TestGracefulDegradation:
    def test_missing_matplotlib_raises_structured_error(self, monkeypatch):
        import builtins

        from rocket_tools.utils.validation import ToolError

        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name == "matplotlib" or name.startswith("matplotlib."):
                raise ImportError("No module named 'matplotlib'")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", fake_import)
        from rocket_tools.viz.backend import require_matplotlib

        with pytest.raises(ToolError) as exc:
            require_matplotlib()
        assert exc.value.error_code == "MISSING_DEPENDENCY"
