"""End-to-end rocket design: ascent trajectory simulation and preliminary sizing."""

from rocket_tools.trajectory.recovery import (
    parachute_area_for_descent_rate,
    parachute_descent_rate,
)
from rocket_tools.trajectory.vehicle import simulate_ascent, size_vehicle

__all__ = [
    "simulate_ascent",
    "size_vehicle",
    "parachute_descent_rate",
    "parachute_area_for_descent_rate",
]
