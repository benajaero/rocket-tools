# Changelog

All notable changes to rocket-tools.

## [Unreleased]

## [0.5.0] — 2026-07-25

Twelve new reference-validated tools (68 → 80) plus a batch of correctness fixes that made
the existing tools trustworthy for real design work.

### Added
- **Static stability** — `center_of_pressure()` and `static_margin()` (new `rocket_tools.aerodynamics.stability`). Subsonic center of pressure of a fin-stabilized rocket by the Barrowman method (nose + trapezoidal fins on a straight body), and static margin in calibers from CP, CG, and reference diameter. CP is pinned to a hand-computed Barrowman case. This closes the biggest rocketry gap: a vehicle with the CP ahead of the CG is unflyable regardless of its delta-v. Tool count 68 → 70.
- **Recovery sizing** — `parachute_descent_rate()` and `parachute_area_for_descent_rate()` (new `rocket_tools.trajectory.recovery`). Terminal descent rate and landing kinetic energy under a round parachute from the steady-descent drag balance, and the inverse (canopy area/diameter for a target landing speed). Air density defaults to ISA at altitude with an explicit override. Tool count 70 → 72.
- **Astrodynamics — orbit determination, targeting, and propagation** (added to `rocket_tools.design.orbital`):
  - `lambert_solver()` — universal-variable Lambert solution (Curtis Algorithm 5.2) for the transfer orbit joining two positions in a given time; validated against Curtis Example 5.2 to 4+ significant figures (`lambert_curtis_5_2` benchmark).
  - `orbital_elements_from_state()` — classical orbital elements from a state vector (Curtis Algorithm 4.2); validated against Curtis Example 4.3 (`coe_from_state_curtis_4_3` benchmark).
  - `state_from_orbital_elements()` — the inverse, a state vector from the elements (Curtis Algorithm 4.5); validated against Curtis Example 4.7 (`state_from_coe_curtis_4_7` benchmark).
  - `kepler_propagate()` — universal-variable time-of-flight state propagation (Curtis Algorithm 3.4), forward or backward; validated against Curtis Example 3.7 (`kepler_propagate_curtis_3_7` benchmark).
  - Together these cover the two-body determine → target → propagate workflow. Tool count 72 → 76.
- **Motor ballistics** — `motor_thrust_curve_analysis()` (in `rocket_tools.aerodynamics.propulsion`). From a measured thrust-time table and propellant mass: total impulse (trapezoidal integral), burn time, average/peak thrust, delivered specific impulse, effective exhaust velocity, and the NAR/TRA motor class and designation (e.g. `C6`). Tool count 76 → 77.
- **Thermal stress** — `thermal_stress()` (new `rocket_tools.structural.thermal`). Restrained-member thermal stress `sigma = -constraint*E*alpha*dT` (compressive when heated), plus free thermal strain, free/restrained elongation, and restraint force. Closes the "no thermal stress" gap previously noted in `docs/scientific-validity.md`. Tool count 77 → 78.
- **Pressure-vessel stress** — `pressure_vessel_stress()` (new `rocket_tools.structural.pressure`). Thin-wall membrane hoop/longitudinal stresses for a pressurized cylinder or sphere, the von Mises equivalent, the r/t ratio with a thin-wall-validity flag, and a margin of safety against yield. The stress-analysis complement to `propellant_tank_sizing`. Tool count 78 → 79.
- **Bi-elliptic transfer** — `bi_elliptic_transfer()` (in `rocket_tools.design.orbital`). Three-impulse transfer between coplanar circular orbits via an intermediate apoapsis, each burn from vis-viva; returns the three burns, total delta-v/time, and a direct comparison against the Hohmann transfer (it wins for large radius ratios). Validated against a hand-computed Curtis Ch. 6 case and cross-checked against `vis_viva_velocity`. Tool count 79 → 80.
- **`examples/sounding_rocket_flight.py`** and **`examples/orbit_determination.py`** — runnable end-to-end workflows that chain the new tools (thrust-curve reduction → Barrowman static margin → ISA ascent → parachute sizing → thermal check; and Lambert → orbital elements → propagation → round-trip). Both run as integration tests.

