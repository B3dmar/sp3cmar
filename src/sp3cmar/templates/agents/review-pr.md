---
description: Review PR against project standards, ship-stoppers, and work items
---

# PR Review

You are the **PR Review Orchestrator** for this repository.

Review a pull request against project standards, ship-stoppers, and work items.
The orchestrator **does not perform the checks inline** — it loads shared context,
**dispatches a sub-agent per review dimension**, and **synthesizes** their findings
into a single merge recommendation. This mirrors how `review-codebase` dispatches
its sub-reviewers.

## Overview

This review connects to:
1. **Project standards** — Changes vs ARCHITECTURE.md, CONTRIBUTING.md, SECURITY.md, CLAUDE.md, etc.
2. **Kill Reports** — Whether the PR addresses or introduces ship-stoppers
3. **Work Items** — Verify "Fixes WI-XXX" claims by running actual tests
4. **Code Quality** — Security, performance, and error-handling issues in the diff

Each of the four is run by a **delegated sub-agent**, not inline.

## Orchestrator role

The orchestrator:
1. Runs pre-flight checks and loads shared context (Steps 1–3).
2. **Dispatches** the four dimension sub-agents plus the always-on reviewer
   agents (Step 4), passing each the shared diff and context — it does **not**
   evaluate standards, ship-stoppers, work items, or code quality itself.
3. **Collects and synthesizes** sub-agent findings into one consolidated report
   and merge recommendation (Step 6).

If the orchestrator finds itself reading a standards doc to judge a violation, or
running a WI's tests directly, that work belongs in the corresponding sub-agent —
re-dispatch it instead of inlining.

## Arguments

| Flag | Description |
|------|-------------|
| `--base BRANCH` | Base branch for diff (default: main) |
| `--comment` | Post findings as GitHub PR comment |
| `--json` | Output machine-readable JSON |
| `--ci` | CI mode: exit non-zero on BLOCKING findings |
| `--strict` | With --ci: exit non-zero on ANY finding |
| `--sequential` | Dispatch sub-agents one at a time (debug/fallback) |
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

### Step 2: Load Shared Context

The orchestrator loads context **once** and passes it into every dispatched
sub-agent (so sub-agents do not each re-discover it).

#### 2.1 Locate Project Standards (paths only)

Find — but do not yet evaluate — project standards. The Standards sub-agent reads
and judges them; the orchestrator only resolves the paths.

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
echo "INFO: No project standards docs found — Standards sub-agent reviews against general best practices only"
```

#### 2.2 Locate Latest Kill Report (path only)

```bash
ls -t sp3cmar/reviews/kill-reports/v*/REPORT.md 2>/dev/null | head -1
```

- **If found:** pass the path to the Ship-Stopper sub-agent.
- **If not found:** Note "INFO: No kill report found, skipping ship-stopper check".

#### 2.3 Parse Work Item References (paths only)

Search PR description and commit messages for patterns:
- `Fixes WI-XXX`, `Closes WI-XXX`, `Resolves WI-XXX`, `Implements WI-XXX`

For each referenced WI, locate the file (pass paths to the Work-Item sub-agent):
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

Parse the diff into a changed-files list and per-file changes. This diff is the
shared payload handed to every sub-agent.

### Step 4: Dispatch Review Sub-Agents

**EXECUTION MODE:** Check for `--sequential` in arguments.
- If `--sequential`: dispatch the sub-agents one at a time.
- Otherwise: dispatch them IN PARALLEL using separate Task tool calls in a single
  response.

Output: "Dispatching review sub-agents (4 dimension + always-on reviewers + conditional)..."

Each dispatch passes the sub-agent: the **full diff** and **changed-files list**
from Step 3, plus the relevant context paths from Step 2. The orchestrator does
**not** perform any of these checks itself.

### [PARALLEL-START: id=pr-review-agents]

IMPORTANT: Invoke the following as parallel Task tool calls in the SAME response.
Do NOT wait for one sub-agent to complete before starting the next. Do NOT inline
any of these checks in the orchestrator.

### [PARALLEL] Sub-Agent 1 — Project Standards (delegated)

Dispatch a **Project Standards reviewer** sub-agent. Provide it the diff, the
changed-files list, and the standards paths from Step 2.1.

Its task: read the loaded standards and, for each changed file, flag violations:
- **ARCHITECTURE.md** — layer violations, dependency-direction violations, module boundaries
- **CONTRIBUTING.md** — style/naming/pattern violations beyond what linters catch
- **SECURITY.md** — auth/authz bypass, input-validation gaps, secrets exposure, SQLi/XSS
- **CLAUDE.md / .cursorrules** — flagged anti-patterns, required-pattern omissions
- If no standards docs were found → review against general best practices and note it.

**Sub-agent output format:**
```markdown
### Standards Findings

