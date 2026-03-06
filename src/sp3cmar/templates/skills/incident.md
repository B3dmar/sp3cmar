---
description: Incident response — trace errors, check deployments, generate postmortem
---

# Incident Response

Take an error or stack trace, trace it to source, check recent deployments, and generate a structured postmortem.

## Overview

Provides:
1. **Error tracing** — From stack trace to source code via grep + git blame
2. **Deployment correlation** — Check if the error appeared after a recent deployment
3. **Structured postmortem** — Timeline, root cause, impact, remediation, prevention

## Arguments

| Flag | Description |
|------|-------------|
| `$ARGUMENTS` | Error message, stack trace, or description of the incident |
| `--severity SEV` | Incident severity: SEV1 (critical), SEV2 (major), SEV3 (minor) (default: SEV2) |

## Instructions

### Step 1: Capture Error Context

Parse the provided error/stack trace. Extract:
- Error type and message
- File and line references from stack trace
- Timestamp (if available)
- Affected service or component

If no stack trace provided, ask: "Paste the error message or stack trace to investigate."

### Step 2: Trace to Source

```bash
# Find the files referenced in the stack trace
# For each file:line in the trace, read the source
```

For each source location:
1. Read the relevant code section
2. Check git blame for recent changes: `git log --oneline -5 {file}`
3. Identify the commit that introduced or last modified the failing code

### Step 3: Check Recent Deployments

```bash
# Check recent releases
gh release list --limit 5 2>/dev/null

# Check recent merges to main
git log main --oneline --merges -10

# Check recent deploys (if Railway/Vercel)
# railway logs 2>/dev/null || vercel ls 2>/dev/null
```

Correlate: did the error start after a specific deployment?

### Step 4: Identify Root Cause

Analyze:
- What changed in the identified commits?
- Is this a regression from a recent merge?
- Is this a latent bug triggered by new conditions?
- Is this an infrastructure/external service issue?

### Step 5: Generate Postmortem

**Output:** `sp3cmar/incidents/INC-{NNN}-{date}-{slug}.md`

```markdown
# Incident: INC-{NNN} — {title}

**Severity:** {SEV1|SEV2|SEV3}
**Status:** Investigating | Mitigated | Resolved
**Date:** {date}
**Duration:** {start} — {end|ongoing}

## Timeline

| Time | Event |
|------|-------|
| {time} | Error first reported |
| {time} | Investigation started |
| {time} | Root cause identified |
| {time} | Fix deployed |

## Error

```
{original error/stack trace}
```

## Root Cause

{Detailed explanation of what went wrong and why}

**Introducing commit:** {hash} — {message} ({author}, {date})
**File:** `{file}:{line}`

## Impact

- **Users affected:** {estimate}
- **Services affected:** {list}
- **Data impact:** {none | description}

## Remediation

### Immediate (done)
- [ ] {action taken}

### Short-term (this week)
- [ ] {follow-up action}

### Long-term (backlog)
- [ ] {prevention measure}

## Prevention

What would have caught this before production:
- [ ] {test that should exist}
- [ ] {monitoring that should trigger}
- [ ] {review check that should catch this pattern}

## Lessons Learned

1. {lesson}
2. {lesson}
```

### Step 6: Link to Work Items

For each remediation and prevention item, suggest creating a tracked work item:
- Short-term items → work items with deadline
- Long-term items → backlog work items
- Prevention items → process improvement work items
