---
description: Audit tracking artifacts for drift — roadmap vs backlog vs GH issues vs memories
---

Cross-reference project tracking artifacts and report contradictions, stale items, and missing entries.

## Arguments

`$ARGUMENTS` controls scope:
- *(empty)* — full audit of all sources
- `roadmap` — audit roadmap.md only
- `issues` — audit GitHub issues only
- `commitments` — audit Engram commitments only

## Steps

### 1. Gather all tracking data

Run in parallel:

- **Roadmap**: Read `roadmap.md` (or equivalent). Extract all checkbox items with their status (done/open) and any issue references
- **Backlog**: Read `backlog.md` (if exists). Extract entries with issue references
- **GitHub issues**: `gh issue list --state all --limit 100 --json number,title,state,labels`
- **Engram commitments**: Read `engram://commitments` and `engram://stale` via MCP resources

### 2. Cross-reference

Check for these drift patterns:

| Pattern | Description |
|---------|-------------|
| **Ghost items** | Marked done in docs but still open on GitHub |
| **Orphaned issues** | Closed on GitHub but listed as open in docs |
| **Duplicate tracking** | Same work tracked in multiple places with different status |
| **Missing issues** | Roadmap items with no corresponding GitHub issue |
| **Stale commitments** | Engram commitments with no recent activity (7+ days) |
| **Unlabeled issues** | Open issues missing area/type/priority labels |

### 3. Report

Output a structured report:

```
## Doc Audit — YYYY-MM-DD

### Contradictions (N found)
- [ ] #123 "feature X" — closed on GH but open in roadmap.md line 45
- [ ] roadmap item "add Y" — checked off but no matching GH issue exists

### Stale items (N found)
- [ ] Commitment "do Z" — 12 days old, no activity
- [ ] #456 "fix W" — open 30+ days, no assignee

### Missing tracking (N found)
- [ ] roadmap line 78 "implement Q" — no GitHub issue
- [ ] backlog entry "refactor R" — no issue, no commitment

### Label gaps (N found)
- [ ] #789 — missing type: label
- [ ] #101 — missing area: label

### Summary
- Total contradictions: N
- Stale items: N
- Tracking gaps: N
```

This command is **READ-ONLY** — it reports issues but does not fix them. Use the findings to create follow-up tasks.
