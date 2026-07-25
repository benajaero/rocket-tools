---
name: add-tool
description: Add a new validated MCP tool to rocket-tools following the repo's 7-point integration pattern. Use when adding any new computational tool (a function that returns a flat dict of numbers).
---

# Add a new tool

Every computational tool touches the same set of files. Do all of them, in order, or a
guard test will fail. A tool is not done until it is validated against a reference value
and the full check gauntlet is green.

## Before writing code

Pick a tool that is **bounded and validatable**. You must be able to pin it to a textbook
worked example or an exact hand computation. If you cannot check the number against a known
answer, do not add the tool. A plausible-but-unverified tool is the exact thing this repo
exists to avoid.

## The seven points

1. **Domain function.** Write it in the right module under `src/rocket_tools/<domain>/`
   (`structural/`, `aerodynamics/`, `design/`, `trajectory/`, `materials/`). It takes SI
   inputs, returns a **flat dict of rounded scalars**, and validates every input, raising
   `ValueError` with a clear message on anything out of envelope. Cast numpy scalars and
   booleans to Python types (`float(...)`, `bool(...)`) so the dict is JSON-safe and mypy is
   happy.

2. **Export it.** Add the function name to that package's `__init__.py` import and `__all__`.
   Packages `aerodynamics`, `structural`, `design`, `materials` are auto-registered into the
   workflow/sweep dispatch registry, so a flat-scalar tool composes for free. A tool that
   returns arrays, images, or nested dicts must be kept OUT of that registry and added to
   both guard sets (`META_TOOLS` in `tests/test_provenance.py` and the `meta` set in
   `tests/test_all_tools_happy_path.py`).

3. **Input schema.** Add a `<Name>Input(StrictModel)` in `src/rocket_tools/schemas/<domain>.py`
   with `Field(...)` constraints (`gt`, `ge`, `le`, `min_length`, `Literal`). `StrictModel`
   already rejects NaN and infinity. Re-export it from `src/rocket_tools/schemas/__init__.py`
   (both the `from .<domain> import` block and `__all__`), keeping isort order.

4. **Server wrapper.** Add an `@mcp.tool()` function in `src/rocket_tools/server.py`:
   validate the inputs through the schema, call the domain function (imported locally inside
   the wrapper), and wrap every exception with `_format_error(e)`. Add the schema import at
   the top (isort order). A `Literal` string param passed to the schema needs
   `# type: ignore[arg-type]` on that argument, matching the existing tools.

5. **Provenance.** Add an entry to `_PROVENANCE` in `src/rocket_tools/provenance.py`, keyed
   by the exact tool name, with `domain`, `references` (a real citation), `formula`, and
   `assumptions`. A test asserts every registered tool has one.

6. **Happy-path call.** Add a valid input to `VALID_CALLS` in
   `tests/test_all_tools_happy_path.py`. A guard test asserts every computational tool has
   one.

7. **Curated benchmark (when there is a textbook value).** Add an entry to `_BENCHMARKS` in
   `src/rocket_tools/validation/benchmarks.py` with the published inputs, expected outputs,
   a tolerance, and a reference string. It runs through the live tool automatically.

## Pin it with a test

Write `tests/test_<name>.py`. Include:
- a case pinned to a hand-computed or textbook value,
- an invariant or round-trip check where one exists,
- parametrized reject cases proving the validation raises.

## Update the counts

Adding a tool raises the surface, so bump every place that counts it:
- `README.md`: the `N MCP Tools` line, `exposes N tools`, and the tests badge.
- `tests/test_packaging.py`: the `assert len(tools) >= N` floor.
- `scripts/verify_release.sh`: the `assert len(tools) >= N` and its message.
- `CHANGELOG.md`: add a bullet under `[Unreleased]`.
- If a domain gained its first tool of a kind, add it to `FEATURES.md`.

## Verify and commit

Run the `verify` skill (full gauntlet + optional clean-room build). Only when it is all
green, commit and push. Commit as the user with no AI attribution trailers.
