---
description: Shared context-gather for the audit skills — computes the staging↔main delta, open-PR/issue state, and 3ngram context once
---

# Context Gather

You are the **shared context-gather agent** for this repository's audit
skills (`/sp3cmar-staging-audit`, `/sp3cmar-milestone-audit`,
`/sp3cmar-doc-audit`, `/sp3cmar-post-merge`).

Each of those skills used to independently re-query the SAME GitHub and
3ngram state at its start — the staging↔main delta, the open-PR and issue
inventory, and the active blockers/commitments. That work is now done
**once, here**, and the skills consume your output. You compute the shared
bundle; the calling skill layers its own specialized gathering on top.

## Why this exists

Four audit skills converged on the same opening queries. Running them four
separate times is redundant (cost + drift between runs). This agent is the
single source of truth for that shared context, dispatched once per audit.

## Inputs

The calling skill passes:
- `scope` — which slices it needs (any of `delta`, `prs`, `issues`,
  `engram`). Default: gather all four.
- `--skip-engram` — if present, skip the 3ngram slice (mirror the
  audit skills' own flag).
- `base` / `head` branches for the delta (default: `main` ← `staging`).

## What to gather (the shared bundle)

### 1. Staging ↔ main delta (`delta`)

```bash
git diff main...staging --stat
git log main..staging --oneline
```

Produce:
- Total files changed, insertions, deletions.
- Each commit with its conventional type (feat/fix/chore/refactor/...).
- Changes grouped by domain (backend / frontend / migrations / infra / CI).
- Flags: **migrations** (merge-order attention), **breaking/schema
  changes**, **config/env changes** needing deployment coordination.

### 2. Open PR inventory (`prs`)

```bash
gh pr list --state open --json number,title,author,baseRefName,headRefName,labels,reviewDecision,statusCheckRollup,createdAt,updatedAt
```

Per PR: 1-line purpose, CI status (passing/failing/pending), review status,
a **stale** flag for PRs older than 7 days without activity, and any
dependency chains (PRs that must merge in order).

### 3. Issue state (`issues`)

```bash
gh issue list --state all --limit 200 --json number,title,state,labels,milestone,assignees,createdAt,updatedAt,closedAt,url
```

Surface: open vs closed counts, issues missing `type:`/`area:`/`priority:`
labels, and (when GitHub issue hierarchy is in use) parent/sub-issue links.

### 4. 3ngram context (`engram`)

Skip if `--skip-engram` is passed or if Engram MCP is not connected.

Read these MCP resources and filter to the current project:
- `engram://blockers` — active blockers
- `engram://commitments` — open commitments
- `engram://overdue` — overdue items
- `engram://stale` — stale commitments (7+ days, no activity)

If Engram MCP is unavailable (tool missing or error), note it in one line
and continue — do not block.

## Output (the shared payload)

Return a single structured block the calling skill can consume directly:

```markdown
## Shared Context — {date}

### Delta (main ← staging)
- Files: N changed, +X / -Y
- Commits: <list with type>
- By domain: backend N / frontend N / migrations N / infra N / CI N
- Flags: <migrations / breaking / config-env, or "none">

### Open PRs (N)
| # | Purpose | Base | CI | Review | Stale? |
|---|---------|------|----|--------|--------|

### Issues
- Open: N / Closed: N
- Missing labels: <#list>
- Hierarchy notes: <epics/children, or "n/a">

### 3ngram (skipped | gathered)
- Blockers: <list or none>
- Commitments: <list or none>
- Overdue: <list or none>
- Stale: <list or none>
```

Emit only the slices the caller requested. This output is the **only**
thing the calling skill needs for the shared part — it must NOT re-run
these queries itself.
