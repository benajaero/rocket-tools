# Changelog

All notable changes to rocket-tools.

## [Unreleased]

### Added
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
- **Coverage gate now passes** — added a happy-path smoke test for all 50 computational MCP tools; `server.py` coverage 44% → 79%, total 77% → **82%**, so the `--cov-fail-under=80` CI gate is met (was failing)
- CI workflow improvements (matrix aligned to 3.11/3.12, lint/format over `tests/`, a build+clean-install `package` job) are prepared and pending a `workflow`-scoped push — see `docs/RELEASE_TODO.md`

### Security
- **Non-finite inputs are now rejected everywhere** — a shared `StrictModel` schema base sets `allow_inf_nan=False`, so NaN and ±inf fail validation on every tool with a structured `INVALID_PARAMETER` error naming the field (incl. nested fields like `cross_section.width`). Previously `inf` passed `gt=0` and propagated to an `inf` output (e.g. `rocket_delta_v`).
- **Hardened the workflow expression evaluator (`safe_eval`)** — it allowed unrestricted attribute access, leaving the classic sandbox-escape surface open (`x.__class__.__bases__[0].__subclasses__`, `__globals__`, and reaching the `_DotDict` internals). Now rejects any private/dunder attribute (name starting with `_`); public tool-output attributes still work. Added adversarial tests.

### Fixed
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
