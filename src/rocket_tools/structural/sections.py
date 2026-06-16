"""Cross-section properties for beams, columns, and structural members.

Supports shapes used in aircraft, rockets, drones, and helicopters:
- Rectangle, hollow rectangle (box beams)
- Circle, hollow circle (tubes, struts)
- I-beam (aircraft spars, helicopter rotor masts)
- C-channel (stringers, stiffeners)
- T-section (floor beams, brackets)
"""

from typing import Literal

import numpy as np
from numba import njit


@njit(cache=True)
def _rectangle_properties(b: float, h: float):
    """Area, I, S, r for solid rectangle."""
    area = b * h
    i_xx = (b * h**3) / 12.0
    s_xx = (b * h**2) / 6.0
    r_xx = h / (2.0 * np.sqrt(3.0))
    return area, i_xx, s_xx, r_xx


@njit(cache=True)
def _hollow_rectangle_properties(b: float, h: float, t: float):
    """Area, I, S, r for hollow rectangle (box section)."""
    b_i = b - 2.0 * t
    h_i = h - 2.0 * t
    area = b * h - b_i * h_i
    i_xx = (b * h**3 - b_i * h_i**3) / 12.0
    s_xx = i_xx / (h / 2.0)
    r_xx = np.sqrt(i_xx / area) if area > 0.0 else 0.0
    return area, i_xx, s_xx, r_xx


@njit(cache=True)
def _circle_properties(d: float):
    """Area, I, S, r for solid circle."""
    r = d / 2.0
    area = np.pi * r**2
    i_xx = (np.pi * r**4) / 4.0
    s_xx = (np.pi * r**3) / 4.0
    r_g = r / 2.0
    return area, i_xx, s_xx, r_g


@njit(cache=True)
def _hollow_circle_properties(d_o: float, d_i: float):
    """Area, I, S, r for hollow circle (tube)."""
    r_o = d_o / 2.0
    r_i = d_i / 2.0
    area = np.pi * (r_o**2 - r_i**2)
    i_xx = (np.pi / 4.0) * (r_o**4 - r_i**4)
    s_xx = i_xx / r_o
    r_g = np.sqrt((r_o**2 + r_i**2) / 2.0)
    return area, i_xx, s_xx, r_g


@njit(cache=True)
def _ibeam_properties(b_f: float, h: float, t_f: float, t_w: float):
    """Area, I, S, r for I-beam.

    Approximate: flange width b_f, overall height h, flange thickness t_f, web thickness t_w.
    """
    h_w = h - 2.0 * t_f
    area = 2.0 * b_f * t_f + h_w * t_w
    i_web = (t_w * h_w**3) / 12.0
    i_flanges = 2.0 * ((b_f * t_f**3) / 12.0 + b_f * t_f * ((h_w + t_f) / 2.0) ** 2)
    i_xx = i_web + i_flanges
    s_xx = i_xx / (h / 2.0)
    r_xx = np.sqrt(i_xx / area) if area > 0.0 else 0.0
    return area, i_xx, s_xx, r_xx


@njit(cache=True)
def _cchannel_properties(b: float, h: float, t_f: float, t_w: float):
    """Area, I, S, r for C-channel.

    Approximate: flange width b, overall height h, flange thickness t_f, web thickness t_w.
    """
    h_w = h - 2.0 * t_f
    area = 2.0 * b * t_f + h_w * t_w
    i_web = (t_w * h_w**3) / 12.0
    i_flanges = 2.0 * ((b * t_f**3) / 12.0 + b * t_f * ((h_w + t_f) / 2.0) ** 2)
    i_xx = i_web + i_flanges
    s_xx = i_xx / (h / 2.0)
    r_xx = np.sqrt(i_xx / area) if area > 0.0 else 0.0
    return area, i_xx, s_xx, r_xx


@njit(cache=True)
def _tsection_properties(b_f: float, h: float, t_f: float, t_w: float):
    """Area, I, S, r for T-section.

    Approximate: flange width b_f, overall height h, flange thickness t_f, web thickness t_w.
    """
    h_w = h - t_f
    area = b_f * t_f + h_w * t_w
    # Centroid from base
    y_c = (b_f * t_f * (h - t_f / 2.0) + h_w * t_w * (h_w / 2.0)) / area
    # I about centroid
    i_flange = (b_f * t_f**3) / 12.0 + b_f * t_f * (h - t_f / 2.0 - y_c) ** 2
    i_web = (t_w * h_w**3) / 12.0 + h_w * t_w * (y_c - h_w / 2.0) ** 2
    i_xx = i_flange + i_web
    s_xx = i_xx / max(y_c, h - y_c)
    r_xx = np.sqrt(i_xx / area) if area > 0.0 else 0.0
    return area, i_xx, s_xx, r_xx


