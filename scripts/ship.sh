#!/usr/bin/env bash
# ship.sh — the rocket-tools update/release pipeline.
#
# One command for the routine loop (verify -> commit -> merge -> push) and for a
# full release (version bump -> clean-room build -> tag -> PyPI -> site deploy),
# with the tool/test/benchmark counts derived from the code so nothing drifts.
#
# Usage:
#   scripts/ship.sh check                 # full local gauntlet only
#   scripts/ship.sh counts                # print live tool/test/benchmark counts
#   scripts/ship.sh merge [BRANCH]        # gauntlet, then ff-merge BRANCH (default: current) into main and push
#   scripts/ship.sh release X.Y.Z         # bump, changelog, verify, commit, tag, push, wait for PyPI
#   scripts/ship.sh site                  # sync counts into the marketing site, build, and deploy
#   scripts/ship.sh ship X.Y.Z            # release + site in one shot
#
# Env:
#   SITE_DIR   path to the Human Engine site repo (default: ~/Code/human-engine/site)
#   DRY_RUN=1  print the mutating git/deploy commands instead of running them
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PY="$ROOT/.venv/bin/python"
SITE_DIR="${SITE_DIR:-$HOME/Code/human-engine/site}"

say() { printf '\033[1;36m==> %s\033[0m\n' "$*"; }
run() { if [[ "${DRY_RUN:-0}" == "1" ]]; then printf '   [dry-run] %s\n' "$*"; else eval "$@"; fi; }
die() { printf '\033[1;31merror: %s\033[0m\n' "$*" >&2; exit 1; }

# ---- the local quality gate; nothing ships red ----
check() {
  say "pytest"
  "$ROOT/.venv/bin/pytest" -q
  say "ruff check"
  "$ROOT/.venv/bin/ruff" check src/ tests/
  say "ruff format --check"
  "$ROOT/.venv/bin/ruff" format --check src/ tests/
  say "mypy"
  "$ROOT/.venv/bin/mypy" src/
  say "gauntlet passed"
}

# ---- live counts, straight from the code (single source of truth) ----
counts() {
  NUMBA_DISABLE_JIT=1 "$PY" - <<'PY'
import asyncio
from rocket_tools.server import mcp
from rocket_tools.validation.benchmarks import _BENCHMARKS

tools = len(asyncio.run(mcp.list_tools()))
benches = len(_BENCHMARKS)
print(f"TOOLS={tools}")
print(f"BENCHMARKS={benches}")
PY
  # test count comes from pytest collection so it never guesses
  local n
  n="$("$ROOT/.venv/bin/pytest" -q --collect-only 2>/dev/null | grep -cE '::')" || true
  printf 'TESTS=%s\n' "$n"
}

# ---- ff-merge the working branch into main and push ----
merge() {
  local branch="${1:-$(git branch --show-current)}"
  [[ "$branch" == "main" ]] && die "already on main; nothing to merge"
  check
  say "fast-forward $branch -> main"
  run "git checkout main"
  run "git merge --ff-only '$branch'"
  run "git push origin main"
  run "git checkout '$branch'"
  say "merged and pushed"
}

# ---- cut a release: bump, verify, tag, push, wait for PyPI ----
release() {
  local ver="${1:-}"
  [[ "$ver" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || die "usage: ship.sh release X.Y.Z"
  local today
  today="$("$PY" -c 'import datetime,os; print(os.environ.get("SHIP_DATE") or datetime.date.today().isoformat())')"

  say "bump version to $ver in pyproject / __init__ / CITATION"
  run "$PY scripts/_bump_version.py '$ver' '$today'"

  grep -q "\[$ver\]" CHANGELOG.md || die "CHANGELOG has no [$ver] section — finalize it first (see release skill)"

  say "clean-room build gate"
  PATH="$ROOT/.venv/bin:$PATH" bash scripts/verify_release.sh
  run "rm -rf dist build src/rocket_tools.egg-info"

  say "commit, tag, push"
  run "git add -A"
  run "git commit -m 'release: $ver'"
  run "git push origin main"
  run "git tag -a 'v$ver' -m 'rocket-tools $ver'"
  run "git push origin 'v$ver'"

  say "waiting for PyPI to publish $ver (Trusted Publishing via tag)"
  for _ in $(seq 1 30); do
    code="$(curl -s -o /dev/null -w '%{http_code}' "https://pypi.org/pypi/rocket-tools/$ver/json")"
    [[ "$code" == "200" ]] && { say "PyPI $ver is live"; return 0; }
    sleep 10
  done
  die "PyPI $ver not visible after 5 min — check 'gh run list'"
}

# ---- sync counts into the marketing site, build, deploy ----
site() {
  [[ -d "$SITE_DIR" ]] || die "site repo not found at $SITE_DIR (set SITE_DIR)"
  eval "$(counts)"
  local ver
  ver="$("$PY" -c 'import rocket_tools; print(rocket_tools.__version__)')"
  say "syncing site to $TOOLS tools / $TESTS tests / $BENCHMARKS benchmarks (v$ver)"
  run "TOOLS=$TOOLS TESTS=$TESTS BENCHMARKS=$BENCHMARKS SITE_DIR='$SITE_DIR' $PY scripts/_sync_site.py"
  say "build:static"
  run "(cd '$SITE_DIR' && npm run build:static)"
  say "deploy (S3 + CloudFront invalidation)"
  run "(cd '$SITE_DIR/..' && bash _ops/deploy-static-site.sh www site/dist)"
  say "site deployed — verify https://www.humanengine.co/rocket-tools"
}

cmd="${1:-check}"; shift || true
case "$cmd" in
  check)   check ;;
  counts)  counts ;;
  merge)   merge "$@" ;;
  release) release "$@" ;;
  site)    site ;;
  ship)    release "$@"; site ;;
  *)       die "unknown command '$cmd' (check|counts|merge|release|site|ship)" ;;
esac
