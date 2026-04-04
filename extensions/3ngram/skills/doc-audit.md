---
description: Cross-reference documentation with 3ngram commitments and decisions
---

# Documentation Audit (3ngram-Enhanced)

Audit project documentation for drift against 3ngram-tracked commitments and decisions.

## Steps

### 1. Load 3ngram Context
- `engram://commitments` — all open commitments
- `mcp__3ngram__search_memories` with topic "decision", `memory_type="decision"`, and project/scope matching this project
- `mcp__3ngram__search_memories` with topic "architecture", `memory_type="decision"`, and project/scope matching this project

### 2. Scan Documentation
Identify key documentation files:
- `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`
- `docs/` directory contents
- API documentation
- Architecture decision records (ADRs)

### 3. Cross-Reference
For each commitment and decision from 3ngram:
1. Check if it's reflected in documentation
2. Flag drift: decisions made but docs not updated
3. Flag stale docs: documentation that contradicts recent decisions

### 4. Produce Report

```
## Documentation Audit Report

### Drift Detected
| Decision/Commitment | Expected In | Status |
|---------------------|-------------|--------|
| [memory summary]    | README.md   | Missing |

### Stale Documentation
| File | Issue | Related Memory |
|------|-------|----------------|
| docs/api.md | Contradicts decision #1234 | [summary] |

### Up-to-Date
- {count} decisions properly documented
- {count} commitments reflected in docs

### Recommendations
1. [Specific doc updates needed]
```

## Graceful Degradation
If 3ngram MCP is not available, perform a standard documentation audit
checking for internal consistency, broken links, and staleness indicators
(last-modified dates, version references).
