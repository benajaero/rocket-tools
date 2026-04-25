"""Benchmarks for utility functions."""

import pytest
from rocket_tools.utils import unit_convert


class TestBenchUnitConvert:
    def test_bench_m_to_mm(self, benchmark):
        benchmark(unit_convert, 1.0, "m", "mm")

    def test_bench_psi_to_pa(self, benchmark):
        benchmark(unit_convert, 100.0, "psi", "pa")

    def test_bench_temp_conversion(self, benchmark):
        benchmark(unit_convert, 20.0, "c", "k")
