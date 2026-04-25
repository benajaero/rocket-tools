"""Benchmarks for structural analysis."""

import pytest
from rocket_tools.structural import beam_analysis


BEAM_CONFIG = {
    "load": 100.0,
    "length": 1.0,
    "youngs_modulus": 68.9e9,
    "cross_section": {"type": "rectangle", "width": 0.05, "height": 0.01},
}


class TestBenchBeamAnalysis:
    def test_bench_simply_supported_point(self, benchmark):
        benchmark(
            beam_analysis,
            BEAM_CONFIG["load"],
            BEAM_CONFIG["length"],
            BEAM_CONFIG["youngs_modulus"],
            BEAM_CONFIG["cross_section"],
            "point_midspan",
            "simply_supported",
        )

    def test_bench_cantilever(self, benchmark):
        benchmark(
            beam_analysis,
            BEAM_CONFIG["load"],
            BEAM_CONFIG["length"],
            BEAM_CONFIG["youngs_modulus"],
            BEAM_CONFIG["cross_section"],
            "point_midspan",
            "cantilever",
        )

    def test_bench_distributed(self, benchmark):
        benchmark(
            beam_analysis,
            50.0,  # N/m distributed
            BEAM_CONFIG["length"],
            BEAM_CONFIG["youngs_modulus"],
            BEAM_CONFIG["cross_section"],
            "distributed",
            "simply_supported",
        )

    def test_bench_axial_buckling(self, benchmark):
        benchmark(
            beam_analysis,
            1000.0,
            BEAM_CONFIG["length"],
            200e9,
            {"type": "circle", "diameter": 0.05},
            "axial",
            "simply_supported",
        )
