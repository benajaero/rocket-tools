"""Benchmarks for aerodynamics calculations."""

from rocket_tools.aerodynamics import (
    aero_analysis,
    dynamic_pressure,
    mach_number,
    reynolds_number,
)


class TestBenchReynoldsNumber:
    def test_bench_re_direct(self, benchmark):
        benchmark(
            reynolds_number,
            velocity=100.0,
            characteristic_length=1.0,
            density=1.225,
            dynamic_viscosity=1.789e-5,
        )

    def test_bench_re_isa(self, benchmark):
        benchmark(
            reynolds_number,
            velocity=100.0,
            characteristic_length=1.0,
            altitude_m=5000.0,
        )


class TestBenchMachNumber:
    def test_bench_mach_sea_level(self, benchmark):
        benchmark(mach_number, 340.0, 0.0)

    def test_bench_mach_high_altitude(self, benchmark):
        benchmark(mach_number, 250.0, 10000.0)


class TestBenchDynamicPressure:
    def test_bench_q(self, benchmark):
        benchmark(dynamic_pressure, 100.0, 0.0)


class TestBenchAeroAnalysis:
    def test_bench_comprehensive(self, benchmark):
        benchmark(
            aero_analysis,
            velocity=250.0,
            altitude_m=5000.0,
            characteristic_length=2.0,
            reference_area=10.0,
            lift=50000.0,
            drag=5000.0,
        )
