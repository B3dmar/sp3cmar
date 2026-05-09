---
description: Phase-0 briefing for a topic — pulls 3ngram memories, GitHub state, and codebase pointers before you start work
---

Gather everything the AI/operator should know about a topic *before* writing code. Surface prior decisions, related issues, files most likely to touch, and any open commitments — so work starts grounded instead of mid-rework.

## Arguments

`$ARGUMENTS` is the topic — a noun phrase or concept name. Examples:

- `/sp3cmar-context entity merge`
- `/sp3cmar-context billing webhook`
- `/sp3cmar-context dedup gating`

Optional flags:

- `--skip-engram` — skip 3ngram lookup (for repos without engram MCP)
- `--no-pr` — skip the PR/issue search (faster, fewer API calls)

## Steps

Run the following in **parallel** wherever possible.

### 1. 3ngram lookup

Skip if `--skip-engram` is set or the engram MCP is unavailable.

- `mcp__3ngram__search_memories` with the topic — surfaces decisions, blockers, prior commitments, feedback memories
- `mcp__3ngram__search_content` with the topic — pulls indexed documents that mention it

Filter to the current project/scope. Report each hit with one-line summary + `id` + memory_type.

### 2. Codebase pointers

- `rg -l "<topic-keywords>" backend/src frontend/src docs/ 2>/dev/null | head -20` — files mentioning the topic
- If `backend/src/engram/services/<topic>/README.md` or `docs/reference/<topic>*.md` exists, **read it**: that's the authoritative pointer
- If `docs/reference/inventory.md` exists, grep it for the topic — gives endpoint/MCP-tool/table inventory

### 3. GitHub state

Skip if `--no-pr` is set.

```bash
gh issue list --search "<topic>" --state all --limit 20 --json number,title,state,labels,milestone,updatedAt
gh pr list --search "<topic>" --state all --limit 10 --json number,title,state,mergedAt,headRefName
```

Group by state (open / closed-merged / closed-unmerged).

### 4. Recent commits

```bash
git log --all --oneline --grep="<topic>" -20
```

Useful for seeing who touched it, when, and which branch it landed on.

### 5. Synthesis

Produce a one-screen briefing:

```markdown
## Context — <topic>

### Prior decisions (3ngram)
- [memory_id] one-line summary

### Open commitments / blockers
- [memory_id] one-line summary

### Related GH issues
| # | State | Title | Updated |
|---|-------|-------|---------|

### Related PRs
| # | State | Title | Merged |
|---|-------|-------|--------|

### Files most likely to touch
- `path/to/file.py` — why it's relevant
- `path/to/other.ts` — why it's relevant

### Authoritative reading
- `docs/reference/<topic>.md` (if exists)
- `backend/src/engram/services/<topic>/README.md` (if exists)

### Recommended starting move
One sentence: where to look first based on the above.
```

## Output

Read-only briefing. Do **not** create or modify any files.

If the topic looks under-specified or contradicts prior decisions, **flag it** in the recommended starting move and suggest the user run `/sp3cmar-acceptance <issue#>` (if a related issue exists) before starting implementation.
