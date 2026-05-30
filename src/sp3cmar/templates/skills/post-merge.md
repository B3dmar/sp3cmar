---
description: Post-merge cascade — update all tracking artifacts after a PR merge
---

After a PR is merged, update all tracking artifacts in one pass. Behavior adapts based on whether the PR targeted staging or main.

## Arguments

`$ARGUMENTS` should include:
- A PR number (e.g., `123`) or PR URL
- Optionally `--dry-run` to preview changes without writing

## Steps

### 1. Read the merged PR

```
gh pr view <PR#> --json title,body,mergedAt,labels,closingIssuesReferences,headRefName,baseRefName,mergeCommit
```

Extract:
- What was shipped (title + body summary)
- Linked/closing issues (from both `closingIssuesReferences` and PR body text — look for `Fixes #N`, `Closes #N`, `Relates to #N`, `Part of #N`)
- Branch that was merged
- **Base branch** (staging or main) — this determines all downstream behavior

If the PR is not merged, STOP and inform the user.

### 2. Update CHANGELOG.md (if it exists)

- Add an entry under the appropriate section (Added/Changed/Fixed)
- Use the PR title and number as the entry
- Follow the existing changelog format in the file

### 3. Update roadmap (if referenced)

**Skip if base branch is `staging`** — roadmap items are only checked off on release to main.

If base branch is `main`:
- Search `roadmap.md` (or equivalent) for items matching the PR title, linked issues, or branch name
- Check off completed items (`- [ ]` → `- [x]`)
- Only modify items that clearly match — do not guess

### 4. Issue lifecycle (branch-dependent)

**If merged to `staging`:**
- Do NOT close any linked issues — they stay open until released to main
- The `project-sync.yml` workflow automatically sets their Project status to "On Staging"
- Note in the summary which issues were found but left open

**If merged to `main`:**
- For each linked issue, verify it was auto-closed by GitHub:
  `gh issue view <#> --json state` — check state is "CLOSED"
- If any issue was NOT auto-closed (e.g., PR used `Relates to` instead of `Fixes`):
  close it with `gh issue close <#>`
- The `project-sync.yml` workflow automatically sets their Project status to "Done"

### 5. Resolve Engram commitments

- Get open commitments from the shared context-gather: dispatch the
  `context-gather` agent for the `engram` slice and use its `### 3ngram`
  block's commitments list. This is the same shared context-gather that
  `staging-audit`, `milestone-audit`, and `doc-audit` consume, so the
  `engram://commitments` read happens once rather than being repeated per
  audit skill. (If you are already running inside an audit that dispatched
  `context-gather`, reuse that output instead of dispatching again.)
- Match commitments to the shipped work (by topic, issue number, or keyword)
- Resolve matched commitments using `resolve()` tool
- If Engram MCP is not connected, skip this step and note it

### 6. Summary

Output what was updated:
```
## Post-merge: PR #<N>
- Base branch: staging | main
- Changelog: [updated/skipped]
- Roadmap: [N items checked off / skipped (staging merge)]
- Issues: [closed: #X, #Y | left open for main merge: #X, #Y]
- Commitments resolved: [list or none]
```

If `--dry-run`, show what would be changed without writing.
