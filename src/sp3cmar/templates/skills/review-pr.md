---
description: Review PR against project standards, ship-stoppers, and work items
---

# PR Review

Review pull request against project standards, ship-stoppers, and work items.

## Overview

This skill performs a comprehensive PR review that connects to:
1. **Project standards** — Check changes against ARCHITECTURE.md, CONTRIBUTING.md, SECURITY.md, CLAUDE.md, etc.
2. **Kill Reports** — Detect if PR addresses or introduces ship-stoppers
3. **Work Items** — Verify "Fixes WI-XXX" claims by running actual tests

## Arguments

| Flag | Description |
|------|-------------|
| `--base BRANCH` | Base branch for diff (default: main) |
| `--comment` | Post findings as GitHub PR comment |
| `--json` | Output machine-readable JSON |
| `--ci` | CI mode: exit non-zero on BLOCKING findings |
| `--strict` | With --ci: exit non-zero on ANY finding |
| `--create-wi` | Create work items for critical findings |
## Instructions

### Step 1: Pre-Flight Checks

Before starting, verify:
- [ ] On a feature branch (not main/master)
- [ ] Git working tree is clean (no uncommitted changes)

```bash
# Check branch
git branch --show-current

```

**If pre-flight fails:**
- Not on feature branch → "ERROR: Must be on a feature branch, not main/master"

### Step 2: Load Context

#### 2.1 Load Project Standards (Optional)

Search for project standards in common locations (first match wins per category):

```bash
# Architecture docs
ls ARCHITECTURE.md docs/ARCHITECTURE.md sp3cmar/constitution/enforced/ARCHITECTURE.md 2>/dev/null | head -1

# Contributing / code standards
ls CONTRIBUTING.md docs/CONTRIBUTING.md .github/CONTRIBUTING.md 2>/dev/null | head -1

# Security policy
ls SECURITY.md docs/SECURITY.md 2>/dev/null | head -1

# AI assistant instructions (often contain project conventions)
ls CLAUDE.md .cursorrules .github/copilot-instructions.md AGENTS.md 2>/dev/null

# Project-specific standards index
ls sp3cmar/constitution/enforced 2>/dev/null || ls sp3cmar/docs-index 2>/dev/null

# If nothing found:
echo "INFO: No project standards docs found — reviewing against general best practices only"
```

Load whatever is found. These form the "project standards" baseline for Agent 1.

#### 2.2 Load Latest Kill Report (Optional)

```bash
# Find latest kill report
ls -t sp3cmar/reviews/kill-reports/v*/REPORT.md 2>/dev/null | head -1
```

- **If found:** Load and extract ship-stopper evidence (file:line references)
- **If not found:** Skip ship-stopper checking with info message: "INFO: No kill report found, skipping ship-stopper check"

#### 2.3 Parse Work Item References (Optional)

Search PR description and commit messages for patterns:
- `Fixes WI-XXX`
- `Closes WI-XXX`
- `Resolves WI-XXX`
- `Implements WI-XXX`

For each referenced WI, locate the file:
```
sp3cmar/work-items/WI-*.md
sp3cmar/features/FEAT-*/work-items/WI-*.md
sp3cmar/reviews/*/v*/work-items/WI-*.md
```

### Step 3: Get PR Diff

```bash
# Get base branch (default: main)
BASE_BRANCH=${BASE:-main}

# List changed files
git diff ${BASE_BRANCH}...HEAD --name-only

# Get full diff
git diff ${BASE_BRANCH}...HEAD
```

Parse diff into:
- Changed files list
- Per-file changes with line numbers

### Steps 4-7: Parallel Agent Dispatch

**EXECUTION MODE:** Check for `--sequential` flag in arguments.
- If `--sequential`: Execute Steps 4, 5, 6, 7 in order, one at a time
- Otherwise: Execute all 4 agents IN PARALLEL using separate Task tool calls in a single response

Output: "Dispatching 6 review agents in parallel (+ conditional agents if applicable)..."

### [PARALLEL-START: id=pr-review-agents]

