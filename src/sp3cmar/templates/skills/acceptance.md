---
description: Verify a GitHub issue has explicit acceptance criteria + linkage before starting work
---

Read a GitHub issue, check it has the structure needed to start work safely (acceptance criteria, scope boundaries, parent/milestone linkage, freshness), and either green-light it or list what's missing. Reduces "implemented the wrong thing" rework.

## Arguments

`$ARGUMENTS` is the issue number (with or without `#`). Examples:

- `/sp3cmar-acceptance 4106`
- `/sp3cmar-acceptance #3887`
- `/sp3cmar-acceptance 4106 --strict` — fail loud on minor gaps
- `/sp3cmar-acceptance 4106 --start` — print suggested starting files and skip the green-light prompt

## Steps

### 1. Fetch the issue

```bash
gh issue view <number> --json number,title,body,labels,milestone,projectItems,state,closedAt,comments,url
```

If the issue is closed (`state: CLOSED`) and not currently being reopened, **stop** and report state + closed reason. Don't audit closed issues.

### 2. Identify the issue template

Look up the right template based on labels and branch-prefix conventions:

| Label / branch prefix | Template path |
|----------------------|---------------|
| `feat/`, `feature` label | `.github/ISSUE_TEMPLATE/feature.yml` |
| `fix/`, `bug` label | `.github/ISSUE_TEMPLATE/bug.yml` |
| `chore/`, `task` label | `.github/ISSUE_TEMPLATE/task.yml` |
| `spike/`, `spike` label | `.github/ISSUE_TEMPLATE/spike.yml` |
| `epic` label | `.github/ISSUE_TEMPLATE/epic.yml` |

Read the matching template (if present) to learn which fields the body is *supposed* to have. If no template exists, fall back to the generic checklist below.

### 3. Body content checks

For the issue body, verify presence of these sections (case-insensitive, common header variants like "Acceptance Criteria" / "Definition of Done" / "Done when" all count):

| Section | Required? | What to look for |
|---------|-----------|------------------|
| Description / Context | yes | Why this exists |
| Acceptance criteria | yes | Bulleted, testable conditions |
| Scope / Out of scope | nice-to-have | Boundaries called out |
| Test plan | nice-to-have for `feat/`, required for `fix/` | How to verify |
| Risks / dependencies | nice-to-have | Cross-PR or env coordination needed |

### 4. Linkage checks

- **Parent / epic**: search body and Sub-issues panel for "Parent:", "Epic:", or "Tracked by"
- **Milestone**: must be set if the repo uses milestones
- **Project board**: must be on the project board if the repo uses one (check `projectItems`)
- **Labels**: must have at least one type label (`feat`/`bug`/`chore`/`spike`/`epic`)

### 5. Freshness check

- **Last activity**: if `updatedAt` is older than 14 days and the issue claims to be "in progress" (assignee set or label like `in-progress`), flag as **stale** — re-confirm scope before starting
- **Comment churn**: if the latest 2-3 comments contradict the body, the issue body is out of date — flag it

### 6. Output

Print a structured report:

```markdown
## Acceptance check — #<number>: <title>

**State:** open / closed
**Type:** feat / fix / chore / spike / epic / unknown
**Assignee:** ...
**Last activity:** YYYY-MM-DD (X days ago)

### Body content
- [✓] Description present
- [✓] Acceptance criteria present (3 bullets)
- [✗] No "Out of scope" section
- [✗] No test plan

### Linkage
- [✓] Milestone: 0.7.7
- [✗] No parent epic linkage
- [✓] On project board

### Freshness
- [✓] Recent activity (2 days ago)

### Verdict
GREEN / YELLOW / RED — one-sentence reason.
```

**Green** = ready to start. Suggest 3-5 starting files (heuristic: keywords from issue body grep'd against the codebase + service READMEs).

**Yellow** = missing nice-to-haves. Suggest the user fill them in but don't block.

**Red** = missing required sections OR linkage. **Refuse to start work**. List what to add and where.

If `--start` is passed, skip the green-light prompt and go straight to the starting-files section.

## Output rules

Read-only audit. Do **not** create or modify any files.

If the user accepts a Red verdict and tells you to start anyway, log a warning and proceed — but include the gaps in your initial commit message body so reviewers know what wasn't pinned down.
