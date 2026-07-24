"""Plot builders for rocket-tools visualizations.

Each function reuses the corresponding computational tool for its data and returns via
the dual-return contract in :mod:`rocket_tools.viz.backend`. They are presentation
tools, deliberately kept out of the workflow/uncertainty dispatch registry.
"""

import numpy as np

from rocket_tools.aerodynamics.aircraft import drag_polar
from rocket_tools.materials.isa import isa_atmosphere
from rocket_tools.structural.beams import _beam_stations, beam_analysis
from rocket_tools.trajectory import simulate_ascent
from rocket_tools.viz.backend import figure_to_result, require_matplotlib


def plot_beam_diagrams(
    load: float,
    length: float,
    youngs_modulus: float,
    cross_section: dict,
    load_type: str = "point_midspan",
    support_type: str = "simply_supported",
    render: str = "data",
    output_path: str | None = None,
) -> dict:
    """Shear, bending-moment, and deflection diagrams along a beam span (Roark 8.1)."""
    plt = require_matplotlib()
    result = beam_analysis(
        load=load,
        length=length,
        youngs_modulus=youngs_modulus,
        cross_section=cross_section,
        load_type=load_type,  # type: ignore[arg-type]
        support_type=support_type,  # type: ignore[arg-type]
    )
    stations = _beam_stations(
        load, length, youngs_modulus, result["area_moment_m4"], load_type, support_type
    )
    x = stations["x_m"]

    fig, axes = plt.subplots(3, 1, figsize=(7, 8), sharex=True)
    axes[0].plot(x, stations["shear_n"], color="#1f77b4")
    axes[0].set_ylabel("Shear V (N)")
    axes[0].axhline(0, color="k", lw=0.5)
    axes[1].plot(x, stations["moment_n_m"], color="#d62728")
    axes[1].set_ylabel("Moment M (N·m)")
    axes[1].axhline(0, color="k", lw=0.5)
    axes[2].plot(x, stations["deflection_m"] * 1e3, color="#2ca02c")
    axes[2].set_ylabel("Deflection (mm)")
    axes[2].set_xlabel("Position along span (m)")
    axes[0].set_title(f"Beam diagrams — {load_type}, {support_type}")
    for ax in axes:
        ax.grid(True, alpha=0.3)

    meta = {
        "load_type": load_type,
        "support_type": support_type,
        "max_deflection_m": result["max_deflection_m"],
        "max_bending_moment_n_m": result["max_bending_moment_n_m"],
        "bending_stress_pa": result["bending_stress_pa"],
    }
    return figure_to_result(fig, stations, meta, render, output_path)


def plot_drag_polar(
    cd0: float,
    aspect_ratio: float,
    oswald_efficiency: float = 0.85,
    mach: float = 0.0,
    cl_max: float = 1.5,
    render: str = "data",
    output_path: str | None = None,
) -> dict:
    """Drag polar CD vs CL (and L/D vs CL) for a given aircraft configuration."""
    plt = require_matplotlib()
    cl = np.linspace(0.0, cl_max, 60)
    cd = np.array(
        [
            drag_polar(float(c), cd0, aspect_ratio, oswald_efficiency, mach)["drag_coefficient"]
            for c in cl
        ]
    )
    ld = np.divide(cl, cd, out=np.zeros_like(cl), where=cd > 0)
    ld_max_i = int(np.argmax(ld))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
    ax1.plot(cd, cl, color="#1f77b4")
    ax1.set_xlabel("Drag coefficient C_D")
    ax1.set_ylabel("Lift coefficient C_L")
    ax1.set_title("Drag polar")
    ax1.grid(True, alpha=0.3)
    ax2.plot(cl, ld, color="#d62728")
    ax2.scatter([cl[ld_max_i]], [ld[ld_max_i]], color="k", zorder=5)
    ax2.annotate(f"(L/D)max={ld[ld_max_i]:.1f}", (cl[ld_max_i], ld[ld_max_i]))
    ax2.set_xlabel("Lift coefficient C_L")
    ax2.set_ylabel("L/D")
    ax2.set_title("Lift-to-drag ratio")
    ax2.grid(True, alpha=0.3)

    series = {"lift_coefficient": cl, "drag_coefficient": cd, "lift_to_drag_ratio": ld}
    meta = {
        "cd0": cd0,
        "aspect_ratio": aspect_ratio,
        "ld_max": round(float(ld[ld_max_i]), 2),
        "cl_at_ld_max": round(float(cl[ld_max_i]), 3),
    }
    return figure_to_result(fig, series, meta, render, output_path)


