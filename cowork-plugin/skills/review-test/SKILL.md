---
name: review-test
description: Audit test quality, coverage gaps, and test smells
---

# Test Quality Review

Audit test suite quality beyond coverage percentages.

## Overview

Detects:
1. **Untested critical paths** — Auth, payments, data mutations without test coverage
2. **Test smells** — Empty bodies, skips without reason, meaningless assertions
3. **CI config issues** — Tests not running, no thresholds, flaky retries hiding failures
4. **Missing negative tests** — Functions that raise but no error-path test

## Arguments

| Flag | Description |
|------|-------------|
| `--json` | Output machine-readable JSON |
| `--sequential` | Force sequential execution |

## Instructions

### Step 1: Map Test Infrastructure

```bash
# Identify test framework and config
ls pytest.ini pyproject.toml setup.cfg jest.config* vitest.config* .mocharc* 2>/dev/null

# Find test directories
ls -d tests/ test/ __tests__/ spec/ 2>/dev/null

# Check CI config for test execution
ls .github/workflows/* .gitlab-ci.yml Jenkinsfile 2>/dev/null
```

### Step 2: Map Critical Paths

Identify critical application paths that MUST have test coverage:
- Authentication and authorization flows
- Payment processing and financial calculations
- Data mutations (create, update, delete operations)
- Permission and access control checks
- External API integrations
- Data validation and sanitization

### Step 3: Dispatch Test Reviewer

Dispatch the `reviewer-test` agent with:
- Test file inventory
- Critical path map
- CI configuration

### Step 4: Output

```markdown
# Test Quality Review

## Coverage Map
| Critical Path | Test File | Status |
|--------------|-----------|--------|
| Auth login | tests/test_auth.py | COVERED |
| Payment processing | — | MISSING |

## Test Smells
| # | Smell | File | Evidence |
|---|-------|------|----------|
| 1 | Empty test body | tests/test_api.py:45 | `def test_create(): pass` |

## Findings
| # | Severity | Confidence | Finding | Evidence |
|---|----------|------------|---------|----------|
| 1 | BLOCKING | 90 | No tests for payment flow | `src/payments.py:12` |

## Summary
{assessment}
```
