---
description: Unified code review — run one or all review types
---

# Code Review

Run targeted or comprehensive code reviews. Each subcommand dispatches specialized reviewer agents.

## Arguments

`$ARGUMENTS` should start with one of:
- `all` — run all non-overlapping reviews in parallel
- `pr [flags]` — PR review (standards, ship-stoppers, correctness)
- `codebase [flags]` — architecture review with delta tracking
- `kill [flags]` — adversarial kill case review
- `test` — test quality and coverage audit
- `debt [flags]` — tech debt quantification (TODOs, hotspots)
- `deps` — dependency health, CVEs, licenses
- `env` — environment variable consistency
- `contract` — frontend-backend API contract alignment

Common flags (supported by most subcommands):
- `--sequential` — force sequential agent execution (debug/fallback)
- `--json` — output machine-readable JSON
- `--fix` — auto-fix mechanical issues after review (codebase, debt, env, contract)
- `--comment` — post findings as GitHub PR comment (pr, env, contract)

## Shared Preamble (runs for all subcommands)

### Phase 0: Ground in prior decisions (if 3ngram MCP is available)

Before dispatching any reviewer agent, gather prior institutional memory so findings are framed against known decisions, not re-discovered from scratch:

1. Call `mcp__3ngram-prod-oss__briefing` with `brief=true` and `sections=["blockers","stale","recent_decisions"]` — surfaces active blockers, stale commitments, and recent architectural decisions in <5KB.
2. Call `mcp__3ngram-prod-oss__search` with a topic summary of the review scope (e.g. for `codebase`: "architecture modularity contract drift"; for `kill`: "security reliability cost ship-stopper"). Limit 8, `brief=true`.
3. If any returned memory indicates a blocker on the current scope (e.g. "pipeline X is broken, do not add rules until fixed"), pause and surface to the user before dispatch.
4. Pass the briefing + search results to every reviewer agent as "prior decisions / known blockers" context. Reviewers should reference a relevant memory ID instead of re-flagging a known accepted pattern.

If 3ngram MCP is unavailable (tool missing or error), log a one-line note and continue — do not block the review.

### Load Project Standards

Search for project standards in common locations:

```bash
ls ARCHITECTURE.md docs/ARCHITECTURE.md CONTRIBUTING.md docs/CONTRIBUTING.md SECURITY.md docs/SECURITY.md 2>/dev/null
ls CLAUDE.md .cursorrules .github/copilot-instructions.md AGENTS.md 2>/dev/null
ls sp3cmar/constitution/enforced sp3cmar/docs-index 2>/dev/null
```

If found: load and use as baseline for all reviewers. If not: review against general best practices.

### Deterministic Pre-Checks (for codebase, kill, all)

Run `sp3cmar check --json` if the CLI is available. Capture ruff violations, mypy errors, pytest failures. Include in agent context: "Focus on issues tools cannot catch."

If CLI not available: skip with info message and proceed.

### Confidence Scoring (applies to all outputs)

Every finding MUST include severity (BLOCKING/WARNING/INFO) and confidence (0-100).

**Filtering rules:**
- Default: show only findings with confidence >= 75
- `--show-all`: show all findings
- BLOCKING findings with confidence < 75 go to "Needs Investigation" section (never silently dropped)
- Sort: severity DESC, then confidence DESC

---

## Subcommand: `pr`

Dispatch the `sp3cmar-review-pr` agent with:
- Current branch name and base branch (default: staging)
- The full diff (`git diff <base>...HEAD`)
- Changed files list
- Loaded project standards
- PR-specific flags: `--base`, `--comment`, `--json`, `--ci`, `--strict`, `--create-wi`

The agent handles: standards review, ship-stopper check, work item verification, code quality, hardcoded values, correctness, conditional contract/migration review.

## Subcommand: `codebase`

Dispatch the `sp3cmar-review-codebase` agent with:
- Project standards from preamble
- Deterministic pre-check results
- Previous report baseline (from `sp3cmar/reviews/codebase/`) if delta mode
- Flags: `--sequential`, `--fix`

The agent handles: 7 sub-reviewers (architecture, data, modularity, consistency, dependency health, tech debt, rewrite assessment) in 2-phase parallel dispatch, consolidation, and versioned output.

## Subcommand: `kill`

Dispatch the `sp3cmar-review-kill` agent with:
- Project standards from preamble
- Deterministic pre-check results
- Previous report baseline (from `sp3cmar/reviews/kill-reports/`) if delta mode
- Flags: `fresh`/`baseline`/`force full`, `--sequential`, `--no-teams`

The agent handles: 6 adversarial review teams, ship-stopper identification, versioned output with delta tracking.

## Subcommand: `test`

### Step 1: Map Test Infrastructure

```bash
ls pytest.ini pyproject.toml setup.cfg jest.config* vitest.config* .mocharc* 2>/dev/null
ls -d tests/ test/ __tests__/ spec/ 2>/dev/null
ls .github/workflows/* .gitlab-ci.yml Jenkinsfile 2>/dev/null
```

