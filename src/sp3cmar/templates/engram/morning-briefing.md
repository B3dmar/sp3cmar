---
description: Morning session startup with 3ngram recall, commitments, and priorities
---

# Morning Briefing (3ngram-Enhanced)

Start a new working session by loading context from 3ngram memory.

## Steps

### 1. Session Briefing
Call `mcp__3ngram__status` to check 3ngram connection, then:
- `mcp__3ngram__overdue` — show any overdue commitments
- `mcp__3ngram__blockers` — show active blockers
- `mcp__3ngram__commitments` — show open commitments
- `mcp__3ngram__stale_commitments` — flag anything stale (7d+)

### 2. Recent Context
- `mcp__3ngram__recall` with query matching the current project — retrieve recent decisions, patterns, and context
- `mcp__3ngram__suggested_context` — get AI-suggested relevant memories

### 3. Project Status
- Check `git log --oneline -10` for recent commits
- Check `gh pr list --state open` for open PRs
- Check `gh issue list --state open --limit 10` for open issues

### 4. Priority Summary
Synthesize all context into:

```
## Today's Priorities
1. [Highest priority item based on overdue/blockers]
2. [Next priority based on commitments]
3. [Suggested work based on recent context]

## Open Items
- Overdue: {count}
- Blockers: {count}
- Commitments: {count}
- Stale: {count}
```

## Graceful Degradation
If 3ngram MCP is not available, fall back to git log + GitHub CLI context only.
Report that 3ngram is unavailable and suggest setup steps.
