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

- [ ] **P0 — Curated validation benchmarks have WRONG expected values and are never run.**
  `src/rocket_tools/validation/benchmarks.py` is at 0% test coverage. When executed against
  the actual tools, 3 of 13 fail — and in every case the **tool is correct and the benchmark
  `expected` is wrong**:
  - `beam_simply_supported_point`: expected δ=0.004 m / σ=120 MPa; correct (Roark PL³/48EI,
    PL/4·c/I for P=1000 N, L=2 m, E=200 GPa, 50×10 mm rect) is **δ=0.2 m / σ=600 MPa** (tool value).
  - `beam_cantilever_point`: expected δ=0.02274 m; correct (PL³/3EI) is **δ=4.777 m** (tool value).
    Also revisit `load_type="point_midspan"` semantics on a `cantilever` support.
  - `skin_friction_turbulent`: expected 0.00297; the reference string's own arithmetic
    `0.0592/(1e7)^0.2` actually equals **0.002357** (tool value). 0.00297 is the 0.074/Re^0.2
    *average-plate* coefficient mislabelled as local cf.
  Fix: recompute every `expected` from the cited formula/table, correct the reference strings,
  then wire ALL benchmarks into pytest as a hard regression gate (see Testing P0). Cross-check
  each against its stated source (Roark, Blasius, Anderson, Sutton, NASA-TM-X-74335, Vallado).
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
- [ ] **P1 — Structured-error contract consistency.** `_format_error` emits
  `{error, error_code, message, parameter, constraint, suggestion}` but `ToolError.to_dict()`
  emits `{error_type, ...}` (test_utils asserts `error_type`). Unify one error schema across
  every tool and document it so an LLM can branch on it. Add a test asserting the shape.
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

- [ ] **P0 — Wire curated benchmarks into pytest** (`tests/test_validation_benchmarks.py`),
  parametrised over `list_benchmarks()`, asserting each tool output is within tolerance of the
  (corrected) expected value. This makes references a real regression gate. Depends on Correctness P0.
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

## Discovered / notes (append as we go)

- `srv` tool for skin friction is not named `skin_friction` at module scope — confirm the
  registered MCP name maps cleanly for the benchmark runner.
- CI at `.github/workflows/test.yml` exists (673 B) — needs reading; ensure it runs the new
  benchmark gate, the clean-room install, and matches release-checklist commands.
