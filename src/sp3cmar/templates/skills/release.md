---
description: Drive engram's scripts/release.sh end-to-end — version bump, release PR, tag
---

Cut an engram release. Validate the working state, pick the next version, run `scripts/release.sh`, open the `staging` → `main` release PR with the CHANGELOG delta as its body, and after merge tag the release on `main`. HALT on any failure — never proceed past a failed step.

This skill is engram-specific: it assumes engram's repo layout (`scripts/release.sh`, `backend/pyproject.toml`, `CHANGELOG.md` at the repo root) and the `staging` → `main` merge-commit workflow.

## Arguments

`$ARGUMENTS` controls behavior:
- *(empty)* — read the current version and prompt for the next semver
- `--patch` — bump the patch component (default suggestion)
- `--minor` — bump the minor component
- `--major` — bump the major component
- `--dry-run` — print every planned action without executing (no `release.sh`, no PR, no tag)

## Steps

### 1. Confirm the repo

- Confirm the working directory is engram's repo root: `scripts/release.sh` and `backend/pyproject.toml` must both exist.
- If either is missing, STOP — this skill only drives engram releases. Warn the user and ask them to re-run from engram's repo root.

### 2. Pre-flight validation (HALT on failure)

- Run `git status --porcelain`. If it prints anything, the working tree is dirty — STOP and list the dirty files. A release must run from a clean tree.
- Run `git rev-parse --abbrev-ref HEAD`. If the current branch is not `staging`, STOP. Releases are cut from `staging` only.
- Run `git fetch origin` and confirm `staging` is up to date with `origin/staging` (`git rev-list --left-right --count origin/staging...staging`). If `staging` is behind, STOP and tell the user to pull first.

### 3. Determine the next version

- Read the current version from `backend/pyproject.toml` (the canonical source — the `[project]` `version` field).
- Compute the three candidate bumps from the current `MAJOR.MINOR.PATCH`:
  - `--patch` → `MAJOR.MINOR.(PATCH+1)`
  - `--minor` → `MAJOR.(MINOR+1).0`
  - `--major` → `(MAJOR+1).0.0`
- If an explicit `--patch`/`--minor`/`--major` flag was passed, use that bump.
- Otherwise prompt the user: show the current version and the three candidates, defaulting the suggestion to patch. Let the user confirm or type an exact version.
- Validate the chosen version is a clean semver string greater than the current version. If not, STOP and re-prompt.

### 4. Preview the CHANGELOG delta

- Read `CHANGELOG.md` at the repo root.
- Extract the `[Unreleased]` section — these are the entries this release will publish.
- Show the delta to the user so they can sanity-check what is shipping. If `[Unreleased]` is empty, warn and confirm the user still wants to release before proceeding.
- Save this delta — it becomes the release PR body in Step 6.

### 5. Run the release script (HALT on failure)

- If `--dry-run`: print `scripts/release.sh <new-version>` and the rest of the planned actions, then STOP. Do not execute.
- Otherwise run `scripts/release.sh <new-version>` and stream its full output to the user.
- Check the exit code. If non-zero, STOP immediately, surface the script's output, and do NOT attempt to open a PR or tag. Releases are partially-applied otherwise.
- `release.sh` is the single source of truth for the version bump and CHANGELOG roll (it dates the `[Unreleased]` heading and bumps `backend/pyproject.toml`). Do not duplicate that work by hand — let the script own it.

### 6. Open the release PR (HALT on failure)

- The release script commits the version bump on a release branch (or on `staging` per engram's convention — inspect `release.sh` output to confirm the source branch). Push that branch.
- Open the release PR with `gh pr create --base main --head staging`:
  - Title: `chore(release): <new-version>`
  - Body: the CHANGELOG delta captured in Step 4, under a short summary line (e.g. `Release <new-version>.`). Use `Closes`/`Fixes` only for issues this release explicitly resolves — a release PR usually links none.
- Output the PR URL. If `gh pr create` fails (e.g. a release PR already exists), STOP and surface the error.

### 7. Wait for merge, then tag (HALT on failure)

- Tagging happens on `main` AFTER the release PR merges — never before. Do not tag a commit that has not landed on `main`.
- Poll the PR state with `gh pr view <number> --json state,mergedAt` until it reports `MERGED`. Surface progress to the user; allow them to abort the wait (the tag step can be re-run later).
- After merge:
  - `git fetch origin` and `git checkout main && git pull --ff-only origin main`.
  - Create an annotated tag: `git tag -a v<new-version> -m "Release <new-version>"` on the merge commit.
  - Push it: `git push origin v<new-version>`.
- Confirm the tag is on the remote (`git ls-remote --tags origin v<new-version>`). If the push failed, STOP and surface the error.

### 8. Associate shipped issues with the release (HALT on failure)

With the tag on `main`, set the project `Release` field on every issue that shipped in this release, so the board shows which version carried each issue. This is the single source of truth for Release association (there is no GitHub Actions equivalent).

- **Compute the range.** The previous release tag is the greatest semver `v*.*.*` tag strictly below `v<new-version>` — sort `git tag --list 'v*.*.*'` by *semver*, not creation date. Range = `<prev tag>..v<new-version>` (or just `v<new-version>` if there is no prior tag).
- **Resolve shipped issues** from that range:
  - *PR links (authoritative):* for each `Merge pull request #N` in `git log <range> --pretty=%s`, read that PR's `closingIssuesReferences` (GraphQL) → issue numbers.
  - *Text refs (supplemental):* `Closes/Fixes/Resolves #N` in `git log <range> --pretty=%B`.
  - Keep only **closed, non-PR issues** (drop open issues, PRs, and not-found).
- **Confirm with the user before writing.** Show the resolved list (number + title) targeting `Release=v<new-version>`. Call out any that read as retrospective *mentions* rather than this-release work — e.g. a commit saying `from closed #N` will false-match the text regex. Let the user deselect false positives. HALT if they reject the set.
- **Ensure the option exists.** The field is the `Release` single-select on project `B3dmar/projects/1` (project id `PVT_kwDOD6Qg6M4BUfKe`). Query its options; if `v<new-version>` is missing, append it with `updateProjectV2Field`, passing **all existing options back with their `id` and `color`** plus the new `{name: "v<new-version>", color: PURPLE}`. Omitting the ids recreates the options and orphans every existing Release value — never do that.
- **Set the field.** For each confirmed issue, find its project item (add it to the project if missing), then `updateProjectV2ItemFieldValue` to `v<new-version>`.
- Report the count of issues tagged. HALT and surface any GraphQL error.

### 9. Summarize

Output a structured release summary, reporting each step's outcome:

```
## Release <new-version>
- **Pre-flight**: clean tree, on staging ✓
- **Version**: <old> → <new>
- **release.sh**: <ok | failed>
- **Release PR**: <url> (<merged | open>)
- **Tag**: v<new-version> <pushed | pending>
- **Release field**: <N> issues set to v<new-version> on the board
- **Next**: [e.g. /sp3cmar-release-notes --tag v<new-version> --publish to publish GitHub release notes]
```

If any step HALTED, state which step failed and what the user must do to recover before re-running.
