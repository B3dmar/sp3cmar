---
description: Pre-merge audit — open PRs, blockers, staging↔main delta, roadmap
---

Audit the current project's readiness to merge staging into main. Aggregate open PRs, blockers, the staging↔main diff, and produce an actionable roadmap.

## Arguments

`$ARGUMENTS` controls behavior:
- *(empty)* — full audit with roadmap
- `quick` — delta + blockers only, skip PR deep-dive
- `--skip-engram` — skip 3ngram/Engram memory queries

## Steps

### 1. Gather shared context (once)

Dispatch the `context-gather` agent for the slices this audit needs:
`prs`, `engram`, and `delta`. Pass `--skip-engram` through if present.

It returns the **shared bundle** — open-PR inventory, active
blockers/commitments/overdue/stale, and the staging↔main delta — computed
**once** so this skill, `milestone-audit`, `doc-audit`, and `post-merge`
do not each re-run the same GitHub + 3ngram queries.

Consume its output for the next steps. Do NOT re-run `gh pr list`,
`git diff main...staging`, `git log main..staging`, or the
`engram://` resource reads yourself — the agent already did.

From its `### Open PRs` table, confirm per PR: purpose, CI status, review
status, the **stale** flag (>7 days, no activity), and dependency chains.

From its `### 3ngram` block, filter blockers/commitments/overdue/stale to
the current project before extracting anything that affects merge readiness.

From its `### Delta (main ← staging)` block, take the file/commit counts,
per-commit types, domain grouping, and the migration / breaking-change /
config-env flags.

### 2. Risk assessment

For each category, rate risk (low / medium / high) with justification:

| Category | What to check |
|----------|---------------|
| Migration safety | Irreversible schema changes? Migration conflicts? |
| API compatibility | Breaking endpoint changes? FE/BE schema mismatch? |
| Test coverage | New features covered? Skipped/failing tests? |
| Dependency conflicts | Package version mismatches between branches? |
| Deployment order | Must backend deploy before frontend, or vice versa? |

### 3. Synthesize roadmap

Produce this structured output:

```markdown
## Staging Audit — {date}

### Pre-Merge Checklist
- [ ] Items that MUST be resolved before staging → main

### Merge Sequence
- Ordered list of PRs/actions with rationale

### Post-Merge Actions
- [ ] Items to address immediately after merge (env vars, migrations, monitoring)

### Backlog Items
- Non-blocking issues as follow-ups (with priority)

### Recommended Timeline
- Sequence work into batches with dependencies mapped
```

Link PR numbers, file paths, and commit SHAs where relevant.
Flag anything **irreversible** that needs extra caution.

## Output

Do NOT create or modify any files. This is a read-only audit.
Output the full report directly in the conversation.
