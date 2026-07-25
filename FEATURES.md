# Features

Everything rocket-tools can do, grouped by area. There are 80 computational tools plus
the platform pieces that wrap them. Every computational tool takes SI inputs, returns a
flat dictionary of numbers, validates its inputs, rejects NaN and infinity at the
boundary, and has a provenance entry you can pull with `cite_tool`.

Each tool is available three ways from one shared core: as a Python function, through the
`rocket-tools` command line, and as an MCP tool an AI agent can call.

## Structures

- `beam_analysis` — bending stress, deflection, and shear for common load and support cases.
- `section_properties` — area, moments of inertia, and section modulus for seven cross
  sections (rectangle, hollow rectangle, circle, hollow circle, I-beam, C-channel, T-section).
- `column_buckling` — Euler-Johnson buckling with end-condition factors.
- `plate_buckling_coefficient` — buckling coefficient k for plates in compression, shear, or bending.
- `margin_of_safety` — stress or load margin of safety.
- `von_mises_stress` — equivalent stress and principal stresses for combined loading.
- `combined_margin_of_safety` — margin for a combined stress state via von Mises.
- `deflection_margin` — margin against a deflection limit (L/360, L/500, or a custom ratio).
- `truss_analysis` — 2D and 3D pin-jointed trusses by the direct stiffness method.
- `thermal_stress` — stress and expansion of a restrained member heated or cooled by dT.
- `pressure_vessel_stress` — thin-wall hoop, longitudinal, and von Mises stress for a
  cylinder or sphere, with a margin against yield.
- `thick_wall_pressure_vessel_stress` — thick-wall (Lame) stresses at any radius ratio, for
  the r/t < 10 case where thin-wall theory is inaccurate.

## Materials

- `material_lookup` — mechanical and thermal properties for 49 aerospace materials by name,
  each with a source citation.
- `list_materials` — filter the database by family or by application (rocket, drone,
  aircraft, spacecraft, engine).

## Aerodynamics

- `reynolds_number`, `mach_number`, `dynamic_pressure` — the basics, with ISA lookups.
- `lift_coefficient`, `drag_coefficient` — coefficients from a force you supply.
- `skin_friction_coefficient` — flat-plate skin friction (laminar, transitional, turbulent).
- `aero_analysis` — a combined pass returning Reynolds, Mach, dynamic pressure, and the coefficients.

## Compressible flow

- `isentropic_flow` — temperature, pressure, density, and area ratios versus Mach.
- `normal_shock` — downstream conditions and the stagnation-pressure loss across a normal shock.
- `oblique_shock` — the weak-solution shock angle for a given deflection, with detachment handling.
- `prandtl_meyer` and `prandtl_meyer_from_angle` — expansion angle from Mach and the inverse.

## Aircraft performance

- `lift_curve_slope` — finite-wing lift-curve slope, subsonic and supersonic.
- `drag_polar` — drag coefficient with induced drag and Korn wave drag.
- `breguet_range` and `breguet_endurance` — cruise range and endurance.
- `wing_loading` — wing loading and stall speed.

## Propulsion

- `nozzle_performance` — thrust, specific impulse, thrust coefficient, and exit conditions
  for a de Laval nozzle, including under- and over-expansion with flow separation.
- `optimal_area_ratio` — the area ratio that matches exit pressure to ambient.
- `characteristic_velocity`, `ideal_specific_impulse`, `throat_mass_flux` — geometry-free
  figures of merit from combustion-gas properties.
- `motor_thrust_curve_analysis` — total impulse, burn time, average and peak thrust,
  delivered specific impulse, and NAR motor class from a measured thrust-time curve.

## Aerothermodynamics

- `stagnation_temperature` and `recovery_temperature` — total and adiabatic-wall temperature,
  with a flag when the perfect-gas assumption breaks down above Mach 5.
- `sutton_graves_heat_flux` — stagnation-point convective heating for blunt-body entry.
- `ballistic_entry_peak_deceleration` — Allen-Eggers peak deceleration for a steep entry.

## Mission design

- `rocket_delta_v` and `multi_stage_delta_v` — the rocket equation, single and multi-stage.
- `orbital_velocity` — circular and escape speed.
- `payload_fraction` — payload fraction from delta-v, specific impulse, and structural fraction.
- `thrust_to_weight` — thrust-to-weight with a hover and climb check.
- `composite_cg` — center of gravity and mass moments of inertia for a multi-part body.
- `propellant_tank_sizing` — tank mass, wall thickness, and dimensions for a cylinder,
  sphere, or ellipsoid, with hoop-stress wall sizing.

## Orbital mechanics