### Step 2: Map Critical Paths

Identify application paths that MUST have coverage: auth, payments, data mutations, permissions, external APIs, validation.

### Step 3: Dispatch `reviewer-test` agent

Provide: test file inventory, critical path map, CI configuration.

### Step 4: Output

Findings table with coverage map, test smells, and critical path gaps.

## Subcommand: `debt`

### Step 1: Mode Selection

Check `sp3cmar/reviews/debt/` for prior versioned reports. Full or delta mode.

### Step 2: Inventory Debt Markers

```bash
grep -rn "TODO\|FIXME\|HACK\|XXX\|WORKAROUND\|TEMPORARY\|TECH_DEBT" --include="*.py" --include="*.ts" --include="*.js" src/ app/ lib/ 2>/dev/null | head -100
```

### Step 3: Identify Hotspots

```bash
git log --since="90 days ago" --name-only --pretty=format: | sort | uniq -c | sort -rn | head -20
```

Cross-reference churn with debt density.

### Step 4: Dispatch `reviewer-debt` agent

Provide: debt inventory, churn data, previous baseline (if delta).

### Step 5: Cross-Reference

Load latest codebase and kill reports if available for cross-referencing.

### Step 6: Output

Versioned report at `sp3cmar/reviews/debt/v{N}/REPORT.md`.

If `--fix`: filter mechanical markers, generate batch instructions, execute on approval.

## Subcommand: `deps`

### Step 1: Identify Package Managers

```bash
ls package.json pyproject.toml Cargo.toml go.mod Gemfile 2>/dev/null
```

### Step 2: Run Audit Tools

```bash
npm audit --json 2>/dev/null || true
pip-audit --format json 2>/dev/null || true
```

### Step 3: Dispatch `reviewer-deps` agent

Provide: dependency manifests, lock files, audit results.

### Step 4: Output

Findings table with CVEs, outdated packages, unused deps, license conflicts.

## Subcommand: `env`

### Step 1: Collect Environment Sources

```bash
ls .env* .env.example docker-compose*.yml vercel.json railway.json 2>/dev/null
grep -rn "os.environ\|process.env\|getenv" --include="*.py" --include="*.ts" --include="*.js" src/ app/ 2>/dev/null | head -50
```

### Step 2: Dispatch `reviewer-env` agent

Provide: all env files, code references to env vars, deployment configs.

### Step 3: Output

Findings table with missing vars, inconsistencies, exposed secrets, undocumented vars.

If `--fix`: generate fixes for consistency issues.
If `--comment`: post as GitHub PR comment.

## Subcommand: `contract`

### Step 1: Identify API Boundaries

```bash
# Backend routes
grep -rn "app\.\(get\|post\|put\|delete\|patch\)\|@router\.\|@app\.route" --include="*.py" --include="*.ts" --include="*.js" src/ app/ 2>/dev/null | head -30

# Frontend API calls
grep -rn "fetch\|axios\|useSWR\|useQuery" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" src/ app/ 2>/dev/null | head -30
```

### Step 2: Dispatch `reviewer-contract` agent

Provide: backend route definitions, frontend API calls, OpenAPI/schema files if present.

### Step 3: Output

Findings table with mismatched endpoints, missing error handling, type drift.

If `--fix`: generate alignment fixes.
If `--comment`: post as GitHub PR comment.

---

## Subcommand: `all`

Run all non-overlapping reviews in parallel. Excludes `pr` (requires branch context).

### Execution Plan

**Group A — Independent leaf reviews (parallel):**
Dispatch these 5 simultaneously:
- `test` (reviewer-test agent)
- `debt` (reviewer-debt agent)
- `deps` (reviewer-deps agent)
- `env` (reviewer-env agent)
- `contract` (reviewer-contract agent, conditional on frontend+backend existing)

**Group B — Architecture review (after Group A):**
- `codebase` (sp3cmar-review-codebase agent, benefits from Group A context)

**Group C — Adversarial review (after Group B):**
- `kill` (sp3cmar-review-kill agent, benefits from codebase findings)

### Consolidated Output

After all groups complete:

```markdown
# Full Review — YYYY-MM-DD

## Summary
- {N} BLOCKING findings across {M} review types
- {K} WARNING findings
- Top risk areas: {list}

## By Review Type
### Test Quality
{test findings}

### Tech Debt
{debt findings}

### Dependencies
{deps findings}

### Environment Config
{env findings}

### API Contract
{contract findings}

### Architecture
{codebase executive summary}

### Kill Case
{kill case verdict + top ship-stoppers}

## Cross-Cutting Findings
{findings that appeared in multiple reviews, deduplicated}

## Action Items (prioritized)
1. {BLOCKING items first}
2. {WARNING items}
3. {Improvement items}
```

Deduplicate findings that appear in multiple reviews (e.g., a TODO flagged by both debt and codebase).