def plot_nozzle_contour(
    throat_radius_m: float,
    area_ratio: float,
    half_angle_deg: float = 15.0,
    render: str = "data",
    output_path: str | None = None,
) -> dict:
    """Conical convergent-divergent nozzle wall contour from throat radius and A_e/A*."""
    require_matplotlib()
    if throat_radius_m <= 0:
        raise ValueError("throat_radius_m must be > 0")
    if area_ratio < 1.0:
        raise ValueError("area_ratio must be >= 1")
    plt = require_matplotlib()

    rt = throat_radius_m
    re = rt * np.sqrt(area_ratio)
    half = np.radians(half_angle_deg)
    # Convergent 30-deg cone from chamber (2x throat radius) into throat, then
    # divergent cone at half_angle_deg out to the exit radius.
    rc = 2.0 * rt
    conv_len = (rc - rt) / np.tan(np.radians(30.0))
    div_len = (re - rt) / np.tan(half)

    x_conv = np.linspace(-conv_len, 0.0, 30)
    r_conv = rt + (rc - rt) * (-x_conv) / conv_len
    x_div = np.linspace(0.0, div_len, 40)
    r_div = rt + (re - rt) * x_div / div_len
    x = np.concatenate([x_conv, x_div])
    r = np.concatenate([r_conv, r_div])

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(x, r, color="#1f77b4")
    ax.plot(x, -r, color="#1f77b4")
    ax.fill_between(x, r, -r, color="#1f77b4", alpha=0.08)
    ax.axvline(0, color="k", lw=0.5, ls="--")
    ax.set_xlabel("Axial position (m)")
    ax.set_ylabel("Radius (m)")
    ax.set_title(f"Nozzle contour — A_e/A* = {area_ratio:.1f}")
    ax.set_aspect("equal", adjustable="datalim")
    ax.grid(True, alpha=0.3)

    series = {"x_m": x, "radius_m": r}
    meta = {
        "throat_radius_m": rt,
        "exit_radius_m": round(float(re), 4),
        "area_ratio": area_ratio,
        "divergent_length_m": round(float(div_len), 4),
        "half_angle_deg": half_angle_deg,
    }
    return figure_to_result(fig, series, meta, render, output_path)


def plot_isa_profile(
    max_altitude_m: float = 84000.0,
    render: str = "data",
    output_path: str | None = None,
) -> dict:
    """Temperature, pressure, and density vs altitude (US Standard Atmosphere 1976)."""
    plt = require_matplotlib()
    if not 0 < max_altitude_m <= 84852.0:
        raise ValueError("max_altitude_m must be in (0, 84852]")
    alt = np.linspace(0.0, max_altitude_m, 120)
    t = np.array([isa_atmosphere(float(h))["temperature_k"] for h in alt])
    p = np.array([isa_atmosphere(float(h))["pressure_pa"] for h in alt])
    rho = np.array([isa_atmosphere(float(h))["density_kg_m3"] for h in alt])
    km = alt / 1000.0

    fig, axes = plt.subplots(1, 3, figsize=(12, 4.5), sharey=True)
    axes[0].plot(t, km, color="#d62728")
    axes[0].set_xlabel("Temperature (K)")
    axes[0].set_ylabel("Altitude (km)")
    axes[1].semilogx(p, km, color="#1f77b4")
    axes[1].set_xlabel("Pressure (Pa)")
    axes[2].semilogx(rho, km, color="#2ca02c")
    axes[2].set_xlabel("Density (kg/m³)")
    for ax in axes:
        ax.grid(True, alpha=0.3)
    fig.suptitle("U.S. Standard Atmosphere 1976")

    series = {"altitude_m": alt, "temperature_k": t, "pressure_pa": p, "density_kg_m3": rho}
    meta = {"max_altitude_m": max_altitude_m}
    return figure_to_result(fig, series, meta, render, output_path)


def plot_trajectory(
    initial_mass_kg: float,
    dry_mass_kg: float,
    specific_impulse_s: float,
    mass_flow_rate_kg_s: float,
    reference_area_m2: float,
    drag_coefficient: float = 0.5,
    launch_angle_deg: float = 90.0,
    dt: float = 0.1,
    render: str = "data",
    output_path: str | None = None,
) -> dict:
    """Run an ascent simulation and plot altitude, velocity, dynamic pressure, and g-load."""
    plt = require_matplotlib()
    sim = simulate_ascent(
        initial_mass_kg=initial_mass_kg,
        dry_mass_kg=dry_mass_kg,
        specific_impulse_s=specific_impulse_s,
        mass_flow_rate_kg_s=mass_flow_rate_kg_s,
        reference_area_m2=reference_area_m2,
        drag_coefficient=drag_coefficient,
        launch_angle_deg=launch_angle_deg,
        dt=dt,
    )
    s = sim["series"]
    t = np.array(s["time_s"])

    fig, axes = plt.subplots(2, 2, figsize=(11, 7))
    axes[0, 0].plot(t, np.array(s["altitude_m"]) / 1000.0, color="#1f77b4")
    axes[0, 0].set_ylabel("Altitude (km)")
    axes[0, 1].plot(t, s["velocity_ms"], color="#d62728")
    axes[0, 1].set_ylabel("Velocity (m/s)")
    axes[1, 0].plot(t, np.array(s["dynamic_pressure_pa"]) / 1000.0, color="#2ca02c")
    axes[1, 0].set_ylabel("Dynamic pressure (kPa)")
    axes[1, 0].set_xlabel("Time (s)")
    axes[1, 1].plot(t, s["acceleration_g"], color="#9467bd")
    axes[1, 1].set_ylabel("Acceleration (g)")
    axes[1, 1].set_xlabel("Time (s)")
    for ax in axes.flat:
        ax.grid(True, alpha=0.3)
    fig.suptitle(
        f"Ascent — apogee {sim['apogee_km']:.1f} km, "
        f"max-q {sim['max_dynamic_pressure_pa'] / 1000:.0f} kPa"
    )

    series = {
        "time_s": t,
        "altitude_m": s["altitude_m"],
        "velocity_ms": s["velocity_ms"],
        "dynamic_pressure_pa": s["dynamic_pressure_pa"],
        "acceleration_g": s["acceleration_g"],
    }
    meta = {
        "apogee_m": sim["apogee_m"],
        "max_dynamic_pressure_pa": sim["max_dynamic_pressure_pa"],
        "max_accel_g": sim["max_accel_g"],
        "burnout_velocity_ms": sim["burnout_velocity_ms"],
    }
    return figure_to_result(fig, series, meta, render, output_path)