- `hohmann_transfer` — the two-impulse minimum-energy transfer.
- `bi_elliptic_transfer` — the three-impulse transfer, compared against Hohmann.
- `vis_viva_velocity` — orbital speed at a radius.
- `plane_change_delta_v` — the cost of a simple plane change.
- `orbital_period` — Keplerian period.
- `lambert_solver` — the transfer orbit joining two positions in a given time.
- `orbital_elements_from_state` and `state_from_orbital_elements` — convert between a state
  vector and the six classical elements, both directions.
- `kepler_propagate` — move a state vector forward or backward in time on its orbit.

## Trajectory and vehicle sizing

- `simulate_ascent` — an RK4 ascent through the full ISA atmosphere, reporting burnout,
  apogee, max dynamic pressure, peak g-load, and a time series.
- `size_vehicle` — preliminary mass sizing from a delta-v budget.
- `parachute_descent_rate` — terminal descent rate and landing energy under a round canopy.
- `parachute_area_for_descent_rate` — the canopy size needed for a target landing speed.

## Optimization

- `optimize_staging` — the payload-maximizing delta-v split across stages.
- `optimize_design` — a golden-section search over any output of any tool against one variable.

## Standards and reliability

- `design_review_report` — rolls up margins of safety into a PASS or FAIL verdict with the
  governing item.
- `fmea_report` — ranks failure modes by risk priority number (severity times occurrence
  times detection).
- `list_standards` — a catalog of the referenced aerospace standards.

## Visualization (optional `viz` extra)

`plot_beam_diagrams`, `plot_drag_polar`, `plot_nozzle_contour`, `plot_isa_profile`, and
`plot_trajectory`. Each returns a base64 PNG together with the underlying data series, or a
native MCP image, and degrades with a clear error if matplotlib is not installed.

## Working with results

- `cite_tool` — the reference, formula, assumptions, and validation benchmark behind any tool.
- `list_references` — the full bibliography.
- `parameter_sweep` — a trade study over any input, one row per value.
- `list_validation_benchmarks` and `validate_result` — check a computed number against a
  curated, reference-backed benchmark.
- `propagate_uncertainty` — Monte-Carlo propagation over any tool, reporting the mean,
  spread, and a 95% interval, plus which inputs drive each output.
- `unit_convert` — SI and imperial conversions.

## Platform

- **Python library.** Import any tool and call it directly.
- **Command line.** `rocket-tools` exposes the tools and can start the MCP server.
- **MCP server.** `rocket-tools serve` runs a stdio server so an AI agent can call any tool
  with structured inputs and validated outputs. There is also an ASGI app with health,
  readiness, and Prometheus metrics endpoints for a hosted deployment.
- **MCP resources.** Readable datasets an agent can pull as context: the bibliography, the
  benchmark set, per-tool provenance, the standards catalog, and the material database.
- **Natural-language router.** Ask a question in plain words and get a validated tool call.
- **Workflow engine.** Chain tools into reusable YAML workflows.

## How it compares

rocket-tools is a preliminary-design and education library that spans many domains, not a
deep specialist in any one of them. It sits one to two fidelity tiers below the dedicated
packages below, and it is meant to be reached for early, when you want a fast, traceable
number in code or from an agent rather than a GUI session or a solver run. For a final
design you still hand off to the specialist tool and a qualified engineer.

| Compared with | What that tool is best at | Where rocket-tools differs |
|---|---|---|
| OpenRocket, RASAero | Dedicated model and high-power rocket flight simulation with a drag build-up, stability, and recovery, in a GUI | Scriptable Barrowman center of pressure, a point-mass ascent, and parachute sizing at lower fidelity and no GUI, but as part of a broader library an agent can call |
| NASA CEA, RPA | Rocket chemical equilibrium and theoretical propellant performance | Ideal nozzle and specific-impulse relations given the gas properties; you bring the chamber temperature, gamma, and molecular weight that CEA computes. A chemical-equilibrium front end is on the roadmap |
| NASTRAN, Ansys, Abaqus | General finite-element structures, thermal, and modal analysis | Closed-form beams, columns, trusses, plates, and thermal and pressure-vessel stress; there is no general FEM |
| GMAT, STK, Orekit | High-fidelity mission design and operations with perturbations, ephemerides, and maneuver planning | Two-body transfers, a Lambert solver, orbit determination both directions, and Kepler propagation; no perturbations, low thrust, or ephemeris |
| poliastro, Orekit (Python) | Focused open-source astrodynamics | Overlaps on the two-body and Lambert core, but as one area of a wider aerospace library rather than a dedicated astrodynamics package |
| AeroSandbox | Python aircraft design and optimization with automatic differentiation | The closest multi-domain Python neighbor; rocket-tools leans toward rocketry and reference-backed lookups, and adds the MCP interface |

The one thing rocket-tools does that none of these do is expose validated aerospace
calculations as MCP tools with provenance you can query, so an AI agent can compute a
number and cite where it came from in the same call.
