# Codebase Architecture Review

You are the Review Orchestrator for this repository.

## GOAL

Maintain a versioned architecture/codebase review in `sp3cmar/reviews/codebase/`.

## MODE SELECTION (Execute These Steps)

1. Check whether `sp3cmar/reviews/codebase/` exists. If not, create it.
2. Scan for existing `v*/REVIEW.md` folders (e.g., v001, v002)
3. If no prior reports exist (missing or not found) → run **FULL** review → create `v001/REVIEW.md`
4. If prior reports exist → identify latest version → load as baseline → run **DELTA** review → create `v{N+1}/REVIEW.md`

**Output:** `sp3cmar/reviews/codebase/v{N}/REVIEW.md`

## STEP 0: LOAD PROJECT STANDARDS

Search for project standards in common locations:

```bash
# Architecture / code standards / security
ls ARCHITECTURE.md docs/ARCHITECTURE.md CONTRIBUTING.md docs/CONTRIBUTING.md SECURITY.md docs/SECURITY.md 2>/dev/null

# AI assistant instructions (often contain project conventions and anti-patterns)
ls CLAUDE.md .cursorrules .github/copilot-instructions.md AGENTS.md 2>/dev/null

# Project-specific standards index (sp3cmar convention)
ls sp3cmar/constitution/enforced sp3cmar/docs-index 2>/dev/null
```

If found:
1. Read them for architecture, data, modularity, and documentation expectations
2. Flag standards violations as findings throughout the review
3. Suggest follow-up work items in the report summary

If nothing found: proceed without — reviewers evaluate against general best practices.

## STEP 0b: DETERMINISTIC PRE-CHECKS

Run `sp3cmar check --json` and capture the output. Summarize:

"Deterministic checks: {N} ruff violations, {M} mypy errors, {K} test failures."

Include this summary in each reviewer agent's context:
"Focus your review on issues deterministic tools cannot catch. Known tool findings: {summary}"

Add a "Deterministic Checks" section at the beginning of the review output (before agent sections):
```markdown
## Deterministic Checks
- ruff: {N} violations
- mypy: {M} errors
- pytest: {K} failures
```

If check fails: warn "Fix deterministic violations first" but proceed (reviews are advisory).

## EVIDENCE RULES (STRICT)

- No generic advice. Every claim must cite evidence.
- HIGH severity items MUST include: `file_path:line_start–line_end`
- If you cannot provide file:line evidence, downgrade severity.
- Reference specific functions, classes, or modules by name.

## SCORING RUBRIC (0–5)

| Score | Meaning |
|-------|---------|
| 0 | broken/absent |
| 1 | poor |
| 2 | inconsistent |
| 3 | acceptable |
| 4 | strong |
| 5 | excellent |

## Arguments

| Flag | Description |
|------|-------------|
| `--sequential` | Force sequential reviewer execution A → B → C → D → E (debug/fallback) |
| `--fix` | After review, offer to auto-fix consistency issues via `/batch` |
## SUB-REVIEWERS (A–E)

Spawn 7 independent sub-reviewers. Each evaluates ONLY their assigned dimension (~400–800 words each).

### Sub-Reviewer Dispatch

**EXECUTION MODE:** Check for `--sequential` flag in arguments.
- If `--sequential`: Execute Reviewers A → B → C → D → E in order, one at a time
- Otherwise: Execute A-D, F, G in parallel (Phase 1), then E sequentially (Phase 2 - E depends on A-G summaries)

Output: "Dispatching 6 reviewers in parallel (Phase 1)..."

### [PARALLEL-START: id=codebase-reviewers-phase1]

IMPORTANT: Invoke Reviewers A, B, C, D, F, G as parallel Task tool calls in a SINGLE response. Do NOT wait for one reviewer to complete before starting the next.

### [PARALLEL] Reviewer A — Solution Architecture

**Deliverables:**
- Architecture score (0–5) + justification
- System boundary assessment
- Dependency direction issues (file:line for HIGH)
- Top 5 architectural risks (ranked, severity + evidence)
- 3 recommended architectural moves

**Focus Areas:**
- Layer separation (handlers → services → repositories)
- Dependency injection patterns
- Configuration management
- External integration boundaries

### [PARALLEL] Reviewer B — Data & Database Design

**Deliverables:**
- Data/DB score (0–5) + justification
- DB/schema inventory (key schemas/tables/models, their role)
- Modeling issues (constraints, naming, normalization, migrations) with severity + evidence
- Data ownership map (which module owns writes to which models)
- Top 3 data risks + remediation

**Focus Areas:**
- Schema design and normalization
- Migration safety and reversibility
- Data access patterns
- Index coverage for common queries

### [PARALLEL] Reviewer C — Modularity & Code Organization

