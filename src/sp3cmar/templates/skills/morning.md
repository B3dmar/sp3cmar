---
description: Morning session startup — context, commitments, and priorities
---

Start the day with full context. Aggregate recent work, open commitments, and blockers into a single briefing.

## Arguments

`$ARGUMENTS` controls behavior:
- *(empty)* — full morning briefing
- `quick` — commitments and blockers only

## Steps

### 0. Daily note (seb-life context only)

If `notes/daily-notes/` exists in the current repo or in `~/projects/seb-life`:
- Run `./scripts/daily-note.sh` (or `~/projects/seb-life/system/scripts/daily-note.sh`) to create/open today's note
- Read today's note and identify carryover tasks (items with `(↻N)` markers or `- [ ]` from yesterday)
- Summarize carryover tasks in the briefing output

If not in seb-life context: skip this step.

### 1. Gather context

Run these in parallel where possible:

- **Recent commits**: `git log --oneline --since="yesterday" --all` across the current repo
- **Open commitments**: Query Engram MCP `commitments()` tool for open items
- **Blockers**: Query Engram MCP `blockers()` tool
- **Overdue items**: Query Engram MCP `overdue()` tool
- **Stale commitments**: Query Engram MCP `stale_commitments()` tool

If Engram MCP is not connected, skip memory queries and note that context is limited.

### 2. Check external state

- `gh pr list --author @me --state open` — open PRs awaiting review or CI
- `gh pr list --review-requested @me` — PRs needing your review
- Check if any open PRs have failing CI checks

### 3. Synthesize briefing

Output a structured briefing:

```
## Morning briefing — YYYY-MM-DD

### Open PRs
- [list with CI status]

### Commitments (N open)
- [list with age/urgency]

### Blockers
- [list or "none"]

### Overdue / Stale
- [items needing attention]

### Yesterday's work
- [commit summary]

### Suggested priorities
1. [highest impact item]
2. [next]
3. [next]
```

### 4. Priority recommendation

Based on the gathered context, suggest 3 priorities for the day:
- Overdue items first
- Blocking items second
- Feature work third

Do NOT create or modify any files. This is a read-only briefing.
