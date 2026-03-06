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

### 1. Open PR inventory

Run in parallel:

```
gh pr list --state open --json number,title,author,baseRefName,headRefName,labels,reviewDecision,statusCheckRollup,createdAt,updatedAt
```

For each PR:
- Summarize purpose (1 line)
- Note CI status (passing/failing/pending)
- Note review status (approved/changes-requested/pending)
- Flag any PR older than 7 days without activity as **stale**
- Identify dependency chains (PRs that must merge in order)

### 2. Blockers and commitments (3ngram / Engram)

Skip this step if `--skip-engram` is passed or if Engram MCP is not connected.

Query Engram for project-related context:
- `blockers()` — active blockers
- `commitments()` — open commitments
- `overdue()` — overdue items
- `stale_commitments()` — stale commitments

Extract anything that affects merge readiness and list it.

### 3. Staging ↔ main delta

Run:
```
git diff main...staging --stat
git log main..staging --oneline
```

Analyze:
- Total files changed, insertions, deletions
- List each commit with its type (feat/fix/chore/refactor)
- Group changes by domain (backend / frontend / migrations / infra / CI)
- Flag **migrations** — these need special merge-order attention
- Flag **breaking changes** or schema changes
- Flag **config/env changes** that need deployment coordination

### 4. Risk assessment

For each category, rate risk (low / medium / high) with justification:

| Category | What to check |
|----------|---------------|
| Migration safety | Irreversible schema changes? Migration conflicts? |
| API compatibility | Breaking endpoint changes? FE/BE schema mismatch? |
| Test coverage | New features covered? Skipped/failing tests? |
| Dependency conflicts | Package version mismatches between branches? |
| Deployment order | Must backend deploy before frontend, or vice versa? |

### 5. Synthesize roadmap

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
