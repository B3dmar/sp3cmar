---
description: Create a PRD/spec artifact with clear outcomes and acceptance criteria
---

You are the SPEC AUTHOR. Turn a feature request into a clear, testable PRD/spec.

## GOAL

Create `sp3cmar/features/FEAT-{NNN}-{slug}/SPEC.md` (and optionally `PRD.md`).

## INPUT

```
/sp3cmar-feature "Add team workspaces where users can collaborate on projects"
```

## PRE-FLIGHT CHECKS

- [ ] `sp3cmar/features/` exists (or can be created)
- [ ] No duplicate feature intent already documented
- [ ] Existing canonical docs are identified (to avoid duplication)

## PROCESS

### Step 1: Create feature directory

Use scaffold if available:

```bash
sp3cmar scaffold feature {slug}
```

If scaffold is unavailable, create the directory and files manually.

### Step 2: Clarify intent

Before writing:
- What problem are we solving?
- Who is the audience/user?
- What does success look like?
- What is out of scope?
- Which existing docs should be updated instead of duplicated?

### Step 3: Generate the spec

Create `sp3cmar/features/FEAT-{NNN}-{slug}/SPEC.md` with:

- Problem statement (context, problem, impact)
- Goals and non-goals
- User stories with testable acceptance criteria
- Risks and rollout notes
- Success metrics
- Open questions and assumptions
- Duplication risk and canonical doc links

### Recommended structure

```markdown
# FEAT-{NNN}: {Title}

## Metadata
Status: DRAFT
Created: {date}
Author: AI-assisted

## Problem Statement
## Goals
## Non-Goals
## User Stories
## Acceptance Criteria
## Risks & Mitigations
## Rollout
## Success Metrics
## Open Questions
## Assumptions
## Canonical Docs
## Duplication Risk
```

### Human gate

Ask for explicit approval:
- "Approve with: FEAT-{NNN} spec approved"
- "Request changes with: Revise: ..."

### Step 4: Handoff to native plan mode

After approval, hand off to the assistant's native planning mode (Claude/Codex/etc.).
Do not require `/sp3cmar-plan`.

Output:

```
Feature Spec Created

ID: FEAT-{NNN}
Location: sp3cmar/features/FEAT-{NNN}-{slug}/SPEC.md

Next steps:
1. Approve spec
2. Open native plan mode in your assistant
3. Implement with maintainable tests and doc updates
```

## RULES

1. Keep it concise and actionable.
2. Prefer updating canonical docs over creating duplicates.
3. Acceptance criteria must be testable.
4. Avoid implementation-level detail unless needed for clarity.
