# PROJECT_LIFECYCLE.md — rocket-tools weekly rhythm

Automated by cron. Each day has a theme to keep momentum without grinding.

| Day | Activity | Focus |
|-----|----------|-------|
| Monday | Planning & Priorities | Review Phase 2 tasks, pick 1–2 for the week, update roadmap |
| Tuesday | Core Development | Natural language router, composable workflows, or uncertainty propagation |
| Wednesday | Testing & Quality | Write tests for recent features, benchmark regressions, fix flaky tests |
| Thursday | Integration & Polish | MCP server polish, skill cross-references, example notebooks |
| Friday | Documentation & Skills | Write `.md` skills, update README, docstrings, worked examples |
| Saturday | Open Source & Community | Respond to issues, review PRs, write blog/forum posts |
| Sunday | Reflection & Cleanup | Review the week, tidy code, small refactors, set up Monday |

## Sunday: Reflection & Cleanup

- Review `git log` since last Sunday
- Check for TODO/FIXME comments in code
- Run full test suite + benchmarks
- Small refactors (naming, dead code, imports)
- Update `CHANGELOG.md` or `memory/` with week summary
- Leave repo clean for Monday

## Notes

- If a major feature is in flight, activity may shift — that's fine, document it
- Always commit with timestamp: `YYYY-MM-DD rocket-tools: [activity] — automated lifecycle`
- Push even if no code changes (shows the heartbeat)
