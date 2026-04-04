---
description: Session close with structured memory extraction to 3ngram
---

# Session Debrief (3ngram-Enhanced)

Close a working session by extracting and persisting structured memories.

## Steps

### 1. Gather Session Artifacts
- `git diff --stat HEAD~5..HEAD` — recent changes
- `git log --oneline -10` — recent commits
- List files modified during this session

### 2. Extract Memories
Identify and classify memories from this session:

**Decisions** — choices made with rationale
- Use `mcp__3ngram__remember` with classification `decision`

**Patterns** — coding patterns, conventions discovered
- Use `mcp__3ngram__remember` with classification `pattern`

**Context** — project state, environment details
- Use `mcp__3ngram__remember` with classification `context`

**Commitments** — things promised for future sessions
- Use `mcp__3ngram__remember` with classification `commitment`

### 3. Resolve Completed Items
- `engram://commitments` — check open commitments
- For any completed during this session: `mcp__3ngram__resolve` with the memory ID

### 4. Session Summary
Produce a structured debrief:

```
## Session Debrief

### Work Completed
- [List of changes made]

### Memories Stored
- {count} decisions
- {count} patterns
- {count} context entries
- {count} new commitments

### Commitments Resolved
- [List of resolved commitments]

### Open Items for Next Session
- [Remaining work]
```

## Graceful Degradation
If 3ngram MCP is not available, produce the session summary as text output only.
Suggest the user save it manually.
