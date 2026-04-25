# Changelog

All notable changes to rocket-tools.

## [Unreleased]

### Added
- `PROJECT_LIFECYCLE.md` — weekly activity rhythm for automated development

### Changed
- Code style: applied `ruff` formatting across `src/` and `tests/`
- Fixed ambiguous variable names (`l` → `char_length`, `beam_length`) in `aerodynamics/fundamentals.py` and `structural/beams.py`
- Wrapped long docstrings and comments to stay within 100-character line limit
- Cleaned up unused imports in `utils/validation.py` and benchmark files

### Fixed
- Import sorting in `__init__.py` files (I001 ruff rule)

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

