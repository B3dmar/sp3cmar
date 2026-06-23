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

### 2. Worktree prune candidates

If running inside a multi-worktree repo, run `git worktree list --porcelain` to enumerate worktrees and `git branch --merged origin/main` to find merged branches. Compute the intersection: worktrees whose branch has already merged. List them to the user with their slug and last-commit date, and offer (yes/no) to remove via `git worktree remove <path>` for each. Default to NOT removing if the user is silent — destructive action requires affirmative consent. Skip this step entirely if not in a git repo or if `.worktrees/` doesn't exist.

### 3. Session review

Scan the conversation for:
- **Decisions made** — architectural choices, tradeoffs resolved, approaches selected
- **Patterns discovered** — coding patterns, conventions, gotchas worth remembering
- **Commitments** — things promised for later ("I'll do X next", "TODO: Y")
- **Blockers discovered** — issues that couldn't be resolved, external dependencies
- **Key context** — anything a future session would need to continue this work

If `quick` argument: only extract decisions and commitments.

### 4. Check open commitments

Read `engram://commitments` to identify any commitments that were completed during this session.

### 5. Persist memories

Use the 3ngram MCP tools to store structured memories with explicit classification:

- `mcp__3ngram-prod-oss__remember` with classification `decision` — for architectural choices and tradeoffs
- `mcp__3ngram-prod-oss__remember` with classification `pattern` — for coding patterns, conventions, gotchas
- `mcp__3ngram-prod-oss__remember` with classification `context` — for project state, environment details
- `mcp__3ngram-prod-oss__remember` with classification `commitment` — for things promised for future sessions

For any commitments completed during this session: `mcp__3ngram-prod-oss__resolve` with the memory ID.

If 3ngram MCP is not connected, output the debrief summary as text so the user can capture it manually.

### 6. Summarize

Output a structured debrief:
```
## Session debrief
- **Shipped**: [what was completed]
- **Decisions**: [key choices made]
- **Open**: [commitments, blockers, next steps]
- **Persisted**: N decisions, N patterns, N context, N commitments | N resolved
```