| Severity | File:Line | Violation | Standard Reference |
|----------|-----------|-----------|---------------------|
| BLOCKING | src/api/handler.py:45 | Direct DB access in handler | ARCHITECTURE.md: "No DB in handlers" |
| WARNING | src/utils/auth.py:23 | Missing input validation | SECURITY.md: "Validate all inputs" |
```

### [PARALLEL] Sub-Agent 2 — Ship-Stopper Check (delegated)

Dispatch a **Ship-Stopper reviewer** sub-agent. Provide it the diff, the
changed-files list, and the kill-report path from Step 2.2.

Its task (only if a kill report was found): extract ship-stopper evidence
(file:line), then compare against the PR — does it modify referenced files,
introduce NEW matching violations, or potentially RESOLVE a ship-stopper?

**Sub-agent output format:**
```markdown
### Ship-Stopper Findings

| Status | Ship-Stopper | Evidence | PR Impact |
|--------|--------------|----------|-----------|
| BLOCKING | Missing tenant isolation | src/api/queries.py:45 | PR adds similar unfiltered query |
| INFO | Missing tenant isolation | src/api/queries.py:45 | PR modifies this file - verify fix |
```

If no kill report: the sub-agent reports "INFO: No kill report found, skipping ship-stopper check".

### [PARALLEL] Sub-Agent 3 — Work Item Verification (delegated)

Dispatch a **Work-Item Verification reviewer** sub-agent. Provide it the WI paths
from Step 2.3.

Its task, for each referenced work item:
1. Load the WI file; extract test files from its "Acceptance Criteria" section.
2. Run the tests:
   ```bash
   pytest tests/{test_file}.py -v --tb=short
   ```
3. Report results with actual test output.

**Sub-agent output format:**
```markdown
### Work Item Verification

| WI | Status | Tests | Result |
|----|--------|-------|--------|
| WI-003-001 | VERIFIED | tests/test_review_pr.py | 22/22 passing |
| WI-003-002 | BLOCKING | tests/test_skill.py | 3/5 failing |
| WI-003-003 | NOT VERIFIABLE | (no tests found) | Tests required |
```

- Tests pass → "WI-XXX acceptance criteria verified"
- Tests fail → BLOCKING with failure details
- No tests → "Tests not found - WI not verifiable"

If no WI referenced: the sub-agent reports "INFO: No work item references found".

### [PARALLEL] Sub-Agent 4 — Code Quality (delegated)

Dispatch a **Code Quality reviewer** sub-agent. Provide it the diff and
changed-files list.

Its task: review the diff for general code quality:
- **Security:** OWASP top 10 patterns, hardcoded secrets, unsafe deserialization
- **Performance:** N+1 queries, missing indexes, unbounded loops
- **Error Handling:** bare excepts, missing handling, silent failures

**Sub-agent output format:**
```markdown
### Code Quality Findings

| Severity | File:Line | Issue | Recommendation |
|----------|-----------|-------|----------------|
| WARNING | src/api/users.py:67 | N+1 query pattern | Use prefetch_related |
| INFO | src/utils/cache.py:12 | Unbounded cache | Add TTL or max size |
```

### [PARALLEL] Sub-Agent 5 — Hardcoded Values (always)

Dispatch the `reviewer-hardcoded` agent with the full diff and changed-files list
to scan for hardcoded values that should be configuration.

**Output format:**
```markdown
### Hardcoded Values Findings

| # | Severity | Confidence | Finding | Evidence |
|---|----------|------------|---------|----------|
| 1 | WARNING | 85 | Hardcoded API URL in handler | `src/api/client.py:23` |
```

### [PARALLEL] Sub-Agent 6 — Correctness (always)

Dispatch the `reviewer-correctness` agent with the full diff and changed-files
list to review for bugs, logic errors, edge cases, and functional correctness.

**Output format:**
```markdown
### Correctness Findings

