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

   When the session in this worktree is itself a **sub-agent** launched by
   an orchestrator (rather than an interactive session), export
   `ENGRAM_HOOK_ROLE=subagent` for it, e.g.
   `ENGRAM_HOOK_ROLE=subagent claude ...`. The 3ngram-hook briefing binary
   early-returns (skips the 3ngram auto-pull) when
   `ENGRAM_HOOK_ROLE=subagent` OR the cwd is a secondary worktree; setting
   the env var is the belt-and-suspenders for Task-dispatched sub-agents
   that inherit the orchestrator's main-worktree cwd and so slip past the
   path check.

   The shell-prefix form above only reliably reaches **shell-launched**
   sub-agents. For **in-process** `Task`-tool sub-agents there is no shell, so
   the recommended harness-level mechanism is to set `ENGRAM_HOOK_ROLE=subagent`
   in the global `~/.claude/settings.json` `env` block so hook subprocesses
   inherit it on any launch path. Whether in-process `Task` dispatch actually
   propagates the var to the 3ngram-hook subprocess is **UNVERIFIED** and
   tracked by **#29** (verify with `ENGRAM_HOOK_DEBUG=1` + a real `Task` run).

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
   - 3ngram commitments: read `engram://commitments` and `engram://blockers` resources
   - Existing worktrees: `git worktree list` to avoid duplicating in-flight work

2. **Group into batches**:
   - Cluster related items (e.g., all CI fixes in one worktree, all docs updates in another)
   - Prioritize: blockers > overdue commitments > milestone items > backlog
   - Skip items already covered by active worktrees

3. **Output** for each worktree (orchestrator pulls context; sub-agents never do):
   For each worktree, run ONE `mcp__3ngram-prod-oss__search(topic="<TOPIC KEYWORDS FROM THIS WORKTREE>", brief=true, limit=8)` and paste the top hits into the Inherited Context block below. The orchestrator already holds blockers/commitments from step 1 — sub-agents must not re-fetch any of it.
   ```
   ## Worktree N: <name>
   Branch: <type>/<slug>
   Items: #<issue>, roadmap item, commitment ref

   ### Prompt
   <detailed prompt with refs to roadmap items, GH issue numbers, and commitments>

   <STANDARD SUB-AGENT DIRECTIVES — injected verbatim into every generated prompt>
   ## Hook environment
   When launching this sub-agent, export `ENGRAM_HOOK_ROLE=subagent` in its
   environment (e.g. `ENGRAM_HOOK_ROLE=subagent claude ...`). The 3ngram-hook
   briefing binary skips the 3ngram auto-pull when `ENGRAM_HOOK_ROLE=subagent`
   OR the cwd is a secondary worktree; the env var is the belt-and-suspenders
   for Task-dispatched sub-agents that inherit the orchestrator's
   main-worktree cwd and so slip past the path check. The orchestrator has
   already pulled context (see the Inherited Context block below) — the
   sub-agent must not re-pull it.

   ## Inherited Context (from orchestrator — do NOT re-pull)
   Relevant prior decisions / blockers / patterns / gotchas for THIS worktree:
   - [<memory_id>] <one-line summary>        ← orchestrator pastes its per-worktree search hits here
   - ...
   If a line above indicates the work is blocked (e.g. "pipeline X broken, don't add rules until fixed"), stop and report back instead of coding around it.

   Context rules:
   - Do NOT call `mcp__3ngram-prod-oss__briefing` or `mcp__3ngram-prod-oss__search` — your context is the Inherited Context block above; the orchestrator already pulled it. Re-pulling wastes tokens and duplicates the orchestrator's work.
   - Escape hatch: only if a SPECIFIC unknown surfaces mid-task that is NOT covered above, make one targeted `mcp__3ngram-prod-oss__get_facts` / `mcp__3ngram-prod-oss__search` call, and state in your report why the inherited context was insufficient.

   Before opening the PR (PUSH findings back):
   - If you discovered a new pattern, made a non-obvious decision, or hit a gotcha, call `mcp__3ngram-prod-oss__remember` with the right classification (pattern | decision | commitment) AND `tags: ["subagent", "branch:<slug>"]`, prefixing the topic with the branch slug for attribution. One call per sub-agent minimum unless the task was purely mechanical.

   If 3ngram MCP is unavailable, skip the remember step with a one-line note and continue.
   <END DIRECTIVES>
   ```

   The Inherited Context block is mandatory in every generated prompt. Tune the `<TOPIC KEYWORDS>` per worktree (used by the orchestrator's search in this step) so it lands on the right prior memories (e.g. "auth mixin protocol runtime assert" for an auth split; "uv ruff version pin sync" for a deps hygiene task). Sub-agents read context; they never fetch it.

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
