---
name: review-env
description: Audit environment variable consistency across configs
---

# Environment Config Review

Compare environment configurations across `.env*` files, docker-compose, infra configs, and application config models.

## Overview

Builds a variable-by-environment matrix and finds:
1. **Gaps** — Variable in code but missing from production config
2. **Drift** — Different defaults or types across environments
3. **Exposure** — Secrets in committed files

## Arguments

| Flag | Description |
|------|-------------|
| `--json` | Output machine-readable JSON |
| `--comment` | Post findings as GitHub PR comment |
| `--fix` | After review, offer to fill config gaps via `/batch` |

## Instructions

### Step 1: Discover Config Sources

```bash
# Find all env-related files
ls .env* docker-compose*.yml docker-compose*.yaml 2>/dev/null
ls **/terraform.tfvars **/*.tf railway.json vercel.json 2>/dev/null | head -20

# Find application config modules
grep -rl "BaseSettings\|dotenv\|process\.env\|os\.environ\|env\." src/ app/ lib/ 2>/dev/null | head -20
```

### Step 2: Extract Variables

For each source, extract all environment variable names and their values/defaults:

| Source Type | How to Extract |
|-------------|---------------|
| `.env*` files | Parse KEY=VALUE lines |
| docker-compose | Parse `environment:` blocks |
| Terraform/Railway/Vercel | Parse variable declarations |
| pydantic-settings | Parse `Field(...)` defaults and env names |
| `os.environ` / `process.env` | Grep for variable access patterns |

### Step 3: Build Matrix

Construct a variable × source matrix:

| Variable | .env.example | .env.dev | docker-compose | Code Default | Required? |
|----------|-------------|----------|----------------|-------------|-----------|
| DATABASE_URL | ✓ | ✓ | ✓ | — | Yes |
| API_KEY | ✓ | ✗ | ✗ | — | Yes |
| DEBUG | ✓ | ✓ | ✓ | False | No |

### Step 4: Dispatch Env Reviewer

Dispatch the `reviewer-env` agent with the variable matrix and config file locations.

### Step 5: Output

```markdown
# Environment Config Review

## Variable Matrix
{matrix table}

## Findings
| # | Severity | Confidence | Finding | Evidence |
|---|----------|------------|---------|----------|
| 1 | BLOCKING | 95 | DATABASE_URL missing from production | `.env.example:3` |

## Summary
{assessment}
```

### Step 6: Fill Config Gaps (`--fix` only, skip in `--ci`)

When `--fix` is passed:

1. From the variable matrix, identify variables missing from specific config files
2. Generate a `/batch` instruction set to add missing entries:
   - Use `.env.example` values as defaults where available
   - Use `CHANGEME` placeholder for secrets
3. Present the plan to the user with the list of additions per file
4. On approval: execute via `/batch`
5. On decline: skip — the review is still saved
