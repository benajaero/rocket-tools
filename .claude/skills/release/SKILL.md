---
name: release
description: Cut a rocket-tools release and publish to PyPI. Use only when the maintainer has explicitly asked to release or to update PyPI. Publishing is irreversible.
---

# Release

PyPI updates only when a new version is published, so "update PyPI" means cutting a release.
Do this only on explicit maintainer go-ahead. The version tag triggers GitHub Actions
Trusted Publishing (OIDC), so there is no token to handle, and the push is irreversible.

## Version to pick

Follow semver against the last tag. New tools and features since the last release are a
minor bump (`0.5.0` to `0.6.0`); a fix-only release is a patch bump. Check the last tag with
`git tag | tail`.

## Steps

1. **Bump the version in all three places** (they must agree, a test enforces it):
   - `pyproject.toml` -> `version = "X.Y.Z"`
   - `src/rocket_tools/__init__.py` -> `__version__ = "X.Y.Z"`
   - `CITATION.cff` -> `version: "X.Y.Z"` (and `date-released` to today)

2. **Finalize the changelog.** In `CHANGELOG.md`, rename the `[Unreleased]` heading to
   `[X.Y.Z] — <today>` and open a fresh empty `[Unreleased]` above it. Confirm the notes are
   accurate and free of inflated claims.

3. **Verify.** Run the `verify` skill including the clean-room build. The build must print
   `OK: rocket-tools X.Y.Z - <N> tools`. Remove the `dist/` and `build/` artifacts after.

4. **Commit and push** the version bump to `main`.

5. **Tag and push the tag** on that commit:
   ```bash
   git tag -a vX.Y.Z -m "rocket-tools X.Y.Z" <commit>
   git push origin vX.Y.Z
   ```
   The `v*` tag triggers `.github/workflows/workflow.yml` (environment `pypi`).

6. **Confirm the publish.** Check the run with `gh run list`, then verify PyPI:
   ```bash
   curl -s -o /dev/null -w "%{http_code}\n" https://pypi.org/pypi/rocket-tools/X.Y.Z/json
   ```
   A `200` means the version is live. The aggregate `info.version` in the JSON can lag by a
   minute behind Fastly's cache; the per-version endpoint is authoritative.

## After the release

If the marketing site should reflect the release, follow the site-deploy notes in the
project memory (`human-engine-site-rocket-tools`): update the counts and add a release
entry, then build and deploy. Do not touch DNS.
