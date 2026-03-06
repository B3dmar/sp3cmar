---
description: Post-merge cascade — update all tracking artifacts after a PR merge
---

After a PR is merged, update all tracking artifacts in one pass.

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
- Linked/closing issues
- Branch that was merged
- Base branch (staging or main)

If the PR is not merged, STOP and inform the user.

### 2. Update CHANGELOG.md (if it exists)

- Add an entry under the appropriate section (Added/Changed/Fixed)
- Use the PR title and number as the entry
- Follow the existing changelog format in the file

### 3. Update roadmap (if referenced)

- Search `roadmap.md` (or equivalent) for items matching the PR title, linked issues, or branch name
- Check off completed items (`- [ ]` → `- [x]`)
- Only modify items that clearly match — do not guess

### 4. Close linked issues

- For each issue linked in the PR body or via `closingIssuesReferences`:
  - Verify it should be closed (the PR actually resolves it)
  - If not auto-closed by GitHub, close with `gh issue close <#>`

### 5. Resolve Engram commitments

- Query Engram MCP `commitments()` for open commitments
- Match commitments to the shipped work (by topic, issue number, or keyword)
- Resolve matched commitments using `resolve()` tool
- If Engram MCP is not connected, skip this step and note it

### 6. Update daily note (if in seb-life context)

- Add a line to today's daily note: `- [x] Merged PR #<N>: <title>`
- If no daily note exists for today, skip

### 7. Summary

Output what was updated:
```
## Post-merge: PR #<N>
- Changelog: [updated/skipped]
- Roadmap: [N items checked off/no matches]
- Issues closed: [list or none]
- Commitments resolved: [list or none]
- Daily note: [updated/skipped]
```

If `--dry-run`, show what would be changed without writing.