### Fixed
- **Structural correctness** — truss support reactions were computed from the penalty-augmented stiffness matrix and returned ≈0; now use the original stiffness so reactions are correct. Beam shear stress was dimensionally wrong (fixed to `tau = k*V/A` with the right section factor). The cantilever `point_midspan` case was actually applying a tip load; corrected, and a distinct `point_tip` load type added. The plate-compression buckling coefficient `k` was ~6× unconservative; replaced with the exact minimum-over-m. Added geometry validation to I-beam/C-channel/T-section and zero-length-member guards to the truss.
- **Aerodynamics correctness** — `breguet_range` was ~9.8× too large (missing the `g` factor). `aero_analysis` crashed on transitional Reynolds numbers. `lift_curve_slope` produced a singularity at M = 1 (now rejects the transonic band and supersonic subsonic-leading-edge cases). `drag_polar` used a fabricated wave-drag term; replaced with the Korn drag-divergence model. The nozzle tool defaulted to air, ignored flow separation, and divided by zero in vacuum; now uses combustion-gas defaults, models Summerfield overexpansion separation, and guards the vacuum case.
- **Propulsion / trajectory / mass fidelity** — `composite_cg` dropped each component's own inertia (now added via parallel-axis). `propellant_tank_sizing` gained real hoop-stress wall sizing, hemispherical cylinder domes, and a corrected ellipsoid surface area. Unified the gas constant to CODATA. `stagnation_temperature` flags `perfect_gas_valid=False` above M5; `simulate_ascent` reports `apogee_reached`.
- **Data & provenance** — 7075 aluminum was mistakenly cited to the steel chapter of MIL-HDBK-5J (fixed to the aluminum section, marked representative); Rhenium's Poisson ratio was corrected 0.49 → 0.30.

### Changed
- **Stricter validation everywhere** — the new tools raise clear, structured errors on out-of-envelope inputs (degenerate Lambert geometry, inconsistent orbital elements, non-monotonic thrust curves, etc.) instead of returning wrong numbers.
- **Honest scope docs** — `docs/scientific-validity.md` rewritten: "validated" means textbook-consistent (not experimental), with the real assumptions and missing tiers spelled out, and updated to describe the new stability, recovery, astrodynamics, and thermal-stress capabilities and their limits.
- Updated the README (78 tools, test count), inventory floors (`tests/test_packaging.py`, `scripts/verify_release.sh`), and per-tool provenance for every new tool.

## [0.4.1] — 2026-07-25

### Fixed
- **Python 3.13 support** — widened `requires-python` from `<3.13` to `<3.14` and added the 3.13 classifier and CI leg. `pip install rocket-tools` previously failed outright on Python 3.13; the full suite now passes on 3.13 (numba 0.66, numpy 2.4).
- **Correct MCP launch command in the docs** — the README said to run `rocket-tools` to start the server, but the server is `rocket-tools serve`; bare `rocket-tools` only prints help. Fixed, and added a copy-paste `claude_desktop_config.json` block (pip and `uvx` variants) so adding it to Claude Desktop is a paste, not a puzzle.
- **The README quickstart actually runs now** — the headline Python example had drifted from the real API in nine places (`ns['mach2']`→`mach_downstream`, `import convert`→`unit_convert` returning a dict, the `m_s`→`m/s` unit, `section_properties("ibeam", width=...)`→`flange_width`, `buckling['failure_mode']`→`regime`, the oblique-shock angle key, and wrong kwargs on `rocket_delta_v`/`orbital_velocity`/`propellant_tank_sizing`). Every runnable code block now executes.

### Added
- **`examples/`** — runnable `quickstart.py` and `ascent_and_sizing.py` scripts.
- **`tests/test_readme_examples.py`** — executes every self-contained README code block and the example scripts in CI, so the docs cannot silently rot again.

### Changed
- Updated the agent-facing MCP tool manifest (was "35 tools", now 68) with the trajectory, optimization, visualization, and standards tools.

## [0.4.0] — 2026-07-24