IMPORTANT: Invoke the following 6 agents as parallel Task tool calls. Each agent should be a separate Task invocation in the SAME response. Do NOT wait for one agent to complete before starting the next.

### [PARALLEL] Step 4: Project Standards Review (Agent 1)

For each changed file, check against loaded project standards from Step 2.1.

**Check ARCHITECTURE.md (if loaded):**
- Layer violations (e.g., handler calling DB directly)
- Dependency direction violations
- Module boundary violations

**Check CONTRIBUTING.md (if loaded):**
- Code style violations beyond what linters catch
- Naming convention violations
- Pattern violations (e.g., "always use repository pattern for DB access")

**Check SECURITY.md (if loaded):**
- Auth/authz bypass
- Input validation gaps
- Secrets exposure
- SQL injection / XSS patterns

**Check CLAUDE.md / .cursorrules (if loaded):**
- Anti-patterns flagged in project instructions
- Required patterns not followed

**If no standards docs found:**
- Review against general engineering best practices only
- Note: "No project standards docs found — findings based on general best practices"

**Output format:**
```markdown
### Standards Findings

| Severity | File:Line | Violation | Standard Reference |
|----------|-----------|-----------|---------------------|
| BLOCKING | src/api/handler.py:45 | Direct DB access in handler | ARCHITECTURE.md: "No DB in handlers" |
| WARNING | src/utils/auth.py:23 | Missing input validation | SECURITY.md: "Validate all inputs" |
```

### [PARALLEL] Step 5: Ship-Stopper Check (Agent 2)

If kill report was loaded:

**Extract ship-stopper evidence** from the report (file:line references)

**Compare against PR changes:**
- Does PR modify files referenced in ship-stoppers?
- Does PR introduce NEW violations matching ship-stopper patterns?
- Does PR potentially RESOLVE a ship-stopper?

**Output format:**
```markdown
### Ship-Stopper Findings

| Status | Ship-Stopper | Evidence | PR Impact |
|--------|--------------|----------|-----------|
| BLOCKING | Missing tenant isolation | src/api/queries.py:45 | PR adds similar unfiltered query |
| INFO | Missing tenant isolation | src/api/queries.py:45 | PR modifies this file - verify fix |
```

If no kill report: Skip with "INFO: No kill report found, skipping ship-stopper check"

### [PARALLEL] Step 6: Work Item Verification (Agent 3)

For each referenced work item:

1. **Load the WI file** and extract test files from "Acceptance Criteria" section
2. **Run the tests:**
   ```bash
   pytest tests/{test_file}.py -v --tb=short
   ```
3. **Report results:**

**Output format:**
```markdown
### Work Item Verification

| WI | Status | Tests | Result |
|----|--------|-------|--------|
| WI-003-001 | VERIFIED | tests/test_review_pr.py | 22/22 passing |
| WI-003-002 | BLOCKING | tests/test_skill.py | 3/5 failing |
| WI-003-003 | NOT VERIFIABLE | (no tests found) | Tests required |
```

- **Tests pass** → "WI-XXX acceptance criteria verified"
- **Tests fail** → BLOCKING status with failure details
- **No tests** → "Tests not found - WI not verifiable"

If no WI referenced: Skip with "INFO: No work item references found"

### [PARALLEL] Step 7: Code Quality Review (Agent 4)

Review diff for general code quality:

**Security:**
- OWASP top 10 patterns
- Hardcoded secrets
- Unsafe deserialization

**Performance:**
- N+1 queries
- Missing indexes
- Unbounded loops

**Error Handling:**
- Bare except clauses
- Missing error handling
- Silent failures

**Output format:**
```markdown
### Code Quality Findings

| Severity | File:Line | Issue | Recommendation |
|----------|-----------|-------|----------------|
| WARNING | src/api/users.py:67 | N+1 query pattern | Use prefetch_related |
| INFO | src/utils/cache.py:12 | Unbounded cache | Add TTL or max size |
```