def section_properties(
    shape: Literal[
        "rectangle",
        "hollow_rectangle",
        "circle",
        "hollow_circle",
        "ibeam",
        "cchannel",
        "tsection",
    ],
    **kwargs: float,
) -> dict:
    """Compute cross-sectional properties for common structural shapes.

    Shapes:
        rectangle: width, height
        hollow_rectangle: width, height, wall_thickness
        circle: diameter
        hollow_circle: outer_diameter, inner_diameter
        ibeam: flange_width, height, flange_thickness, web_thickness
        cchannel: flange_width, height, flange_thickness, web_thickness
        tsection: flange_width, height, flange_thickness, web_thickness

    Returns:
        dict with area_m2, i_xx_m4 (area moment of inertia),
        s_xx_m3 (section modulus), r_xx_m (radius of gyration)
    """
    shape_key = shape.lower()

    if shape_key == "rectangle":
        b = kwargs["width"]
        h = kwargs["height"]
        if b <= 0 or h <= 0:
            raise ValueError("width and height must be > 0")
        area, i_xx, s_xx, r_xx = _rectangle_properties(b, h)

    elif shape_key == "hollow_rectangle":
        b = kwargs["width"]
        h = kwargs["height"]
        t = kwargs["wall_thickness"]
        if b <= 0 or h <= 0 or t <= 0:
            raise ValueError("width, height, and wall_thickness must be > 0")
        if t >= b / 2 or t >= h / 2:
            raise ValueError("wall_thickness must be less than half of width/height")
        area, i_xx, s_xx, r_xx = _hollow_rectangle_properties(b, h, t)

    elif shape_key == "circle":
        d = kwargs["diameter"]
        if d <= 0:
            raise ValueError("diameter must be > 0")
        area, i_xx, s_xx, r_xx = _circle_properties(d)

    elif shape_key == "hollow_circle":
        d_o = kwargs["outer_diameter"]
        d_i = kwargs["inner_diameter"]
        if d_o <= 0 or d_i <= 0:
            raise ValueError("diameters must be > 0")
        if d_i >= d_o:
            raise ValueError("inner_diameter must be less than outer_diameter")
        area, i_xx, s_xx, r_xx = _hollow_circle_properties(d_o, d_i)

    elif shape_key == "ibeam":
        b_f = kwargs["flange_width"]
        h = kwargs["height"]
        t_f = kwargs["flange_thickness"]
        t_w = kwargs["web_thickness"]
        if b_f <= 0 or h <= 0 or t_f <= 0 or t_w <= 0:
            raise ValueError("all dimensions must be > 0")
        area, i_xx, s_xx, r_xx = _ibeam_properties(b_f, h, t_f, t_w)

    elif shape_key == "cchannel":
        b = kwargs["flange_width"]
        h = kwargs["height"]
        t_f = kwargs["flange_thickness"]
        t_w = kwargs["web_thickness"]
        if b <= 0 or h <= 0 or t_f <= 0 or t_w <= 0:
            raise ValueError("all dimensions must be > 0")
        area, i_xx, s_xx, r_xx = _cchannel_properties(b, h, t_f, t_w)

    elif shape_key == "tsection":
        b_f = kwargs["flange_width"]
        h = kwargs["height"]
        t_f = kwargs["flange_thickness"]
        t_w = kwargs["web_thickness"]
        if b_f <= 0 or h <= 0 or t_f <= 0 or t_w <= 0:
            raise ValueError("all dimensions must be > 0")
        area, i_xx, s_xx, r_xx = _tsection_properties(b_f, h, t_f, t_w)

    else:
        raise ValueError(f"Unknown shape: {shape_key}")

    return {
        "shape": shape_key,
        "area_m2": area,
        "i_xx_m4": i_xx,
        "s_xx_m3": s_xx,
        "r_xx_m": r_xx,
    }
