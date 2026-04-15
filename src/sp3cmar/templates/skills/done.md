---
description: Debrief the session and close — extract memories, check dirty state
---

End the current session cleanly. Check for uncommitted work, extract and persist structured memories, resolve completed commitments, and produce a concise summary.

## Arguments

`$ARGUMENTS` controls behavior:
- *(empty)* — run full debrief
- `quick` — minimal debrief (decisions + commitments only, skip patterns/context)

## Steps

### 1. Check for uncommitted work

Run `git status --short` to surface any dirty files. If uncommitted changes exist, flag them before proceeding so the user can decide whether to commit or discard.

### 2. Session review

Scan the conversation for:
- **Decisions made** — architectural choices, tradeoffs resolved, approaches selected
- **Patterns discovered** — coding patterns, conventions, gotchas worth remembering
- **Commitments** — things promised for later ("I'll do X next", "TODO: Y")
- **Blockers discovered** — issues that couldn't be resolved, external dependencies
- **Key context** — anything a future session would need to continue this work

If `quick` argument: only extract decisions and commitments.

### 3. Check open commitments

Read `engram://commitments` to identify any commitments that were completed during this session.

### 4. Persist memories

Use the Engram MCP tools to store structured memories with explicit classification:

- `mcp__3ngram__remember` with classification `decision` — for architectural choices and tradeoffs
- `mcp__3ngram__remember` with classification `pattern` — for coding patterns, conventions, gotchas
- `mcp__3ngram__remember` with classification `context` — for project state, environment details
- `mcp__3ngram__remember` with classification `commitment` — for things promised for future sessions

For any commitments completed during this session: `mcp__3ngram__resolve` with the memory ID.

If Engram MCP is not connected, output the debrief summary as text so the user can capture it manually.

### 5. Summarize

Output a structured debrief:
```
## Session debrief
- **Shipped**: [what was completed]
- **Decisions**: [key choices made]
- **Open**: [commitments, blockers, next steps]
- **Persisted**: N decisions, N patterns, N context, N commitments | N resolved
```
