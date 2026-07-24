"""Visualization tools (optional; requires the ``viz`` extra: matplotlib).

Presentation tools that return plots via a dual-return contract (data dict or native
MCP image). Deliberately excluded from the workflow/uncertainty dispatch registry.
"""

from rocket_tools.viz.diagrams import (
    plot_beam_diagrams,
    plot_drag_polar,
    plot_isa_profile,
    plot_nozzle_contour,
    plot_trajectory,
)

__all__ = [
    "plot_beam_diagrams",
    "plot_drag_polar",
    "plot_nozzle_contour",
    "plot_isa_profile",
    "plot_trajectory",
]