**Deliverables:**
- Modularity score (0–5) + justification
- Coupling hotspots (with examples)
- Cohesion problems (with examples)
- Recommended module boundaries (tree proposal)
- "If I were new here" notes: where would I add feature X?

**Focus Areas:**
- Package/module structure
- Import graph analysis
- Circular dependencies
- Feature isolation

### [PARALLEL] Reviewer D — Consistency & Engineering Standards

**Deliverables:**
- Consistency score (0–5) + justification
- House standards detected (explicit and implicit)
- Inconsistency clusters: 5–10 recurring divergences with examples
- Proposed minimal standards (10–15 bullet rules) tailored to THIS codebase
- Quick wins (1–2 day effort items)

**Focus Areas:**
- Naming conventions
- Error handling patterns
- Logging practices
- Testing patterns

### [PARALLEL] Reviewer F — Dependency Health

**Deliverables:**
- Dependency health score (0–5) + justification
- Outdated packages with security implications
- Known CVEs with severity assessment
- Unused dependencies (declared but never imported)
- License compatibility analysis
- Unpinned or overly broad version constraints

**Focus Areas:**
- Security vulnerabilities in dependency tree
- Supply chain risk (unmaintained deps, single-maintainer packages)
- Dev/prod dependency separation
- Version pinning strategy

### [PARALLEL] Reviewer G — Technical Debt

**Deliverables:**
- Tech debt score (0–5) + justification
- TODO/FIXME/HACK inventory categorized by risk area
- Debt hotspots (high marker density + high git churn)
- Stale debt (markers > 6 months old with no associated issue)
- Debt in critical paths (auth, data integrity, payments)
- Trend assessment (growing/shrinking based on git history)

**Focus Areas:**
- Debt markers in security-critical code
- Deferred error handling in production paths
- Deprecated API usage
- Legacy patterns that fight the architecture

### [PARALLEL-END: id=codebase-reviewers-phase1]

Output: "Phase 1 complete. {completed}/6 reviewers finished."

If any Phase 1 reviewer failed:
- Output: "⚠️ {failed}/6 reviewers did not complete: {names}"
- Output: "Tip: Re-run with `--sequential` to retry"
- Note: Reviewer E may have incomplete context

Output: "Executing Reviewer E (depends on A-D summaries)..."

### [SEQUENTIAL: depends-on=codebase-reviewers-phase1]

### Reviewer E — Rewrite vs Refactor Assessment

