---
description: Audit dependency health, CVEs, unused deps, and license conflicts
---

# Dependency Health Review

Audit project dependencies for security, hygiene, and correctness.

## Overview

Checks:
1. **Known CVEs** — Dependencies with published security advisories
2. **Unused deps** — Declared but never imported
3. **License conflicts** — Incompatible licenses in the dependency tree
4. **Unpinned versions** — Missing or overly broad version constraints
5. **Outdated packages** — Major versions behind on security-sensitive deps

## Arguments

| Flag | Description |
|------|-------------|
| `--json` | Output machine-readable JSON |
| `--sequential` | Force sequential execution |

## Instructions

### Step 1: Identify Package Manager

```bash
# Detect manifest files
ls pyproject.toml requirements*.txt Pipfile package.json pnpm-lock.yaml Cargo.toml go.mod Gemfile 2>/dev/null
```

### Step 2: Run Available Audit Tools

Execute the appropriate audit commands for the detected package manager:

| Manager | Audit Command |
|---------|--------------|
| pip/uv | `uv pip audit 2>/dev/null \|\| pip-audit 2>/dev/null` |
| npm | `npm audit --json 2>/dev/null` |
| cargo | `cargo audit 2>/dev/null` |
| go | `govulncheck ./... 2>/dev/null` |

If audit tools aren't available, proceed with manual analysis.

### Step 3: Dispatch Deps Reviewer

Dispatch the `reviewer-deps` agent with:
- Manifest file contents
- Audit tool output (if available)
- Source code import inventory

### Step 4: Output

```markdown
# Dependency Health Review

## Dependency Summary
| Category | Count |
|----------|-------|
| Direct deps | N |
| Dev deps | N |
| Outdated (major) | N |
| Known CVEs | N |
| Unused | N |
| License issues | N |

## Findings
| # | Severity | Confidence | Finding | Evidence |
|---|----------|------------|---------|----------|
| 1 | BLOCKING | 95 | CVE-2024-XXXX in package-name | `pyproject.toml:15` |

## Summary
{assessment}
```
