---
description: Break approved spec into ordered stacked PRs under 200 lines
---

# Feature Breakdown

Take an approved SPEC.md and produce an ordered list of stacked PRs respecting the <200 line PR rule.

## Overview

Converts a feature specification into an actionable implementation plan with:
1. **Ordered PR list** — Each PR builds on the previous, forming a stack
2. **File-level scope** — Exact files to create or modify per PR
3. **Acceptance criteria** — What "done" means for each PR
4. **Complexity estimates** — S/M/L sizing for planning

## Arguments

| Flag | Description |
|------|-------------|
| `$ARGUMENTS` | Path to SPEC.md or FEAT-NNN slug (e.g., `FEAT-001-auth`) |

## Instructions

### Step 1: Load Spec

```bash
# Try direct path first, then sp3cmar features directory
ls $ARGUMENTS 2>/dev/null || ls sp3cmar/features/FEAT-*-*/SPEC.md 2>/dev/null
```

Read the spec file. If no approved spec found, output: "ERROR: No approved SPEC.md found. Run `/sp3cmar-feature` first." and exit.

Verify the spec has been approved (look for approval marker or ask user to confirm).

### Step 2: Ground in prior decisions (3ngram, if available)

Before slicing the spec into PRs, pull institutional memory that shapes the boundaries:

1. Call `mcp__3ngram__briefing` with `brief=true` and `sections=["blockers","stale","recent_decisions"]` — surfaces active blockers and architectural decisions that affect ordering.
2. Call `mcp__3ngram__search_memories` with a topic derived from the spec title and the modules it touches (e.g. "auth mixin protocol", "billing subscription webhook"). Limit 8, `brief=true`.
3. Read returned memories. Notably: prior **decisions** often dictate the right PR ordering (e.g. "protocol must ship before mixins" from a similar refactor); prior **blockers** may force re-ordering (e.g. "don't merge X until Y pipeline fixed").
4. If any returned memory indicates a blocker on this feature's scope, pause and surface to the user before writing the breakdown.

If 3ngram MCP is unavailable, skip with a one-line note and continue.

### Step 3: Analyze Scope

From the spec, extract:
- All components/modules that need changes
- New files that need creation
- Existing files that need modification
- External dependencies or integrations
- Database migrations needed

### Step 4: Determine PR Boundaries

Rules for splitting:
1. **Each PR must be under 200 lines of diff** (excluding generated files, lock files)
2. **Each PR must be independently reviewable** — no half-implemented features
3. **Each PR must leave the codebase in a working state** — tests pass, no broken imports
4. **Database migrations get their own PR** — never mixed with application code
5. **Foundation first** — types, models, and interfaces before implementation
6. **Tests travel with their code** — test files in the same PR as the code they test

### Step 5: Order the Stack

Determine dependency order:
1. Schema/migration PRs first
2. Shared types and interfaces
3. Core business logic
4. API/route handlers
5. Frontend components
6. Integration tests and e2e
7. Documentation updates

### Step 6: Generate Breakdown

**Output:** `sp3cmar/features/FEAT-{NNN}-{slug}/BREAKDOWN.md`

```markdown
# Breakdown: FEAT-{NNN} — {title}

Source: `sp3cmar/features/FEAT-{NNN}-{slug}/SPEC.md`
Generated: {date}
Total PRs: {count}
Estimated complexity: {S/M/L/XL}

## PR Stack

### PR 1: {title}
**Branch:** `feat/{slug}-1-{short-desc}`
**Complexity:** S | M | L
**Files:**
- `CREATE src/models/user.py` — User model definition
- `MODIFY src/db/migrations/` — Add users table migration

**Acceptance Criteria:**
- [ ] Migration runs successfully
- [ ] Model matches spec schema
- [ ] Tests pass

**Blockers:** None

---

### PR 2: {title}
**Branch:** `feat/{slug}-2-{short-desc}`
**Complexity:** S | M | L
**Depends on:** PR 1
**Files:**
- `CREATE src/services/auth.py` — Auth service implementation
- `CREATE tests/test_auth.py` — Auth service tests

**Acceptance Criteria:**
- [ ] Login flow works end-to-end
- [ ] Tests cover happy path and error cases

**Blockers:** PR 1 must be merged

---
{... additional PRs ...}

## Dependency Graph
PR1 → PR2 → PR3
            ↘ PR4 → PR5
```

### Step 7: Validate

After generating:
1. Verify total estimated lines across all PRs roughly matches spec scope
2. Verify no circular dependencies between PRs
3. Verify each PR has at least one acceptance criterion
4. Output summary: "{N} PRs, estimated {S/M/L} total, longest chain: {depth}"
