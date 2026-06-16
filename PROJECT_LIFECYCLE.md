# PROJECT_LIFECYCLE.md - rocket-tools weekly rhythm

This document describes a lightweight weekly maintenance rhythm. It is a guide for human or
automation-assisted development, not a promise that the repository is updated on every listed day.

| Day | Activity | Focus |
|-----|----------|-------|
| Monday | Planning & Priorities | Review open issues, pick 1-2 priorities for the week, update roadmap |
| Tuesday | Core Development | Library APIs, router behavior, workflows, or uncertainty propagation |
| Wednesday | Testing & Quality | Write tests for recent features, benchmark regressions, fix flaky tests |
| Thursday | Integration & Polish | MCP server smoke tests, skill cross-references, examples |
| Friday | Documentation & Skills | Write `.md` skills, update README, docstrings, worked examples |
| Saturday | Open Source & Community | Respond to issues, review PRs, write blog/forum posts |
| Sunday | Reflection & Cleanup | Review the week, tidy code, small refactors, set up Monday |

## Sunday: Reflection & Cleanup

- Review `git log` since last Sunday
- Check for TODO/FIXME comments in code
- Run full test suite + benchmarks
- Small refactors (naming, dead code, imports)
- Update `CHANGELOG.md` with user-facing changes
- Leave repo clean for Monday

## Release Preparation

- Confirm `README.md` examples match the installed package API
- Run the same validation commands as `.github/workflows/test.yml`
- Smoke test `rocket-tools serve` as an MCP stdio server from a client configuration
- Smoke test `uvicorn rocket_tools.asgi:app --host 127.0.0.1 --port 8000`
- Build package artifacts with `python -m build` and inspect them with
  `python -m twine check dist/*`
- Verify `CHANGELOG.md` has clear release notes and no inflated claims
- Tag only after package metadata, docs, tests, and examples agree on the release version

## Notes

- If a major feature is in flight, activity may shift; document the change in the relevant issue or
  release notes
- Prefer meaningful commits tied to code, docs, tests, or release preparation
