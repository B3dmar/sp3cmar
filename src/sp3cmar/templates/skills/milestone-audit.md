---
description: Audit GitHub milestone scope, issue hygiene, parent links, and release readiness
---

Audit a GitHub milestone for scope drift, issue hygiene, parent/child consistency, release blockers, and tracking drift.

## Arguments

`$ARGUMENTS` controls scope:
- *(empty)* - audit the active or nearest open milestone for the current repo
- `<milestone>` - audit a specific milestone title, for example `v0.6.38`
- `<milestone> --quick` - skip 3ngram and roadmap/doc drift checks
- `<milestone> --apply` - only after presenting a change plan and getting explicit user approval, apply safe GitHub metadata fixes such as labels, milestone moves, and parent/child links

## Rules

1. Default mode is read-only. Do not mutate GitHub, files, branches, or milestones unless `--apply` is present and the user approves the exact change list.
2. Do not infer issue hierarchy from title alone when GitHub parent/sub-issue metadata is available. Prefer GitHub's structured fields.
3. Distinguish release blockers from advisory noise. Failed required checks and unresolved dependencies block; stale comments, optional checks, and old advisory failures do not.
4. Use 3ngram/Engram context when available unless `--quick` is passed.
5. Every finding must cite an issue, PR, file path, memory id, or command result.

## Steps

### 1. Resolve repository and milestone

Identify the current repo:

```bash
gh repo view --json nameWithOwner,defaultBranchRef
```

Resolve the milestone:
- If `$ARGUMENTS` names a milestone, use that exact title.
- If empty, list open milestones and choose the nearest active release milestone. If ambiguous, ask the user which milestone to audit.

Use GitHub CLI/API as needed:

```bash
gh api repos/{owner}/{repo}/milestones
gh issue list --state all --milestone "<milestone>" --limit 200 --json number,title,state,labels,milestone,assignees,createdAt,updatedAt,closedAt,url
gh pr list --state all --base staging --limit 100 --json number,title,state,labels,reviewDecision,statusCheckRollup,createdAt,updatedAt,url
```

If the repo uses GitHub issue hierarchy, inspect parent/sub-issue metadata via `gh issue view` or GraphQL for issues that look like epics or children.

### 2. Gather project context

Unless `--quick` is passed:
- Search 3ngram/Engram for the project, milestone title, release blockers, and recent scope decisions.
- Read roadmap/backlog/release notes files if present: `roadmap.md`, `backlog.md`, `docs/**/roadmap*`, `docs/**/release*`, `.claude/plans/**`.
- Compare docs and memories to GitHub issue state.

### 3. Classify issues

For each milestone issue, classify:

| Class | Meaning |
|-------|---------|
| Epic | Parent issue that owns child work |
| Child | Issue that should have a parent epic |
| Standalone | Self-contained issue with no expected parent |
| Blocker | Must be resolved before release |
| Follow-up | Valid work, but should move out of the milestone |
| Noise | Closed, duplicate, stale, or advisory item that should not affect release readiness |

Check:
- Missing `type:` / `area:` / `priority:` labels
- Missing or wrong milestone
- Open blockers
- Epics without children
- Children without parent epics
- Closed issues still listed as open in docs
- Open GitHub issues marked done in docs
- Scope clusters that make the milestone too broad
- PRs attached to milestone issues that are failing, stale, unreviewed, or merged to the wrong base

### 4. Assess scope and readiness

Rate:
- **Scope focus**: low / medium / high drift
- **Release readiness**: green / yellow / red
- **Tracking integrity**: clean / minor drift / major drift
- **CI/deploy risk**: low / medium / high

State why. Prefer concrete counts over narrative.

### 5. Report

Output:

```markdown
## Milestone Audit - {milestone} - {YYYY-MM-DD}

### Summary
| Metric | Value |
|--------|------:|
| Open issues | N |
| Closed issues | N |
| Epics | N |
| Children without parent | N |
| Epics without children | N |
| Missing labels | N |
| Release blockers | N |
| Scope drift | low/medium/high |
| Readiness | green/yellow/red |

### Blockers
- [ ] #123 Title - why it blocks release, required next action

### Scope Moves
- [ ] Move #456 to vX.Y.Z - rationale

### Hierarchy Fixes
- [ ] Link #789 under #321 - evidence

### Label And Metadata Gaps
- [ ] #234 - missing `priority:` and `area:`

### Tracking Drift
- [ ] roadmap.md line 42 says done, but #345 is open

### Proposed Apply Plan
Only include this section when fixes are clear and safe.
- [ ] gh issue edit ...
- [ ] gh api ...
```

If `--apply` is present, stop after the proposed apply plan and ask for explicit approval before making changes.
