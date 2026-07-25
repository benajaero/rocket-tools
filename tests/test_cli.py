"""Tests for the command-line interface."""

import json

import pytest

from rocket_tools.cli import main


def _json_output(capsys):
    return json.loads(capsys.readouterr().out)


class TestCli:
    def test_tools(self, capsys):
        main(["tools"])
        data = _json_output(capsys)
        # The listing reflects the live MCP registry, not a hand-maintained list.
        assert data["count"] >= 81
        assert data["count"] == len(data["tools"])
        assert "beam_analysis" in data["tools"]
        assert "list_materials" in data["tools"]

    def test_tools_verbose(self, capsys):
        main(["tools", "--verbose"])
        data = _json_output(capsys)
        assert data["count"] >= 81
        first = data["tools"][0]
        assert set(first) == {"name", "description"}
        assert all(entry["description"] for entry in data["tools"])

    def test_convert_cross_unit(self, capsys):
        # psi -> MPa is a pressure conversion the old direct-pair table lacked.
        main(["convert", "1000", "psi", "MPa"])
        data = _json_output(capsys)
        assert data["converted_value"] == pytest.approx(6.894757, rel=1e-6)

    def test_convert_incompatible_exits_cleanly(self, capsys):
        with pytest.raises(SystemExit) as exc:
            main(["convert", "5", "psi", "m"])
        assert exc.value.code == 2
        assert "Incompatible units" in capsys.readouterr().err

    def test_convert(self, capsys):
        main(["convert", "100", "mm", "m"])
        data = _json_output(capsys)
        assert data["converted_value"] == 0.1

    def test_materials(self, capsys):
        main(["materials"])
        data = _json_output(capsys)
        assert data["count"] >= 5
        assert "6061-T6" in data["materials"]

    def test_beam_with_yield_strength(self, capsys):
        main(
            [
                "beam",
                "--load",
                "100",
                "--length",
                "1",
                "--youngs-modulus",
                "68.9e9",
                "--cross-section",
                '{"type":"rectangle","width":0.05,"height":0.01}',
                "--yield-strength",
                "276e6",
            ]
        )
        data = _json_output(capsys)
        assert data["safety_factor_yield"] > 1.0

    def test_workflow_list(self, capsys):
        main(["workflow", "list"])
        data = _json_output(capsys)
        assert "design_beam" in data["workflows"]

    def test_workflow_run_inputs_file(self, capsys, tmp_path):
        inputs = {
            "velocity": 120.0,
            "altitude_m": 3000.0,
            "characteristic_length": 1.8,
            "reference_area": 9.5,
            "lift": 18000.0,
            "drag": 1900.0,
            "flow_regime": "turbulent",
        }
        input_path = tmp_path / "inputs.json"
        input_path.write_text(json.dumps(inputs))

        main(["workflow", "run", "aero_characterization", "--inputs-file", str(input_path)])
        data = _json_output(capsys)
        assert data["outputs"]["mach"]["mach_number"] > 0

    def test_route(self, capsys):
        main(["route", "Mach number at 250 m/s and 10000m"])
        data = _json_output(capsys)
        assert data["type"] == "tool_call"
        assert data["tool_name"] == "mach_number"