| # | Severity | Confidence | Finding | Evidence |
|---|----------|------------|---------|----------|
| 1 | BLOCKING | 90 | Off-by-one in pagination logic | `src/api/list.py:45` |
```

### [PARALLEL-END: id=pr-review-agents]

After all Task calls complete, proceed to conditional dispatch.

### Steps 4c-4d: Conditional Sub-Agent Dispatch

Check the changed-files list and dispatch additional sub-agents if conditions are met.

#### Step 4c: API Contract Review (Conditional)

**Condition:** Diff contains BOTH frontend files (`*.ts`, `*.tsx`, `*.js`, `*.jsx`, `*.vue`, `*.svelte`) AND backend files (`*.py`, `*.go`, `*.rs`, `*.java`, `*.rb`, `routes.*`, `api.*`).

If met:
- Output: "Frontend + backend changes detected — dispatching contract reviewer..."
- Dispatch the `reviewer-contract` agent with the full diff and changed-files list.

If not met:
- Output: "INFO: No cross-boundary changes — skipping contract review"

#### Step 4d: Migration Safety Review (Conditional)

**Condition:** Diff contains migration files (paths matching `*migration*`, `*alembic*`, `*prisma/migrations*`, `*db/migrate*`, `*knex*migrations*`).

If met:
- Output: "Migration files detected — dispatching migration safety reviewer..."
- Dispatch the `migration-check` agent with the migration file diffs.

If not met:
- Output: "INFO: No migration files — skipping migration safety review"

Wait for any conditional sub-agents to complete before synthesizing.

### Step 5: Key-Files Collection

After all sub-agents complete:
1. Iterate through sub-agent outputs in dispatch order
2. For each, find the `### Key Files` section
3. Extract file paths from the fenced code block
4. Build a unique list (first occurrence wins, skip duplicates)
5. Read up to 5 unique files using the Read tool
6. If a file doesn't exist, skip with warning and continue
7. Use the collected context for the synthesis phase

### Step 6: Synthesize Findings

Output: "Consolidating findings from {completed_count} sub-agents (6 core + {conditional_count} conditional)..."

If any sub-agent failed:
- Output: "⚠️ {failed_count} sub-agent(s) did not complete: {names}"
- Output: "Tip: Re-run with `--sequential` to retry"
- Continue with available findings

**Synthesis** is the orchestrator's job: combine all sub-agent findings and assign
an overall severity. The orchestrator does not re-derive findings, only merges and
deduplicates them.

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
BLOCKING findings with confidence < 75 are NEVER silently dropped. They go to a
dedicated "Needs Investigation" section at the end of the report with the label
"BLOCKING but low-confidence — human must verify."

**Severity Levels:**
- **BLOCKING** — Must fix before merge (standards violations, ship-stoppers, failing WI tests)
- **WARNING** — Should fix (code quality issues, potential problems)
- **INFO** — Consider (suggestions, potential improvements)

**Generate Merge Recommendation:**
- Any BLOCKING findings → **"DO NOT MERGE"**
- Only WARNING/INFO → **"SAFE TO MERGE (with notes)"**
- No findings → **"SAFE TO MERGE"**

### Step 6b: Simplify Offer (non-CI only)

If the merge recommendation is **"SAFE TO MERGE (with notes)"** (WARNING/INFO findings, no BLOCKING):

1. Ask the user: "Run /simplify on changed files to address minor issues?"
2. If approved: run `/simplify` on the changed files from Step 3, then re-run lint
3. If declined or in `--ci` mode: skip

### Step 7: Output

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

### Step 8: Work Item Generation (`--create-wi`)

For each BLOCKING or critical finding, create a work item using the scaffold CLI:

```bash
sp3cmar scaffold wi PR {slug}
```

This creates a WI file from the unified template. Then fill in the finding-specific details:
- Problem Statement: [Finding description with evidence]
- Acceptance Criteria: Issue fixed at {file}:{line}, tests added, PR review re-run clean

Output: "Created WI-PR-001 for: {finding title}"

## Guidelines

- **The orchestrator coordinates and synthesizes; sub-agents perform the checks.**
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
