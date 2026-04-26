"""Benchmarks for material and ISA lookups."""

from rocket_tools.materials import isa_atmosphere, material_lookup


class TestBenchMaterialLookup:
    def test_bench_lookup_hit(self, benchmark):
        benchmark(material_lookup, "6061-T6")

    def test_bench_lookup_hit_filter(self, benchmark):
        benchmark(material_lookup, "Ti-6Al-4V", "density")


class TestBenchISA:
    def test_bench_isa_sea_level(self, benchmark):
        benchmark(isa_atmosphere, 0.0)

    def test_bench_isa_troposphere(self, benchmark):
        benchmark(isa_atmosphere, 5000.0)

    def test_bench_isa_interpolated(self, benchmark):
        benchmark(isa_atmosphere, 1234.5)
