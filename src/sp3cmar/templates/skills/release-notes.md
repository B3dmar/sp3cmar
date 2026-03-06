---
description: Generate release notes from staging-to-main diff
---

# Release Notes

Generate human-readable release notes from the staging→main diff.

## Overview

Groups changes by audience (users/devs/ops), deduplicates related commits, and highlights breaking changes. Optionally posts via `gh release create`.

## Arguments

| Flag | Description |
|------|-------------|
| `--tag TAG` | Git tag for the release (default: auto-increment from latest tag) |
| `--draft` | Create as draft release on GitHub |
| `--publish` | Create and publish release on GitHub via `gh release create` |
| `--from REF` | Start ref for diff (default: latest tag or last release) |
| `--to REF` | End ref for diff (default: HEAD) |

## Instructions

### Step 1: Determine Diff Range

```bash
# Get latest tag
LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")

# Get commit log since last release
if [ -n "$LATEST_TAG" ]; then
  git log ${LATEST_TAG}..HEAD --oneline --no-merges
else
  git log --oneline --no-merges -50
fi
```

If `--from` / `--to` are provided, use those instead.

### Step 2: Analyze Commits

For each commit:
1. Parse conventional commit prefix (feat, fix, refactor, docs, chore, perf)
2. Extract scope if present
3. Read the full commit message for context
4. Group related commits (same feature across multiple commits)

### Step 3: Classify by Audience

| Audience | Include |
|----------|---------|
| **Users** | New features, bug fixes, UX changes, breaking changes |
| **Developers** | API changes, new integrations, refactors, dependency updates |
| **Ops** | Infrastructure changes, config changes, deployment notes |

### Step 4: Detect Breaking Changes

Flag as breaking if:
- Commit message contains `BREAKING CHANGE:` or `!:` suffix
- API endpoints removed or renamed
- Required config variables added
- Database migrations with destructive operations

### Step 5: Generate Release Notes

```markdown
# Release {tag}

## Highlights
{1-3 sentence summary of the most impactful changes}

## What's New
- {feature description} ({PR link if available})

## Bug Fixes
- {fix description} ({PR link if available})

## Breaking Changes
- {breaking change with migration instructions}

## For Developers
- {API changes, refactors, dependency updates}

## For Ops
- {infrastructure, config, deployment notes}

## Contributors
{list of commit authors}
```

### Step 6: Publish (Optional)

If `--publish` or `--draft`:

```bash
# Create GitHub release
gh release create {tag} --title "Release {tag}" --notes-file /tmp/release-notes.md {--draft}
```

Output the release URL when done.
