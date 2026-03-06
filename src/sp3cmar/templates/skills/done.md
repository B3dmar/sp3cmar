---
description: Debrief the session and close — extract memories, then clear
---

End the current session cleanly. Extract structured memories for cross-session continuity, then clear.

## Arguments

`$ARGUMENTS` controls behavior:
- *(empty)* — run full debrief, then clear
- `quick` — minimal debrief (decisions + commitments only), then clear
- `--no-clear` — debrief but stay in the session

## Steps

### 1. Session review

Scan the conversation for:
- **Decisions made** — architectural choices, tradeoffs resolved, approaches selected
- **Commitments** — things promised for later ("I'll do X next", "TODO: Y")
- **Blockers discovered** — issues that couldn't be resolved, external dependencies
- **Key context** — anything a future session would need to continue this work

### 2. Persist memories

Use the Engram MCP tools (if available) to store structured memories:
- `remember` — store decisions, context, and blockers as memories
- `commitments` — register any new commitments with deadlines if stated

If Engram MCP is not connected, output the debrief summary as text so the user can capture it manually.

### 3. Summarize

Output a brief session summary:
```
## Session debrief
- **Shipped**: [what was completed]
- **Decisions**: [key choices made]
- **Open**: [commitments, blockers, next steps]
```

### 4. Clear (unless `--no-clear`)

Clear the session context. The user should see the debrief summary before the clear happens.
