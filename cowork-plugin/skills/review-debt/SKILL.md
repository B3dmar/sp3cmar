---
name: review-debt
description: Quantify tech debt — TODOs, hotspots, and trend tracking
---

# Tech Debt Review

Quantify and categorize technical debt across the codebase.

## Overview

Provides:
1. **Debt inventory** — TODO/FIXME/HACK markers categorized by risk area
2. **Hotspot analysis** — High-debt files that also have high git churn
3. **Trend tracking** — Versioned reports in `sp3cmar/reviews/debt/` for delta comparison
4. **Cross-references** — Links to `review-codebase` and `review-kill` findings

## Arguments

| Flag | Description |
|------|-------------|
| `--json` | Output machine-readable JSON |
| `--sequential` | Force sequential execution |
| `--fix` | After review, offer to auto-fix mechanical debt via `/batch` |

## Instructions

### Step 1: Mode Selection

1. Check whether `sp3cmar/reviews/debt/` exists. If not, create it.
2. Scan for existing `v*/REPORT.md` folders
3. If no prior reports → run **FULL** review → create `v001/REPORT.md`
4. If prior reports exist → load latest as baseline → run **DELTA** review → create `v{N+1}/REPORT.md`

### Step 2: Inventory Debt Markers

```bash
# Find all debt markers
grep -rn "TODO\|FIXME\|HACK\|XXX\|WORKAROUND\|TEMPORARY\|TECH_DEBT" --include="*.py" --include="*.ts" --include="*.js" --include="*.go" --include="*.rs" src/ app/ lib/ 2>/dev/null | head -100
```

### Step 3: Identify Hotspots

```bash
# Find high-churn files (most commits in last 90 days)
git log --since="90 days ago" --name-only --pretty=format: | sort | uniq -c | sort -rn | head -20
```

Cross-reference churn data with debt marker density to find hotspots.

### Step 4: Dispatch Debt Reviewer

Dispatch the `reviewer-debt` agent with:
- Debt marker inventory
- Git churn data
- Previous report baseline (if delta mode)

### Step 5: Load Cross-References (Optional)

```bash
# Load latest codebase review if available
ls -t sp3cmar/reviews/codebase/v*/REVIEW.md 2>/dev/null | head -1

# Load latest kill report if available
ls -t sp3cmar/reviews/kill-reports/v*/REPORT.md 2>/dev/null | head -1
```

Cross-reference findings with architecture issues and ship-stoppers.

### Step 6: Output

**Output:** `sp3cmar/reviews/debt/v{N}/REPORT.md`

```markdown
# Tech Debt Report v{N}
Generated: {date}
Mode: {FULL | DELTA from v{N-1}}

## Debt Inventory
| # | Category | File:Line | Marker | Age | Risk |
|---|----------|-----------|--------|-----|------|
| 1 | Security | src/auth.py:45 | TODO: add rate limiting | 6mo | HIGH |

## Hotspots
| File | Debt Markers | Commits (90d) | Risk Score |
|------|-------------|---------------|------------|
| src/api/handler.py | 8 | 23 | CRITICAL |

## Findings
| # | Severity | Confidence | Finding | Evidence |
|---|----------|------------|---------|----------|
| 1 | BLOCKING | 88 | Deferred auth in critical path | `src/auth.py:45` |

## Summary
{assessment}
```

### Step 7: Auto-Fix Mechanical Debt (`--fix` only, skip in `--ci`)

When `--fix` is passed:

1. Filter the debt inventory for **mechanical markers** — items with clear inline instructions (e.g., `TODO: rename to X`, `FIXME: add type annotation`, `HACK: replace with proper config lookup`)
2. Exclude vague markers (e.g., `TODO: refactor this`, `FIXME: improve performance`)
3. Group fixable markers by category (naming, typing, config, cleanup)
4. Generate a `/batch` instruction set describing each fix
5. Present the plan to the user with marker count per category
6. On approval: execute via `/batch`, then re-run lint checks
7. On decline: skip — the report is still saved

### Delta Mode (When Baseline Exists)

Include additional sections:
- **Trend:** debt count this version vs previous
- **Resolved:** markers removed since last report
- **New:** markers added since last report
- **Stale:** markers present in both reports with no progress