### Added
- **End-to-end rocket design** — `simulate_ascent()` and `size_vehicle()` (new `rocket_tools.trajectory` package). `simulate_ascent` integrates a planar point-mass gravity-turn ascent with a fixed-step RK4 kernel (Numba-JIT) through the full 7-layer ISA atmosphere (thrust, drag, altitude-varying gravity), reporting burnout/apogee events, max-q, peak g-load, and downsampled time-series. A self-contained `_isa_rho` kernel reproduces `isa_atmosphere` to <1e-5 (parity-tested). `size_vehicle` solves the rocket equation for gross mass and chains `rocket_delta_v`/`thrust_to_weight`/`propellant_tank_sizing`. Validated against the closed-form vacuum trajectory (Sutton & Biblarz Ch. 4 / Curtis Ch. 11); new `ascent_vacuum_vertical` benchmark. Tool count 56 → 58.
- **Optimization** — `optimize_staging()` and `optimize_design()` (new `rocket_tools.optimization` package). `optimize_staging` solves the restricted optimal-staging problem via a Lagrange multiplier with robust bracketed bisection (no negative-ΔV escape), returning the payload-fraction-maximizing ΔV split; validated against an independent brute-force optimum and the analytic symmetric case (`staging_optimum_symmetric` benchmark, Curtis Ch. 11). `optimize_design` generalizes `parameter_sweep` to a golden-section search over any output of any dispatch tool (pure numpy, no scipy). Tool count 58 → 60.
- **Visualization** — `plot_beam_diagrams()`, `plot_drag_polar()`, `plot_nozzle_contour()`, `plot_isa_profile()`, `plot_trajectory()` (new optional `rocket_tools.viz` package; `pip install rocket-tools[viz]`). Dual-return contract: `render="data"` (default) returns a JSON dict with a base64 PNG **plus** the underlying data series; `render="image"` returns a native MCP image. Graceful degradation with a structured `MISSING_DEPENDENCY` error when matplotlib is absent. Added a private `_beam_stations` helper (shear/moment/deflection along the span, Roark Table 8.1). Tool count 60 → 65.
- **Standards & reliability** — `design_review_report()`, `fmea_report()`, `list_standards()` (new `rocket_tools.standards` package) plus the `rocket-tools://standards` MCP resource. `design_review_report` rolls up margins of safety (reusing `margin_of_safety`) into a governing-margin PASS/FAIL verdict; `fmea_report` ranks failure modes by RPN = S×O×D (MIL-STD-1629A / SAE J1739); `list_standards` catalogs the referenced standards. Tool count 65 → 68; resources 5 → 6.
- **Honest coverage of JIT hot paths** — tests now run with `NUMBA_DISABLE_JIT=1` (new `tests/conftest.py`) so coverage.py can trace Numba-compiled functions as pure Python. Total coverage 82% → 87%; the trajectory integrator and existing compressible/buckling kernels are now measured honestly.
- **Research workflow tools** — `parameter_sweep()`, `list_validation_benchmarks()`, `validate_result()`
  - `parameter_sweep(tool, params, sweep_parameter, values)` runs a trade study over any input, one row per value (per-point errors don't abort the sweep)
  - `list_validation_benchmarks()` + `validate_result(benchmark_name, result)` let an agent self-check a computed number against a curated, reference-backed benchmark. Tool count 53 → 56
- **MCP Resources** — readable research datasets exposed via the MCP resources primitive
  - `rocket-tools://references` (bibliography), `://benchmarks` (curated validation dataset), `://provenance` (per-tool sources/formulas/assumptions), `://materials` (full database), and templated `://materials/{name}`
  - Lets an agent pull authoritative context directly instead of discovering it one tool call at a time
- **Uncertainty & sensitivity** — `propagate_uncertainty()` MCP tool
  - Monte-Carlo propagation over any computational tool: per-output mean, std, min, max, and 95% CI
  - Correlation-based sensitivity ranking of which inputs drive each output (one-pass, from the same samples)
  - Expanded the workflow/uncertainty tool dispatch from 11 hand-picked tools to **all 50** computational tools (dynamic registry), so uncertainty and workflows reach every calculation. Tool count 52 → 53
- **Research provenance tools** — `cite_tool()` and `list_references()`
  - `cite_tool(tool_name)` returns the authoritative reference(s), governing formula, modelling assumptions, and any curated validation benchmark backing a tool (with a `validated` flag) — so any computed number is traceable and citable
  - `list_references()` returns the de-duplicated bibliography and the documented tool list
  - New `rocket_tools.provenance` registry covering all 50 computational tools; a completeness test keeps it in sync as tools are added. Tool count 50 → 52
- **Propulsion thermochemistry** — `characteristic_velocity()`, `ideal_specific_impulse()`, `throat_mass_flux()`
  - Geometry-free propellant figures of merit (Sutton & Biblarz Ch. 3): c* via the Vandenkerckhove function, ideal exhaust velocity/Isp from the pressure ratio, choked throat mass flux
  - New `characteristic_velocity_lox_rp1` regression benchmark; tool count 47 → 50
- **Aerothermodynamics** — `stagnation_temperature()`, `recovery_temperature()`, `sutton_graves_heat_flux()`, `ballistic_entry_peak_deceleration()`
  - Stagnation/recovery temperature (Anderson), Sutton-Graves stagnation-point heat flux (NASA TR R-376), Allen-Eggers ballistic-entry peak deceleration (NACA TR 1381)
  - New `stagnation_temperature_mach3` and `ballistic_entry_allen_eggers` regression benchmarks; tool count 43 → 47
- **Full atmosphere to 86 km** — `isa_atmosphere()` now implements the complete 7-layer U.S. Standard Atmosphere 1976 (was 3-layer, 0–25 km)
  - Valid range 0–84,852 m geopotential (86 km geometric); matches NASA-TM-X-74335 Table 1 to <0.02% at every layer boundary
  - New `isa_47000m` (stratopause) and `isa_71000m` regression benchmarks; significant-figure output so sub-pascal pressures/densities aren't rounded away
- **Orbital Mechanics** — `hohmann_transfer()`, `vis_viva_velocity()`, `plane_change_delta_v()`, `orbital_period()`
  - Two-impulse Hohmann transfer (delta-v + transfer time), vis-viva speed, simple plane change, Keplerian period
  - Validated against Curtis (LEO→GEO Example 6.1) and Vallado worked values; new `hohmann_leo_to_geo` regression benchmark
  - Tool count: 39 → 43 MCP tools

### Changed
- **`section_properties` validated for all 7 shapes** — cross-checked area/I/S against Roark closed forms, including the composite I-beam, C-channel, and T-section (centroid + parallel-axis); added `section_ibeam`/`section_tsection` benchmarks. No numerical discrepancy.
- **`column_buckling` validated against Euler-Johnson theory** — cross-checked both regimes vs independent formulas (Timoshenko; Shigley Eq. 4-46), plus the defining tangency invariant (Euler and Johnson meet at σcr=Sy/2 at the transition slenderness) and monotonicity/end-condition checks; added `column_buckling_euler` and `column_buckling_johnson` benchmarks. No discrepancy found.
- **`nozzle_performance` validated end-to-end** — cross-checked the composite tool (exit Mach, exit conditions, thrust, Cf, Isp, c*, choked mass flow) against an independent ideal 1-D implementation; added consistency/monotonicity/expansion-state tests and a `nozzle_ideal_expansion` regression benchmark. No discrepancy found.
- **Coverage gate now passes** — added a happy-path smoke test for all 50 computational MCP tools; `server.py` coverage 44% → 79%, total 77% → **82%**, so the `--cov-fail-under=80` CI gate is met (was failing)
- CI workflow improvements (matrix aligned to 3.11/3.12, lint/format over `tests/`, a build+clean-install `package` job) are prepared and pending a `workflow`-scoped push — see `docs/RELEASE_TODO.md`

### Security
- **Non-finite inputs are now rejected everywhere** — a shared `StrictModel` schema base sets `allow_inf_nan=False`, so NaN and ±inf fail validation on every tool with a structured `INVALID_PARAMETER` error naming the field (incl. nested fields like `cross_section.width`). Previously `inf` passed `gt=0` and propagated to an `inf` output (e.g. `rocket_delta_v`).
- **Hardened the workflow expression evaluator (`safe_eval`)** — it allowed unrestricted attribute access, leaving the classic sandbox-escape surface open (`x.__class__.__bases__[0].__subclasses__`, `__globals__`, and reaching the `_DotDict` internals). Now rejects any private/dunder attribute (name starting with `_`); public tool-output attributes still work. Added adversarial tests.

### Fixed
- **`section_properties` gave a cryptic error for a missing shape parameter** — e.g. an `ibeam` call without `flange_width` returned `INTERNAL_ERROR: 'flange_width'` (a bare KeyError). Now returns a structured `INVALID_PARAMETER` naming the missing parameter and listing all fields the shape requires; unknown shapes are likewise `INVALID_PARAMETER`.
- **Oblique shock returned the strong (non-physical) solution and mishandled detachment** — the θ–β–M bisection assumed monotonicity and converged on the strong root (e.g. β=79.8° instead of the physical weak β=45.3° at M1=2, θ=15°), and deflections beyond θ_max silently returned a no-shock result. Now returns the **weak** solution, computes θ_max, adds `solution`/`max_deflection_deg`/`normal_mach_upstream` keys, and raises a structured `INVALID_PARAMETER` error naming θ_max when the shock detaches. Validated vs Anderson Ch. 9 (θ_max = 22.97°/34.07° at M=2/3).
- **Normal-shock stagnation pressure ratio (p02/p01) was wrong** — returned values > 1 that grew with Mach (6.5, 28, 325, … at M=1.5, 2, 3) instead of the correct ≤ 1 decreasing loss. The isentropic total/static factors were inverted and combined with the wrong sign. Replaced with the closed-form NACA 1135 Eq. 100; now matches the table to < 0.01% across M = 1.5–5. Caught by new table-driven validation.
- **Rust kernels now compile** — the experimental `src/rust_kernels/` PyO3 crate failed `cargo check` (10 visibility errors + deprecated API); made all `#[pyfunction]`s public, moved to the PyO3 0.21 `Bound` module API, and added macOS linker config so it builds standalone. Documented that it is not part of the published wheel (added a crate README). Native-wheel packaging remains future work.
- **Structured-error contract** — all MCP tools now return one schema `{error, error_code, error_type, message, parameter, constraint, suggestion}`; invalid inputs are labelled `INVALID_PARAMETER` (not `INTERNAL_ERROR`) with the offending field surfaced
- **Validation benchmarks** — corrected six reference values that contradicted their cited sources (beam deflection/stress, turbulent skin friction, rocket delta-v, ISA 25 km, LEO velocity) and wired all benchmarks into the test suite as a regression gate

## [0.3.3] — 2026-06-10

### Added
- **Margin of Safety** — `margin_of_safety()`, `von_mises_stress()`, `combined_margin_of_safety()`, `deflection_margin()`
  - Stress-based and load-based MS calculations per FAA AC 25.571
  - Von Mises equivalent stress for combined loading states
  - Deflection limit checks (L/360, L/500, custom ratios)
- **Truss Analysis** — `truss_analysis()` for 2D/3D pin-jointed structures
  - Direct stiffness method with member forces, reactions, and displacements
  - Supports aircraft frames, spacecraft trusses, launch vehicle adapters
- **Validation Benchmarks** — `rocket_tools.validation` module with curated test cases
  - ISA atmosphere (NASA Standard Atmosphere 1976)
  - Beam deflections (Roark's Formulas)
  - Skin friction (Blasius correlations)
  - Rocket delta-v (Sutton & Biblarz)
  - Isentropic flow & normal shock (Anderson tables)
  - Orbital velocity (Vallado)
- **Material Source Citations** — All 49 materials now include primary source references
  - MIL-HDBK-5J / MMPDS-15 for metallic alloys
  - MIL-HDBK-17 for composites
  - Manufacturer datasheets for specialty materials
- **Module-level References** — Docstrings in all modules cite primary textbooks and standards
- **REFERENCES.md** — Central bibliography with 20+ cited sources

### Changed
- Tool count: 30 → 35 MCP tools
- README updated with new structural tools and agent manifest
- CONTRIBUTING.md updated with 265 tests

## [0.3.2] — 2026-06-10

### Added
- **Structural section properties** — 7 shapes: rectangle, hollow_rectangle, circle, hollow_circle, I-beam, C-channel, T-section
- **Column buckling** — Euler-Johnson transition with effective length factors for pinned, fixed, and free ends
- **Plate buckling coefficient** — compression, shear, and bending for simply-supported, clamped, and free-edge boundaries
- **Isentropic flow relations** — T/T0, P/P0, rho/rho0, A/A*, Mach angle
- **Normal shock relations** — downstream Mach, pressure/density/temperature ratios, stagnation pressure loss
- **Oblique shock relations** — weak shock solution for given deflection angle
- **Prandtl-Meyer expansion** — expansion angle from Mach, and Mach from angle
- **Aircraft aerodynamics** — lift curve slope (2D/3D, subsonic/supersonic), drag polar with compressibility drag, Breguet range/endurance, wing loading with stall speeds
- **Rocket nozzle performance** — thrust, Isp, Cf, exit conditions, expansion state (optimal/underexpanded/overexpanded)
- **Optimal area ratio** — nozzle A/A* for given chamber/ambient pressure ratio
- **Rocket delta-v** — Tsiolkovsky equation, multi-stage delta-v with per-stage breakdown
- **Orbital velocity** — circular and escape velocity, orbital period
- **Payload fraction** — mission feasibility check with required mass ratio
- **Thrust-to-weight ratio** — hover/climb capability assessment
- **Composite CG** — center of gravity and mass moments of inertia for multi-component bodies
- **Propellant tank sizing** — cylinder, sphere, ellipsoid with mass estimation
- Expanded tool count from 11 to 30 MCP tools
- All tools work for rockets, aircraft, drones, helicopters, and spacecraft

### Changed
- Pydantic schemas expanded for all new tools
- README updated with 30 tools and new capability categories

## [0.3.1] — 2026-06-10

### Added
- **Comprehensive materials library** — expanded from 5 to 49+ materials
  - 12 aluminum alloys (2024, 6061, 7075, 2219-T87, 2195, etc.)
  - 4 titanium alloys (Ti-6Al-4V, Ti-6Al-2Sn-4Zr-2Mo, etc.)
  - 10 steels (4130, 4340, 17-4PH, 300M, M50, 52100, etc.)
  - 8 nickel superalloys (Inconel-600/625/718/X750, Hastelloy-X, Waspaloy, Rene-41, Haynes-230)
  - 6 composites (Carbon-Epoxy T300/T700, Glass-Epoxy, Kevlar-49, Carbon-Carbon, Silica-Phenolic)
  - 5 refractory metals (Tungsten, Molybdenum, Rhenium, C18150, GlidCop-Al-25)
  - Specialty alloys (Beryllium-Copper, Magnesium-AZ31B, Copper-C11000)
- **Application-tagged materials** — filter by vehicle type: `rocket`, `drone`, `helicopter`, `aircraft`, `spacecraft`, `satellite`, `engine`
- `compare_materials()` — side-by-side trade study sorted by specific strength
- `search_materials()` — partial name search with application tags
- `list_materials(category)` — filter by material family or application

### Changed
- `asgi.py` version strings now use `__version__` dynamically
- README updated with current test count (182) and coverage (82%)

## [0.3.0] — 2026-06-10

### Added
- **Pydantic schemas** for all 11 tool inputs/outputs (`schemas/` module)
  - Discriminated unions for cross-section types (`RectangleSection | CircleSection`)
  - Field validators for physical constraints (altitude ≤25km, positive loads, etc.)
  - Auto-generated JSON schemas for LLM tool calling
- **Imperial unit support** with comprehensive aerospace conversions
  - Length: ft, in, yd, mi, nm
  - Pressure: psi, psf, ksi, atm, bar, torr
  - Force: lbf, kip, tonf
  - Speed: mph, fps, knots
  - Temperature: F, C, K, Rankine
  - `convert_to_si()` helper for automatic normalization
- **Safe expression evaluation** — replaced `eval()` in workflow engine with `ast`-based `safe_eval`
- **Structured errors** with `error_code`, `parameter`, `constraint`, `suggestion`
- **Health endpoints** — `/health`, `/ready`, `/metrics` (Prometheus) on ASGI app
- **Config management** — `pydantic-settings` with `ROCKET_*` env var prefix
- **Skills docs** — new `units.md` and `schemas.md` skills

### Changed
- Server validates all tool inputs via Pydantic before execution
- All hardcoded constants centralized in `config.py`
- Router uses configurable thresholds from settings
- `ValidationError` renamed to `ToolError` with structured `to_dict()` output

### Removed
- Broken Rust kernel build step from CI (kernels remain scaffolded, deferred)

### Fixed
- Security vulnerability: `eval()` in workflow interpolation
- `mypy` clean across all 34 source files

## [0.2.1] — 2026-06-10

### Added
- Human Engine labs attribution

## [0.2.0] — 2026-04-25

### Added
- Natural language router: intent classification + parameter extraction
- Phase 2 design specs and implementation plan (8 tasks)
- Skills library: `structural-analysis.md`, `aerodynamics.md`
- Comprehensive test suite (34 tests) and benchmarks (18 benchmarks)
- MCP server with 11 aerospace engineering tools

### Changed
- License: MIT → Apache-2.0
- Package structure and build system fixes

## [0.1.0] — 2026-04-19

### Added
- Core tools: structural, materials, aerodynamics, utilities
- Numba JIT acceleration for hot paths
- Rust kernel scaffold (PyO3)
- ISA atmosphere model (0–25,000 m)
- Material database (5 aerospace alloys)
