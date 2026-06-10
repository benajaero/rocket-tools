"""Validation dataset and benchmark cases for rocket-tools.

Provides curated test cases with expected values and primary references
for verifying tool accuracy against established data.

References:
    - Abbott & von Doenhoff, "Theory of Wing Sections", Dover 1959.
    - Blasius (1908), ZAMM: Grenzschichten in Flussigkeiten.
    - Roark's Formulas for Stress and Strain, 8th Ed.
    - NASA-TM-X-74335: U.S. Standard Atmosphere, 1976.
    - Sutton & Biblarz, "Rocket Propulsion Elements", 9th Ed.
"""

from .benchmarks import get_benchmark, list_benchmarks

__all__ = ["get_benchmark", "list_benchmarks"]
