# rocket-tools — Release Backlog (path to a confident 1.0)

Prioritised, checkbox backlog of everything between the current state (`0.3.3`) and a
confident public 1.0 on PyPI + the MCP registry. Ordered within each group by impact.
Do NOT publish without explicit approval — prep to that line and stop.

**Baseline captured 2026-07-20** (Python 3.12.13, venv):
- Tests: **293 passed**, 28 warnings, ~4 s. (README badge says 240 — stale.)
- Coverage: **75%** total. (README badge says 82% — stale.)
- `ruff check`: clean. `ruff format --check`: clean. `mypy src/`: clean (49 files).
- `@mcp.tool()` count in `server.py`: **39**. (README/CHANGELOG say 35 — stale.)
- Build backend: setuptools → `py3-none-any` wheel (pure Python). `src/rust_kernels/`
  exists but is **not built, not imported, not shipped**.

---

## Correctness (numbers must be correct, not just plausible)

- [x] **P0 — Curated validation benchmarks had WRONG expected values and were never run.**
  *(Done 2026-07-20, branch `release-hardening`.)* `benchmarks.py` was at 0% coverage; 3 of 13
  failed when run and in every case the **tool was correct and the benchmark `expected` was
  wrong**. Every value re-derived from its cited source and corrected:
  - `beam_simply_supported_point`: 0.004 m / 120 MPa → **0.2 m / 600 MPa** (Roark PL³/48EI, PL/4·c/I).
  - `beam_cantilever_point`: 0.02274 m / 131.8 MPa → **4.7767 m / 1757.8 MPa** (PL³/3EI, PL·c/I).
  - `skin_friction_turbulent`: 0.00297 → **0.002357** (0.0592/(1e7)^0.2; 0.00297 was the
    0.074/Re^0.2 average-plate coeff mislabelled as local cf — reference string arithmetic was wrong).
  - `rocket_delta_v_standard`: 5068 → **5050.62 m/s** (320·9.80665·ln 5; reference arithmetic was wrong).
  - `isa_25000m`: T 221.55→**221.65 K**, P 2481→**2511 Pa** (US Std Atm 1976, 20–32 km layer); tightened tol 0.02→0.01.
  - `orbital_velocity_leo`: 7.669 km/s / 92.6 min → **7.6726 / 92.41** (matches the reference's own r=6771 km, mean radius).
  All reference strings corrected to show the true arithmetic. Verified: `mypy` clean, tool
  outputs now match every corrected value.
- [ ] **P1 — Independent re-derivation of every physics tool** against its cited source, one
  module per iteration, with the reference value pinned in a test. Priority order by coverage
  gap: `compressible.py` (51%), `sections.py` (53%), `nozzle.py` (66%), `buckling.py` (68%),
  `beams.py` (71%), `aircraft.py` (75%), `fundamentals.py` (77%).
- [ ] **P2 — Verify oblique-shock (β–θ–M) and Prandtl-Meyer** against Anderson Appendix tables
  at 2–3 Mach/angle points each; pin as benchmarks.
- [ ] **P2 — Verify normal-shock p0₂/p0₁, ρ₂/ρ₁, T₂/T₁** at M=2,3,5 against Anderson App. A.
- [ ] **P2 — Verify ISA at 0/11/20/25 km** density & speed-of-sound to full table precision
  (current tolerance 0.01–0.02 is loose enough to hide small errors).
- [ ] **P3 — Materials spot-check**: sample 5–10 alloys' yield/modulus/density vs MMPDS-15 /
  MIL-HDBK-5J and record the exact table/section in `REFERENCES.md`.
- [ ] **P3 — Audit unit-conversion constants** in `utils/units.py` against NIST SP 811
  (in→m, psi→Pa, lbf→N, knot→m/s, °R, etc.); pin each as an exact-value test.

## MCP quality (an agent must call each tool correctly from the schema alone)

- [ ] **P1 — Tool docstrings/schemas audit.** Every `@mcp.tool()` needs: units on every
  parameter and return key, valid enum/range in the description, and a one-line "returns" that
  names the structured output keys. Spot-checked `unit_convert` lists units but not directions;
  several tools rely on Pydantic schema alone. Make descriptions self-sufficient.
- [x] **P1 — Structured-error contract consistency.** *(Done 2026-07-20.)* All tools now return
  one schema — `{error, error_code, error_type, message, parameter, constraint, suggestion}`.
  `_format_error` gained the missing `error_type` on the internal branch, and a new
  `_format_pydantic_error` maps Pydantic `ValidationError` to a clean **`INVALID_PARAMETER`**
  (was mislabelled `INTERNAL_ERROR`) with the offending field name in `parameter` and the
  constraint surfaced — instead of a raw multi-line Pydantic dump. Added `TestServerErrorContract`
  (4 tests, through `mcp.call_tool`). `server.py` coverage 32% → 44%; suite 307 → 311.
  Discovered: FastMCP rejects **gross type mismatches** (e.g. a string for a float) at the
  protocol boundary before our handler, so our contract governs semantically-invalid but
  correctly-typed inputs (negative/out-of-range/bad-enum) — the realistic agent mistake.
- [ ] **P2 — Reconcile tool count.** 39 registered vs "35" in README/CHANGELOG/skills. Fix docs
  and add a test that asserts `len(registered tools) == documented count`.
- [ ] **P2 — Return-value schemas.** Consider Pydantic *output* models (not just inputs) so the
  MCP tool advertises its response shape; at minimum, document return keys per tool.
- [ ] **P3 — Router coverage.** `router/extractors.py` at 81% with many uncovered branches;
  ensure NL router returns a clear "could not parse" structured result, tested.

## Packaging / Release

- [ ] **P0 — Decide the Rust-kernel story.** `src/rust_kernels/` (Cargo, isa/beams/aerodynamics)
  is not built by the setuptools backend, not imported anywhere, and absent from the wheel, yet
  the task brief lists "wheels incl. Rust kernels". Choose ONE and execute:
  (a) wire a maturin/PyO3 build with a **pure-Python fallback** and cibuildwheel matrix, or
  (b) remove the crate and drop Rust from the narrative. README currently credits Numba, not Rust.
  Whichever: the shipped wheel's accel path must match the docs.
- [ ] **P1 — Reproducible clean-room install test** (from release-checklist) run in CI: build,
  `twine check`, install the wheel in a fresh venv, import + smoke-run. Currently only manual.
- [ ] **P1 — Version single-sourcing.** Assert `pyproject.version == rocket_tools.__version__`
  in a test so they can never drift.
- [ ] **P1 — `Development Status :: 3 - Alpha` → `4 - Beta`/`5 - Production` for 1.0**; confirm
  every classifier and the `requires-python = ">=3.11,<3.13"` cap (numba 0.65 supports 3.13 —
  re-check whether the upper cap is still needed).
- [ ] **P2 — PyPI metadata polish:** long-description renders, project URLs resolve, `Homepage`
  vs `Repository` (github.com/benajaero) consistent, add `Documentation` URL, verify LICENSE +
  `license-files` produce correct metadata.
- [ ] **P2 — MCP registry publish prep:** `server.json` / registry manifest, tool list, and the
  stdio launch command (`rocket-tools serve`) validated against the registry schema.
- [ ] **P2 — Pin/verify runtime dep floors** actually work (`mcp>=1.0`, `numba>=0.58`,
  `numpy>=1.24`) — CI matrix on min and latest.
- [ ] **P3 — Dockerfile** builds and runs the SSE server; add to CI.

## Testing

- [x] **P0 — Wire curated benchmarks into pytest.** *(Done 2026-07-20.)*
  `tests/test_validation_benchmarks.py` parametrises over `list_benchmarks()`, runs each case
  through the actual MCP server tool, and asserts the output is within tolerance of the corrected
  reference value; plus a check that every benchmark has a non-empty reference and positive
  tolerance. Suite: 293 → **307 passing**. `validation/benchmarks.py` coverage 0% → 72%.
- [ ] **P1 — Raise `server.py` coverage (32%).** The MCP tool layer — the actual product
  surface — is barely exercised. Add tests calling each tool with valid input AND with invalid
  input asserting the structured-error shape.
- [ ] **P1 — `validation/benchmarks.py` and `validation/__init__.py` at 0%** — covered by the
  Testing P0 item; keep `--cov-fail-under` honest.
- [ ] **P2 — Property-based tests (hypothesis)** for invariants: isentropic ratios ≤ 1 and
  monotonic in M; shock entropy increases (p0₂≤p0₁); beam δ scales as L³ and 1/I; ΔV monotonic
  in mass ratio; unit round-trips (x→other→x) within float tolerance.
- [ ] **P2 — Benchmarks as regression gates.** `tests/bench_*.py` exist; decide perf budgets and
  fail CI on regressions (or explicitly mark benches informational). README claims "<1 ms" and
  "~54 ns" — pin those with a benchmark assertion or soften the claim.
- [ ] **P2 — Raise `--cov-fail-under`** from 80 toward real coverage once server.py is tested;
  update the README badge to the true number.
- [ ] **P3 — Investigate the 28 test warnings**; resolve or explicitly filter with justification.

## Docs / DX

- [ ] **P1 — Fix stale README badges/claims:** 240→293 tests, 82%→75% coverage (or raise
  coverage first), 35→39 tools. Every headline number must match a command output.
- [ ] **P2 — CHANGELOG `[Unreleased]` section** + prepare 1.0 notes; ensure the tool count and
  feature list match reality.
- [ ] **P2 — Verify every README code example runs** against the current API (add a doctest or
  an examples smoke test in CI).
- [ ] **P2 — Skills library (`skills/*.md`) cross-check** tool names, signatures, and return
  keys against `server.py`; stale names mislead agents.
- [ ] **P3 — `docs/scientific-validity.md`** — reconcile with the corrected benchmarks and state
  the validation scope + known limitations plainly (not certified aerospace software).

## Security / Robustness

- [ ] **P1 — Audit `utils/safe_eval.py`** (used by the router / workflow expressions). Confirm
  the AST allow-list rejects attribute access, dunders, calls to arbitrary builtins, and
  resource-exhaustion inputs; add adversarial tests.
- [ ] **P2 — Input hardening at tool boundary:** NaN/inf, negative/zero where physical,
  extreme magnitudes → structured errors, never crashes or silent NaNs. Systematic test.
- [ ] **P2 — ASGI server hardening:** request size limits, error handling on `/`, `/health`,
  `/ready`, `/metrics`; confirm no stack traces leak to clients.
- [ ] **P3 — Dependency/security scan** (`pip-audit`) in CI; document the security policy vs
  `SECURITY.md`.

---

## Feature expansion (user-requested: "add features, make it comprehensive")

Build one fully-verified module per iteration, validated against authoritative sources.

- [x] **Orbital mechanics** *(Done 2026-07-20.)* `design/orbital.py`: `hohmann_transfer`,
  `vis_viva_velocity`, `plane_change_delta_v`, `orbital_period` (+4 MCP tools → 43 total).
  Validated vs Curtis Ex. 6.1 (LEO→GEO ΔV 2.426/1.467, total 3.893 km/s, 5.275 h) and Vallado;
  added `hohmann_leo_to_geo` regression benchmark. 10 new tests; suite → 321.
- [x] **Full ISA to 86 km** *(Done 2026-07-20.)* Rewrote `materials/isa.py` as the complete
  7-layer US Std Atm 1976 (analytic + `lru_cache`, dropped the fragile 1-m index interpolation).
  Range 0–84,852 m geopotential (86 km geometric); matches NASA-TM-X-74335 Table 1 to <0.02% at
  every layer boundary. Added sig-fig output (sub-Pa pressures survive), `isa_47000m`/`isa_71000m`
  benchmarks, and stratopause/mesosphere/ceiling tests. Schema range 25 km → 84,852 m; suite → 327.
  Note: input is **geopotential** altitude (ISO 2533 convention) — documented in tool + docstring.
- [x] **Aerothermodynamics** *(Done 2026-07-20.)* New `aerodynamics/aerothermo.py`:
  `stagnation_temperature`, `recovery_temperature`, `sutton_graves_heat_flux`,
  `ballistic_entry_peak_deceleration` (+4 MCP tools → 47). Validated vs Anderson (T0=616 K at
  M=3), Sutton-Graves NASA TR R-376 (constant 1.7415e-4 → W/m², unit interpretation confirmed by
  cross-check), Allen-Eggers NACA TR 1381 (a_max=79.7 g, V_peak=V_e/√e). 17 tests + 2 benchmarks;
  suite → 343. Also refined README (badges 240→343 tests, 82%→77%, 35→47 tools; new capability rows).
- [ ] **Propulsion depth** — combustion c*, real-gas nozzle corrections, throttling, staging
  optimizer. Cite Sutton & Biblarz, Hill & Peterson.

## Discovered / notes (append as we go)

- `srv` tool for skin friction is not named `skin_friction` at module scope — confirm the
  registered MCP name maps cleanly for the benchmark runner.
- CI at `.github/workflows/test.yml` exists (673 B) — needs reading; ensure it runs the new
  benchmark gate, the clean-room install, and matches release-checklist commands.
- **Semantic wart (add to MCP quality):** `beam_analysis(load_type="point_midspan",
  support_type="cantilever")` computes the *end-load* cantilever result (PL³/3EI), not a
  mid-span load. Either add a dedicated `point_end` load type or document that a cantilever
  point load is applied at the tip — an agent reading the schema would expect mid-span.
- `orbital_velocity` uses **mean Earth radius 6371 km** (r=6771 km at 400 km alt), not the
  equatorial 6378 km. Fine and consistent, but document the constant so results are reproducible.
- ISA tool at 25 km now matches US Std Atm 1976 to <0.5%; the 0/11 km cases are exact. Consider
  tightening the remaining ISA tolerances (Correctness P2) now that the tool is trustworthy.
- **Follow-up (MCP quality):** `unit_convert` with an unknown unit raises a plain `ValueError`
  in the units module → still surfaces as `INTERNAL_ERROR`. Make the units module raise
  `ToolError`/`INVALID_PARAMETER` for unknown units so bad-unit calls are actionable too.
- `server.py` still 44% — the happy-path of most tools is untested. Next Testing pass: call each
  tool with valid input through `mcp.call_tool` and assert key outputs (raises coverage + guards
  the response-key contract the skills docs promise).
