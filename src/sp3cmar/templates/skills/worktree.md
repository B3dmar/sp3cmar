---
description: Git worktree lifecycle — create, list, or tear down parallel workspaces
---

Manage git worktrees for parallel development. Each worktree gets its own branch and working directory.

## Arguments

`$ARGUMENTS` should be one of:
- `start <branch-name> [base]` — create worktree from base branch (default: staging)
- `done <branch-name>` — remove worktree, prune, clean up
- `list` — show all active worktrees
- `stale` — find worktrees with no recent commits
- `plan [N]` — generate batched worktree prompts from roadmap/issues/commitments (default N=6)

## Behavior

### `start <branch-name> [base]`

1. Determine repo name: `basename $(git rev-parse --show-toplevel)`
2. Fetch latest from remote: `git fetch origin <base>`
3. Create worktree:
   ```
   git worktree add ../worktrees/<repo>-<branch-name> -b <branch-name> origin/<base>
   ```
4. Install dependencies in the new worktree:
   - If `backend/pyproject.toml` exists: `cd backend && uv sync`
   - If `frontend/package.json` exists: `cd frontend && npm ci`
   - If root `pyproject.toml` exists: `uv sync`
   - If root `package.json` exists: `npm ci`
5. Report:
   ```
   Worktree ready: ../worktrees/<repo>-<branch-name>
   Branch: <branch-name> (from <base>)

   To start working:
     cd ../worktrees/<repo>-<branch-name>
     claude
   ```

### `done <branch-name>`

1. Determine repo name from current repo
2. Remove worktree:
   ```
   git worktree remove ../worktrees/<repo>-<branch-name>
   ```
   If it has uncommitted changes, warn the user and ask for confirmation before `--force`
3. Prune stale references: `git worktree prune`
4. Clean empty parent directories:
   ```
   find ../worktrees -maxdepth 2 -type d -empty -delete
   ```
5. Check if branch was merged:
   - If merged to staging/main: offer to delete remote branch with `git push origin --delete <branch>`
   - If not merged: warn and do NOT delete

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