**Deliverables:**
- Rewrite/refactor score (0–5) + justification
- Exemplars: 3–6 files/modules as reference patterns (why they're good)
- Refactor candidates: 5–10 items (why, what to do)
- Rewrite candidates: 3–8 items ("why refactor won't work" + target shape)
- Stop doing / Start doing / Keep doing

**Focus Areas:**
- Technical debt hotspots
- Code that fights the architecture
- Legacy patterns that should be retired
- Modern patterns to adopt

### [SEQUENTIAL-END]

Proceed to Consolidation Phase with all 7 reviewer outputs.

### Key-Files Collection

After all agents complete:
1. Iterate through agent outputs in dispatch order
2. For each agent, find the `### Key Files` section
3. Extract file paths from the fenced code block
4. Build a unique list (first occurrence wins, skip duplicates)
5. Read up to 5 unique files using the Read tool
6. If a file doesn't exist, skip with warning and continue
7. Use the collected context for the consolidation phase

## CONSOLIDATION PHASE (MANDATORY)

Output: "Consolidating findings from all 7 reviewers..."

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

After A–E finish, produce unified report with:

### 1. Executive Summary (≤10 bullets)
- Overall health assessment
- Critical findings
- Key recommendations

### 2. Conflicts & Disagreements
- List any reviewer disagreements
- Resolve with reasoning
- Document minority opinions

### 3. Risk Register (Top 10)
Rank by Impact × Likelihood:

| ID | Risk | Impact | Likelihood | Evidence | Mitigation |
|----|------|--------|------------|----------|------------|
| R-001 | {risk} | H/M/L | H/M/L | file:line | {action} |

### 4. Roadmap — NOW / NEXT / LATER
Realistic sequencing of improvements:

**NOW (This Sprint):**
- {item with evidence}

**NEXT (Next 2-4 Weeks):**
- {item with evidence}

**LATER (Backlog):**
- {item with evidence}

### 5. Guardrails-as-Code Mapping
For each standard identified:

| Standard | Enforceable? | Tool/Config | If No: Enforcement |
|----------|--------------|-------------|-------------------|
| {standard} | Yes/No | ruff/mypy/eslint/CI | docs + PR checklist |

### 6. Guiding Principles (3–5)
Derived from what works well in this codebase:
- {principle 1}
- {principle 2}
- {principle 3}

### 7. Documentation Recommendations
What documentation should exist:
- ARCHITECTURE.md: {recommendation}
- DATA_MODEL.md: {recommendation}
- CONTRIBUTING.md: {recommendation}

## AUTO-FIX CONSISTENCY (`--fix` only, skip in `--ci`)

When `--fix` is passed:

1. Extract Reviewer D (Consistency & Engineering Standards) findings
2. Identify **dominant patterns** — the convention used in the majority of cases
3. Identify **minority variants** — deviations from the dominant pattern
4. Generate a `/batch` instruction set to normalize minority variants to the dominant pattern
5. Present the plan to the user with before/after examples and file counts
6. On approval: execute via `/batch`, then re-run deterministic checks from Step 0b
7. On decline: skip — the review is still saved

Only fix mechanical consistency issues (naming, formatting, import ordering). Never auto-fix architectural findings.

## STANDARDS COMPLIANCE

If project standards were loaded in Step 0, check each relevant standard and report:

| Principle | Reference | Status | Evidence |
|-----------|-----------|--------|----------|
| {principle from standards doc} | {doc: section ref} | COMPLIANT / VIOLATION | {file:line or N/A} |

### Standards Violations (if any)

List violations that should become follow-up work items:

| ID | Principle Violated | Evidence | Severity | Suggested WI |
|----|-------------------|----------|----------|--------------|
| CV-001 | {principle} | file:line | Critical/High/Medium | {brief description} |

## DELTA MODE (Only When Baseline Exists)

Include these additional sections when running against a previous review:

### A) Delta Summary
- Overall trend: **improved** / **stable** / **regressed**
- Score changes by category:

| Reviewer | Previous | Current | Trend |
|----------|----------|---------|-------|
| A - Architecture | X/5 | Y/5 | ⬆️/➡️/⬇️ |
| B - Data | X/5 | Y/5 | ⬆️/➡️/⬇️ |
| C - Modularity | X/5 | Y/5 | ⬆️/➡️/⬇️ |
| D - Consistency | X/5 | Y/5 | ⬆️/➡️/⬇️ |
| E - Rewrite/Refactor | X/5 | Y/5 | ⬆️/➡️/⬇️ |
| F - Dependencies | X/5 | Y/5 | ⬆️/➡️/⬇️ |
| G - Tech Debt | X/5 | Y/5 | ⬆️/➡️/⬇️ |

### B) Findings Change Log

Classify each major finding from baseline:

| Status | Meaning |
|--------|---------|
| ✅ RESOLVED | Fixed since last review |
| 🔁 UNCHANGED | Still present, same state |
| ❌ REGRESSED | Got worse |
| 🆕 NEW | Not in baseline |

For each finding:
- Baseline reference (previous finding ID)
- Current evidence (file:line)
- Impact statement

### C) Roadmap Delta
- Items **completed** since last review
- Items **newly added**
- Items **reprioritized** (with reasoning)

## OUTPUT FORMAT

Create the review directory using the scaffold CLI:

```bash
sp3cmar scaffold review codebase
```

This creates the next versioned directory `sp3cmar/reviews/codebase/v{N}/` with a REVIEW.md skeleton.

Then populate the review content in:
```
sp3cmar/reviews/codebase/v{N}/REVIEW.md
```

Structure:
```markdown
# Codebase Review v{N}
Generated: {date}
Mode: {FULL | DELTA from v{N-1}}

## [A] Architecture Report
Score: X/5
{content}

## [B] Data & Database Report
Score: X/5
{content}

## [C] Modularity Report
Score: X/5
{content}

## [D] Consistency & Standards Report
Score: X/5
{content}

## [E] Rewrite vs Refactor Report
Score: X/5
{content}

## [F] Dependency Health Report
Score: X/5
{content}

## [G] Technical Debt Report
Score: X/5
{content}

## [Consolidated] Executive Summary
## [Consolidated] Conflicts & Resolutions
## [Consolidated] Risk Register
## [Consolidated] Roadmap
## [Consolidated] Guardrails-as-Code Mapping
## [Consolidated] Guiding Principles
## [Consolidated] Documentation Recommendations

## Standards Compliance
{Sp3cMar integration section}

{# Delta sections if applicable #}
## [Delta] Summary
## [Delta] Findings Change Log
## [Delta] Roadmap Delta
```

## EXECUTION NOTES

- Be opinionated, specific, and pragmatic
- Avoid generic advice — everything must have evidence
- Assume experienced engineering audience
- Start by exploring the codebase structure to understand what you're reviewing
- Cross-reference findings with project standards
- Findings should include actionable follow-up work item suggestions

## WORK ITEM LINKAGE

After completing this review:
1. Convert findings into tracked work items using your project workflow
2. Link work items to specific findings
3. Enable delta tracking in future reviews

When a work item linked to a finding is marked DONE, the next delta review should mark that finding as ✅ RESOLVED.
