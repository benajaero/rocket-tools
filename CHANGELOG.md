# Changelog

All notable changes to rocket-tools.

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