### [PARALLEL] Step 7b: Hardcoded Values Review (Agent 5 — Always)

Dispatch the `reviewer-hardcoded` agent to scan the diff for hardcoded values that should be configuration.

Provide the agent with:
- The full diff from Step 3
- The changed files list

**Output format:**
```markdown
### Hardcoded Values Findings

| # | Severity | Confidence | Finding | Evidence |
|---|----------|------------|---------|----------|
| 1 | WARNING | 85 | Hardcoded API URL in handler | `src/api/client.py:23` |
```

### [PARALLEL] Step 7e: Correctness Review (Agent 6 — Always)

Dispatch the `reviewer-correctness` agent to review for bugs, logic errors, edge cases, and functional correctness.

Provide the agent with:
- The full diff from Step 3
- The changed files list

**Output format:**
```markdown
### Correctness Findings

| # | Severity | Confidence | Finding | Evidence |
|---|----------|------------|---------|----------|
| 1 | BLOCKING | 90 | Off-by-one in pagination logic | `src/api/list.py:45` |
```

### [PARALLEL-END: id=pr-review-agents]

After all Task calls complete, proceed to conditional agents.

### Steps 7c-7d: Conditional Agent Dispatch

Check the changed files list from Step 3 and dispatch additional agents if conditions are met.

#### Step 7c: API Contract Review (Agent 6 — Conditional)

**Condition:** Diff contains BOTH frontend files (`*.ts`, `*.tsx`, `*.js`, `*.jsx`, `*.vue`, `*.svelte`) AND backend files (`*.py`, `*.go`, `*.rs`, `*.java`, `*.rb`, `routes.*`, `api.*`).

If condition met:
- Output: "Frontend + backend changes detected — dispatching contract reviewer..."
- Dispatch the `reviewer-contract` agent with the full diff and changed files list
- The agent validates that frontend API calls match backend route definitions

If condition not met:
- Output: "INFO: No cross-boundary changes — skipping contract review"

#### Step 7d: Migration Safety Review (Agent 7 — Conditional)

**Condition:** Diff contains migration files (paths matching `*migration*`, `*alembic*`, `*prisma/migrations*`, `*db/migrate*`, `*knex*migrations*`).

If condition met:
- Output: "Migration files detected — dispatching migration safety reviewer..."
- Dispatch the `migration-check` agent with the migration file diffs
- The agent checks for destructive ops, locking risks, and missing rollbacks

If condition not met:
- Output: "INFO: No migration files — skipping migration safety review"

Wait for any conditional agents to complete before proceeding to Step 8.

### Key-Files Collection

After all agents complete:
1. Iterate through agent outputs in dispatch order
2. For each agent, find the `### Key Files` section
3. Extract file paths from the fenced code block
4. Build a unique list (first occurrence wins, skip duplicates)
5. Read up to 5 unique files using the Read tool
6. If a file doesn't exist, skip with warning and continue
7. Use the collected context for the aggregation phase

### Step 8: Aggregate Findings

Output: "Consolidating findings from {completed_count} agents (6 core + {conditional_count} conditional)..."

If any agent failed:
- Output: "⚠️ {failed_count} agent(s) did not complete: {names}"
- Output: "Tip: Re-run with `--sequential` to retry"
- Continue with available findings

**Consolidation:**

Combine all findings and assign overall severity:

### Confidence Scoring

Each finding MUST include a confidence score (0-100) alongside its severity:

| # | Severity | Confidence | Finding | Evidence |
|---|----------|------------|---------|----------|
| 1 | BLOCKING | 92 | Description | `file:line` |
| 2 | WARNING | 78 | Description | `file:line` |

**Filtering rules:**
- Default: Show only findings with confidence >= 75
- `--show-all` flag: Show all findings regardless of confidence
- Sort by severity DESC, then confidence DESC within each severity

**Needs Investigation section:**
BLOCKING findings with confidence < 75 are NEVER silently dropped. They go to a dedicated "Needs Investigation" section at the end of the report with the label "BLOCKING but low-confidence — human must verify."

