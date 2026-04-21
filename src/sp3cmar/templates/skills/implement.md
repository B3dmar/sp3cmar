---
description: Autonomous feature implementation — spec/issue to working PR
---

# Implement

Take a GitHub issue or spec file and autonomously implement the feature end-to-end, producing a working PR.

## Arguments

| Flag | Description |
|------|-------------|
| `$ARGUMENTS` | `#<number>` (GH issue) or `<path>` (spec/plan file). Optional flags: `--pr-only` (skip ship), `--step <N>` (resume from step N) |

## Instructions

### Step 1: Load Requirements

Parse `$ARGUMENTS`:
- If `#<number>` — run `gh issue view <number>` to load the issue body, title, and labels
- If a file path — read the file (spec, plan, or breakdown)
- Extract acceptance criteria, scope, and constraints

If no valid input found, output: "ERROR: Provide a GH issue number (#N) or spec file path." and stop.

### Step 2: Ground in prior decisions (3ngram, if available)

Before exploring the codebase, pull the institutional memory for this topic:

1. Call `mcp__3ngram__briefing` with `brief=true` and `sections=["blockers","stale","recent_decisions"]`.
2. Call `mcp__3ngram__search_memories` with a topic string derived from the issue/spec title and the scope summary (e.g. "mixin pattern protocol runtime assert" for a service-split task). Limit 8, `brief=true`.
3. Read the returned memories in full before exploring. They often contain the exact conventions, prior gotchas, and file paths you'd otherwise re-discover.
4. If any returned memory indicates a blocker on the current work (e.g. "don't add rules until pipeline fixed"), pause and surface to the user before writing code.

If 3ngram MCP is unavailable, skip with a one-line note and continue.

### Step 3: Explore Codebase

Before writing any code:
1. Read the project's `CLAUDE.md` for conventions, patterns, and constraints
2. Find similar existing patterns — search for analogous features already implemented
3. Map the files that will need changes — identify create vs modify
4. Check for existing tests that cover adjacent functionality

### Step 4: Plan Changes

Produce a brief implementation plan:
- List each file to create or modify with a one-line description
- Estimate total diff size — if >200 lines, slice into the smallest shippable unit and note remaining work as follow-up
- Identify any blockers or ambiguities

**Present the plan to the user and wait for approval before proceeding.**

### Step 5: Implement

Execute the approved plan:
1. Write code following project conventions (from CLAUDE.md and existing patterns)
2. Write tests alongside the code — unit tests for logic, integration tests for API/DB
3. Keep changes minimal and focused — no drive-by refactors

### Step 6: Quality Gate

Run the project's quality checks on changed files:

```bash
# Python projects
ruff check <changed_files> --fix
ruff format <changed_files>
# Run mypy if type annotations changed
# Run pytest on relevant test files
```

If any check fails:
1. Fix the issue
2. Re-run checks
3. Repeat up to 3 times total

If still failing after 3 attempts, stop and ask the user for guidance.

### Step 7: Persist findings (3ngram, if available)

Before shipping, capture anything worth keeping for future sessions:

- If you discovered a **new pattern** (convention, mixin shape, protocol, file layout): `mcp__3ngram__remember` with `classification=pattern`
- If you made a **non-obvious architectural choice** with a tradeoff: `classification=decision`
- If you hit a **gotcha that wasn't in the memories you searched in Step 2**: `classification=pattern`, tag it so future searches hit it
- If this surfaces **follow-up work** outside the current PR scope: `classification=commitment` with a short description

One `remember` call per run minimum unless the task was purely mechanical. This makes you a net contributor to the memory, not just a reader.

Skip if 3ngram MCP is unavailable.

### Step 8: Ship

Unless `--pr-only` was passed, delegate to `/sp3cmar-ship` to commit, push, and create the PR.

If `--pr-only` was passed, stage the changes and output a summary of what was implemented, but do not commit or push.

## Rules

- **Single PR per run** — if the implementation exceeds 200 lines, implement only the first slice and document the remainder
- **Never ship with failing tests** — quality gate must pass before Step 7
- **Ask if blocked** — if anything is ambiguous or a decision has multiple valid options, ask the user rather than guessing
- **Follow project conventions** — CLAUDE.md rules override any default behavior
