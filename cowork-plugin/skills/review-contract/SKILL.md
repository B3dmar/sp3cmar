---
name: review-contract
description: Validate frontend-backend API contract alignment
---

# API Contract Review

Validate that frontend API calls match backend route definitions across the full codebase.

## Overview

This skill performs a full-codebase API contract audit that detects:
1. **Ghost endpoints** — Backend routes nobody calls
2. **Phantom calls** — Frontend fetching nonexistent routes
3. **Shape drift** — Request/response mismatches across language boundaries

## Arguments

| Flag | Description |
|------|-------------|
| `--json` | Output machine-readable JSON |
| `--comment` | Post findings as GitHub PR comment |
| `--fix` | After review, offer to fix type drift via `/batch` |

## Instructions

### Step 1: Pre-Flight

Identify the project structure:

```bash
# Detect backend framework
ls src/**/routes* src/**/api* app/**/routes* app/**/api* 2>/dev/null | head -20

# Detect frontend API layer
ls src/**/api* src/**/fetch* src/**/client* app/**/api* 2>/dev/null | head -20
```

If the project has no clear frontend-backend split, output: "INFO: Single-layer project — contract review not applicable" and exit.

### Step 2: Map Backend Routes

Read backend route/endpoint files. For each route, extract:
- HTTP method (GET, POST, PUT, DELETE, PATCH)
- URL path (with path parameters)
- Expected request body schema (if applicable)
- Response shape

### Step 3: Map Frontend API Calls

Read frontend API/fetch files. For each call, extract:
- HTTP method
- Target URL
- Request body shape
- Expected response destructuring

### Step 4: Cross-Reference

Build a match matrix and classify each entry:

| Classification | Meaning |
|---------------|---------|
| **MATCHED** | Frontend call has a corresponding backend route |
| **GHOST** | Backend route with no frontend caller |
| **PHANTOM** | Frontend call to nonexistent backend route |
| **DRIFT** | Route exists but shapes don't match |

### Step 5: Dispatch Contract Reviewer

Dispatch the `reviewer-contract` agent with the collected route maps and diff context.

### Step 6: Output

#### Terminal Output (Default)

```markdown
# API Contract Review

## Route Matrix
| Method | Path | Backend | Frontend | Status |
|--------|------|---------|----------|--------|
| GET | /api/users | src/api/users.py:12 | src/lib/api.ts:45 | MATCHED |
| POST | /api/orders | src/api/orders.py:8 | — | GHOST |
| GET | /api/settings | — | src/lib/api.ts:78 | PHANTOM |

## Findings
| # | Severity | Confidence | Finding | Evidence |
|---|----------|------------|---------|----------|
| 1 | BLOCKING | 95 | Phantom call to /api/settings | `src/lib/api.ts:78` |

## Summary
{assessment}
```

#### JSON Output (`--json`)

```json
{
  "routes": [...],
  "findings": [...],
  "summary": "..."
}
```

### Step 7: Fix Type Drift (`--fix` only, skip in `--ci`)

When `--fix` is passed and DRIFT findings exist:

1. Ask the user for the fix direction: update **frontend** types to match backend, or update **backend** types to match frontend
2. From the DRIFT findings, generate a `/batch` instruction set to update the chosen side's type definitions
3. Present the plan with before/after type shapes
4. On approval: execute via `/batch`, then run the project's type checker (tsc/mypy)
5. On decline: skip — the review is still saved
