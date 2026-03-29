---
description: Git worktree lifecycle — create, list, validate, or tear down parallel workspaces
---

Manage git worktrees for parallel development. Worktrees live inside the repo at `.worktrees/`.

## Arguments

`$ARGUMENTS` should be one of:
- `start <branch-name> [base]` — create worktree from base branch (default: staging)
- `done <branch-name>` — remove worktree, prune, clean up
- `list` — show all active worktrees
- `stale` — find worktrees with no recent commits
- `plan [N]` — generate batched worktree prompts from roadmap/issues/commitments (default N=6)
- `validate` — check batch status: PR states, CI, remaining work

## Behavior

### `start <branch-name> [base]`

1. Fetch latest from remote: `git fetch origin <base>`
2. Create worktree:
   ```
   mkdir -p .worktrees/$(dirname <branch-name>)
   git worktree add .worktrees/<branch-name> -b <branch-name> origin/<base>
   ```
3. Install dependencies in the new worktree:
   - If `backend/pyproject.toml` exists: `cd backend && uv sync`
   - If `frontend/package.json` exists: `cd frontend && npm ci`
   - If root `pyproject.toml` exists: `uv sync`
   - If root `package.json` exists: `npm ci`
4. If an active batch manifest exists (`sp3cmar/worktree-batch-*.md`), update the matching row status to `in-progress`
5. Report:
   ```
   Worktree ready: .worktrees/<branch-name>
   Branch: <branch-name> (from <base>)

   To start working:
     cd .worktrees/<branch-name>
     claude
   ```

### `done <branch-name>`

1. Remove worktree:
   ```
   git worktree remove .worktrees/<branch-name>
   ```
   If `.worktrees/<branch-name>` does not exist, try the old location `../worktrees/<repo>-<branch-name>` as a fallback.
   If it has uncommitted changes, warn the user and ask for confirmation before `--force`
2. Prune stale references: `git worktree prune`
3. Clean empty parent directories:
   ```
   find .worktrees -maxdepth 2 -type d -empty -delete
   ```
4. Check if branch was merged:
   - If merged to staging/main: offer to delete remote branch with `git push origin --delete <branch>`
   - If not merged: warn and do NOT delete
5. If a batch manifest exists, update the matching row status to `merged` or `closed`

### `list`

Run `git worktree list` and enhance the output:
- Show branch name, path, and last commit date
- Flag worktrees with uncommitted changes
- Flag worktrees whose branches have been merged

### `stale`

List worktrees where the branch has no commits in 3+ days:
- For each worktree, check `git log -1 --format=%cr <branch>`
- Report stale worktrees with suggestions (merge or remove)

### `plan [N]`

Generate N batched worktree prompts (default: 6) by cross-referencing available work:

1. **Gather sources** (in parallel):
   - Project roadmap: scan for open `- [ ]` items in the project's `roadmap.md`
   - GitHub issues: `gh issue list --state open --limit 20 --json number,title,labels,milestone`
   - 3ngram commitments: query `commitments()` and `blockers()` tools
   - Existing worktrees: `git worktree list` to avoid duplicating in-flight work

2. **Group into batches**:
   - Cluster related items (e.g., all CI fixes in one worktree, all docs updates in another)
   - Prioritize: blockers > overdue commitments > milestone items > backlog
   - Skip items already covered by active worktrees

3. **Output** for each worktree:
   ```
   ## Worktree N: <name>
   Branch: <type>/<slug>
   Items: #<issue>, roadmap item, commitment ref

   ### Prompt
   <detailed prompt with refs to roadmap items, GH issue numbers, and commitments>
   ```

4. Present the full plan and ask for confirmation before creating any worktrees

5. **Write batch manifest** to `sp3cmar/worktree-batch-YYYY-MM-DD.md`:
   ```markdown
   # Worktree Batch — YYYY-MM-DD

   | # | Branch | Items | Tests | Status | PR |
   |---|--------|-------|-------|--------|----|
   | 1 | fix/mobile-ux | #42, roadmap:UX | browser | pending | - |
   | 2 | chore/security | roadmap:Security | full suite | pending | - |

   ## Dependencies
   - List any cross-worktree dependencies (stacked PRs, API producers/consumers)
   - "None" if all worktrees are independent

   ## Validation Checklist
   - [ ] All PRs merged to staging
   - [ ] CI green on staging after all merges
   - [ ] Integration tests pass (if cross-worktree deps exist)
   - [ ] Roadmap updated
   ```

   Create the `sp3cmar/` directory if it does not exist.

### `validate`

Check the status of the current worktree batch:

1. Find the latest manifest: `ls -t sp3cmar/worktree-batch-*.md | head -1`
   - If no manifest found: "No active worktree batch. Run `/sp3cmar-worktree plan` first."
2. For each row in the manifest table:
   - Check PR status: `gh pr list --head <branch> --json number,state,statusCheckRollup,mergeable`
   - Check if worktree still exists: `git worktree list`
   - Update status: `pending` / `in-progress` / `pr-open` / `ci-failing` / `merged` / `closed`
   - Update PR column with PR number if found
3. Output a summary:
   ```
   ## Batch Status — YYYY-MM-DD

   | # | Branch | Status | PR | CI |
   |---|--------|--------|----|----|
   | 1 | fix/mobile-ux | merged | #42 | pass |
   | 2 | chore/security | pr-open | #43 | failing |

   ### Action Items
   - chore/security: CI failing — run `gh run view --log-failed` to diagnose
   - 2/3 PRs merged — 1 remaining

   ### Ready to close batch?
   - [ ] All PRs merged
   - [x] Integration tests (no cross-worktree deps)
   ```
4. If all PRs are merged: suggest running `/sp3cmar-post-merge` for each and closing the batch
5. Update the manifest file in-place with current statuses
