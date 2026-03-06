---
description: Auto-fix review findings — classify, plan, and execute via /simplify and /batch
---

# Fix Review Findings

Meta-skill that reads a review report, classifies findings by fixability, and executes approved fixes.

## Arguments

`$ARGUMENTS` controls behavior:
- `<report-path>` — path to a specific review report file
- `--latest debt|codebase|env|contract` — load the most recent report of the given type
- `--dry-run` — classify and plan only, do not execute fixes

## Instructions

### Step 1: Load Report

Resolve the report path:

```bash
# If --latest <type> was passed
ls -t sp3cmar/reviews/{type}/v*/REPORT.md sp3cmar/reviews/{type}/v*/REVIEW.md 2>/dev/null | head -1

# Otherwise use the explicit path from $ARGUMENTS
```

If no report found: "ERROR: No report found. Run a review first." and stop.

### Step 2: Parse Findings

Extract the findings table from the report. For each finding, capture:
- Severity (BLOCKING, WARNING, INFO)
- Confidence score
- File:line evidence
- Description

### Step 3: Classify Fixability

Classify each finding into one of three categories:

| Category | Criteria | Action |
|----------|----------|--------|
| **mechanical-single** | Single-file, localized fix (rename, add annotation, fix import) | `/simplify` |
| **mechanical-bulk** | Same fix pattern across multiple files (normalize naming, add config entries) | `/batch` |
| **architectural** | Requires design decisions, multi-module changes, or human judgment | Manual report only |

Rules:
- **Never auto-fix BLOCKING findings** — always report as architectural regardless of fixability
- Findings with confidence < 75 are always classified as architectural
- When uncertain, classify as architectural (safer)

### Step 4: Present Plan

Output a summary grouped by category:

```markdown
## Fix Plan

### Mechanical (single-file) — N findings via /simplify
| # | Finding | File:Line | Action |
|---|---------|-----------|--------|

### Mechanical (bulk) — N findings via /batch
| # | Finding | Files | Action |
|---|---------|-------|--------|

### Architectural (manual) — N findings
| # | Finding | File:Line | Why Manual |
|---|---------|-----------|------------|
```

If `--dry-run`: stop here.

### Step 5: Execute Fixes

On user approval:

1. Run `/simplify` fixes first (single-file changes are lower risk)
2. Run `/batch` fixes second (bulk changes)
3. After each batch: re-run lint checks
4. Report results: files changed, lint status, any failures

### Step 6: Summary

Output final status:
- Findings fixed (count by category)
- Findings skipped (architectural, with brief reason each)
- Lint status after fixes
- Suggestion: "Review architectural findings manually or create work items"
