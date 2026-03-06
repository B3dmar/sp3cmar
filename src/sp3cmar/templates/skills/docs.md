---
description: Create and maintain high-quality documentation with deduplication discipline
---

# Documentation Workflow

Create or improve documentation while following practical best practices and avoiding duplicate sources of truth.

## Core Documentation Principles

- Write for a specific audience and job-to-be-done.
- Prefer clear, concrete language over broad or clever wording.
- Lead with outcomes and fast path steps; add depth below.
- Keep docs task-oriented: one page should solve one core problem well.
- Use examples where ambiguity is likely (commands, inputs, outputs, edge cases).
- Make docs scannable with short sections, descriptive headings, and lists.
- Minimize maintenance burden: avoid duplicate sources of truth.
- Update canonical docs in place instead of creating overlapping pages.
- Link to related pages for context; do not copy large sections across files.
- Include update triggers so docs stay aligned with code and workflows.

## Scope

Use project-managed docs paths only, unless explicitly asked otherwise.
Default managed root is `sp3cmar/` (or the project's canonical docs root if different).

## Workflow

### 1) Understand the user and task

- Identify audience and use case first.
- Confirm whether this should be tutorial, how-to, reference, or explanation content.

### 2) Find existing canonical docs before writing

- Search for existing docs that already cover the topic.
- If overlap exists, update the canonical doc instead of creating a near-duplicate.

### 3) Draft with clear structure

- Lead with purpose and outcomes.
- Keep steps actionable and concrete.
- Include examples where ambiguity risk is high.
- Keep wording concise and scannable.

### 4) Run duplication + quality pass

Before finalizing, check:
- Is there another doc with the same intent?
- Does this doc introduce conflicting definitions?
- Can this content be merged into an existing canonical page?
- Are terms consistent with existing docs?

### 5) Finalize with maintenance cues

- Add update triggers (what changes should prompt doc updates).
- Link to adjacent docs rather than repeating the same explanation.

## Output Requirements

- Include a short "Audience" line.
- Include "When to update this doc" section.
- Include links to canonical related docs.
- If duplicate risk exists, include a "Duplication Risk" note with merge recommendation.