**Severity Levels:**
- **BLOCKING** — Must fix before merge (standards violations, ship-stoppers, failing WI tests)
- **WARNING** — Should fix (code quality issues, potential problems)
- **INFO** — Consider (suggestions, potential improvements)

**Generate Merge Recommendation:**
- Any BLOCKING findings → **"DO NOT MERGE"**
- Only WARNING/INFO → **"SAFE TO MERGE (with notes)"**
- No findings → **"SAFE TO MERGE"**

### Step 8b: Simplify Offer (non-CI only)

If the merge recommendation is **"SAFE TO MERGE (with notes)"** (WARNING/INFO findings, no BLOCKING):

1. Ask the user: "Run /simplify on changed files to address minor issues?"
2. If approved: run `/simplify` on the changed files from Step 3, then re-run lint
3. If declined or in `--ci` mode: skip

### Step 9: Output

#### Terminal Output (Default)

```markdown
# PR Review: feature/my-branch

## Summary
- Standards: 1 BLOCKING, 2 WARNING
- Ship-stoppers: 0 BLOCKING, 1 INFO
- Work Items: 1 VERIFIED, 0 BLOCKING
- Code Quality: 0 BLOCKING, 3 WARNING

## Merge Recommendation: DO NOT MERGE

### BLOCKING Issues (must fix)
1. [Constitution] src/api/handler.py:45 - Direct DB access in handler
   → Move to repository layer per ARCHITECTURE.md

### WARNING Issues (should fix)
[... details ...]

### INFO (consider)
[... details ...]
```

#### GitHub Comment (`--comment`)

```bash
# Get PR number
PR_NUMBER=$(gh pr view --json number -q .number 2>/dev/null)

# Post comment
gh pr comment $PR_NUMBER --body "$(cat review_output.md)"
```

If `gh` not available or not in a PR context, output warning and continue with terminal output.

#### JSON Output (`--json`)

```json
{
  "branch": "feature/my-branch",
  "base": "main",
  "summary": {
    "standards": {"blocking": 1, "warning": 2, "info": 0},
    "ship_stoppers": {"blocking": 0, "warning": 0, "info": 1},
    "work_items": {"verified": 1, "blocking": 0, "not_verifiable": 0},
    "code_quality": {"blocking": 0, "warning": 3, "info": 2}
  },
  "recommendation": "DO NOT MERGE",
  "findings": [...]
}
```

#### CI Mode (`--ci`)

- Suppress Rich formatting (plain text output)
- Exit codes:
  - `0`: No BLOCKING findings
  - `1`: BLOCKING findings present
  - `2`: Review failed to run (pre-flight failed)

With `--strict`:
- `0`: No findings at all
- `1`: Any findings (BLOCKING, WARNING, or INFO)

### Step 10: Work Item Generation (`--create-wi`)

For each BLOCKING or critical finding, create a work item using the scaffold CLI:

```bash
sp3cmar scaffold wi PR {slug}
```

This creates a WI file from the unified template. Then fill in the finding-specific details:
- Problem Statement: [Finding description with evidence]
- Acceptance Criteria: Issue fixed at {file}:{line}, tests added, PR review re-run clean

Output: "Created WI-PR-001 for: {finding title}"

## Guidelines

- **Always provide file:line evidence** for all findings
- **Reference standards docs by name** (e.g., "ARCHITECTURE.md: Layer rules", "CLAUDE.md: Anti-patterns")
- **Show actual test output** for WI verification
- **In CI mode**, output plain text suitable for logs
- **Be thorough but fair** — flag real issues, not style preferences

## Examples

### Basic PR Review
```
/sp3cmar-review-pr
```

### Review Against Different Base Branch
```
/sp3cmar-review-pr --base develop
```

### Post to GitHub PR
```
/sp3cmar-review-pr --comment
```

### CI Pipeline
```
/sp3cmar-review-pr --ci
/sp3cmar-review-pr --ci --strict
```

### Create Work Items for Critical Findings
```
/sp3cmar-review-pr --create-wi
```
