---
description: Drive the full dev lifecycle as an orchestrator — specify, plan, implement (fan-out worktrees), verify, review, resolve-bots, risk-routed gate, approve
---

# Pipeline

Drive a piece of work through the **entire development lifecycle** as a single
orchestrated workflow: from acceptance criteria to a gated, human-approvable PR.
This skill is a **declarative runbook** — it names the phases, the roles, the
context flow, and the gates so that an agent can execute them consistently and so
the same shape can later compile to a portable manifest.

This is a **runbook you follow as prose** — do NOT implement a standalone
orchestration daemon, scheduler, or service in code. The phase graph below is
something the orchestrating agent walks by dispatching sub-agents and running
gates, not a program to write.

It does **not** reimplement capabilities that already exist as skills. It
**composes** them at the right phase (see the phase table). Phases call out to
`/sp3cmar-acceptance`, `/sp3cmar-context`, `/sp3cmar-worktree`,
`/sp3cmar-bot-review`, `/sp3cmar-ship`, and `/sp3cmar-review`.

## Arguments

`$ARGUMENTS` controls behavior:
- *(empty)* — run the full pipeline for the current topic / issue on the current branch
- `<issue-number>` — drive the named GitHub issue end to end
- `--from <phase>` — resume the pipeline at a named phase (e.g. `--from review`).
  **Resume contract:** assume every phase before `<phase>` already passed its exit
  gate; the orchestrator re-runs phase 0 (re-pulls context) before resuming so the
  `## Inherited Context` block is fresh, then continues from `<phase>` onward.
- `--dry-run` — print the routing decision and phase plan without dispatching work

## Roles

There are exactly two roles in this pipeline.

### Orchestrator (you, when you run this skill)

**HARD RULE: the orchestrator NEVER edits code or files itself.** The
orchestrator only:
1. **Pulls context** once (phase 0).
2. **Fans out** to sub-agents (or dispatches a single sub-agent — never edits
   itself — when the complexity router says no fan-out).
3. **Runs gates** (acceptance, verify, the risk-routed gate).
4. **Synthesizes** sub-agent findings into a single decision and report.

If the orchestrator finds itself about to call `Edit`, `Write`, or otherwise
mutate the working tree, that is a bug in how the phase was routed — re-route the
work into a sub-agent instead.

### Sub-agent (spawned by the orchestrator)

A sub-agent does exactly one phase-task: implements one task, runs one reviewer
dimension, etc. Sub-agents are governed by the **Context Contract** below.

## Context Contract

Context flows **one way, pulled once**:

1. **Orchestrator pulls context once** at phase 0: a `mcp__3ngram-prod-oss__search` over
   the topic, the relevant GitHub state (issue, linked PRs, CI), and the relevant
   code (files, prior patterns). This is the `/sp3cmar-context` phase-0 pull.
2. **Orchestrator passes an `## Inherited Context` block** into every sub-agent
   prompt. That block carries the distilled findings the sub-agent needs:
   acceptance criteria, relevant files, prior decisions, the branch slug.
3. **Sub-agents do NOT call briefing/search themselves.** They do not invoke
   `mcp__3ngram-prod-oss__briefing` or `mcp__3ngram-prod-oss__search` for direction. They may read
   the repo. This avoids N sub-agents each re-pulling the same context (cost and
   drift).
4. **Sub-agents PUSH findings back to 3ngram** when done, via
   `mcp__3ngram-prod-oss__remember`, tagged `["subagent", "branch:<slug>"]` so the
   orchestrator (and future sessions) can recover what each sub-agent learned.

The orchestrator prompt template for a sub-agent looks like:

```markdown
You are a sub-agent. Do EXACTLY this one task. CONTEXT CONTRACT: your context is
in this prompt — do NOT call briefing/search for direction (you MAY read the
repo). PUSH a finding back to 3ngram when done, tagged ["subagent","branch:<slug>"].

## Inherited Context
<acceptance criteria, relevant files, prior decisions, branch slug, gate policy>

## Task
<the single task>
```

**Sub-agent hook environment:** when launching a sub-agent, export
`ENGRAM_HOOK_ROLE=subagent` in its environment. The engram-hook briefing
binary early-returns (skips the 3ngram auto-pull) when
`ENGRAM_HOOK_ROLE=subagent` OR the cwd is a secondary worktree.
Task-dispatched sub-agents inherit the orchestrator's main-worktree cwd, so
the path check alone misses them — the env var is the belt-and-suspenders
that stops a sub-agent from re-pulling the briefing the orchestrator already
holds (the Context Contract above). Set it whether you dispatch via the
`Task` tool or spawn a separate `claude` process, e.g.
`ENGRAM_HOOK_ROLE=subagent claude ...`.

**Recommended harness-level mechanism (covers in-process Task dispatch):** the
`ENGRAM_HOOK_ROLE=subagent claude ...` shell prefix only reliably reaches
sub-agents you launch through a **shell**. An **in-process** `Task`-tool
sub-agent has no shell, so the export may not reach the engram-hook subprocess
at all. The durable fix is to set the env var **at the harness level** so hook
subprocesses inherit it regardless of launch path: add
`ENGRAM_HOOK_ROLE=subagent` to the global `~/.claude/settings.json` `env` block
(or the hook config the harness uses to spawn hooks). That way the briefing hook
early-returns for any sub-agent, shell-launched or in-process.

> **UNVERIFIED:** whether an in-process `Task`-tool sub-agent actually inherits
> `ENGRAM_HOOK_ROLE` (via either the shell prefix or the `settings.json` `env`
> block) has **not** been verified end-to-end against the engram-hook
> subprocess. This is tracked by **#29**. Until it is confirmed (instrument the
> hook with `ENGRAM_HOOK_DEBUG=1` and dispatch a real `Task` sub-agent), treat
> in-process propagation as best-effort, not guaranteed.

## Complexity Router

Fan-out is expensive (multi-agent runs cost roughly 15x the tokens of an inline
run). **Do NOT fan out trivial work.** Before the implement phase, make the
routing decision explicit and state it in the report:

| Change shape | Route |
|--------------|-------|
| Trivial / single-file / mechanical (typo, one-line fix, config bump) | **NO FAN-OUT** — delegate to a **single** sub-agent (even genuinely trivial edits go through a sub-agent; the orchestrator never edits directly) |
| Multiple genuinely parallel, isolatable tasks | **FAN-OUT** — one sub-agent per task, each in its own git worktree |
| Sequential / tightly-coupled tasks that share files | **INLINE / serialized** — do not fan out; conflicting worktrees are not parallelizable |

State the decision verbatim, e.g.: *"Complexity router: 3 independent tasks
touching disjoint files → FAN-OUT (3 worktrees)."* or *"Complexity router:
single-file change → single sub-agent, no fan-out."*

## Execution mechanism

The Complexity Router decides **WHEN** to fan out. This section is the **HOW**:
once the router has chosen a FAN-OUT route (or a single-sub-agent route), drive
the parallel implement (phase 3) and review (phase 5) sub-agent dispatch through
the **Workflow tool**, not hand-managed parallel `Agent` / `Task` calls.

Prefer the Workflow tool for the fan-out because it gives you:

- **Deterministic fan-out** — each task maps to one tracked sub-agent run;
  no silently-dropped or double-dispatched tasks.
- **Journaling + resume** — the run is recorded, so `--from <phase>` resumes
  cleanly and a crashed orchestrator can pick the run back up.
- **Per-agent isolation** — each sub-agent gets its own context and working
  tree (the implement-phase worktree), so they cannot clobber one another.
- **Cancellation isolation** — cancelling or failing one sub-agent does not
  cancel the siblings; the orchestrator still collects the survivors' findings.

This does **not** change the routing decision: the router still says *whether*
to fan out (and how many ways), the HARD RULE still holds (the orchestrator
never edits files — every edit goes through a sub-agent), and the Context
Contract is unchanged (one `## Inherited Context` block per sub-agent; sub-agents
do not re-pull briefing/search). The Workflow tool is purely the dispatch
mechanism for the FAN-OUT route.

**Operational lesson — Bash from the orchestrator (and inside sub-agents):**

- Do **NOT** batch cwd-dependent Bash calls into a single parallel batch. Each
  Bash call is a fresh shell with no shared cwd, and one failed call cancels the
  whole batch. Run cwd-dependent commands **sequentially** — one call each, or
  one compound `cd X && a && b`.
- Prefer `NO_COLOR=1` plus exit-code / `grep -c` / dumped-then-Read assertions
  over eyeballing a colorized diff. The stdout capture layer can mangle ANSI
  codes and surface plausible-but-wrong text; trust exit codes and `git show`,
  not a colorized rendering.

## Phase Graph (declarative)

Execute the phases in this order. Each phase names the skill it composes (if any),
its inputs, and its exit gate.

| # | Phase | Composes | What happens | Exit gate |
|---|-------|----------|--------------|-----------|
| 0 | **context** | `/sp3cmar-context` | Orchestrator pulls 3ngram + GitHub + code once; builds the `## Inherited Context` block | Context block exists |
| 1 | **specify** | `/sp3cmar-acceptance` | Define / verify EARS-style acceptance criteria and issue linkage | Every AC is explicit and testable |
| 2 | **plan** | — | Break work into **atomic, independently-testable tasks**; run the **complexity router** | Routing decision stated; task list frozen |
| 3 | **implement** | `/sp3cmar-worktree` | **Fan out** one sub-agent per task, each in its **own git worktree** (or a single sub-agent when the router says no fan-out) | All tasks produce committed branches |
| 4 | **verify** | `/sp3cmar-acceptance` | Run **tests** for each task; **optional advisory** frontend-acceptance step (Slice 2; non-blocking) | Tests green (BLOCK on red) |
| 5 | **review** | `/sp3cmar-review` | Dispatch **delegated leaf reviewers** (the refactored `review-pr` agent) and synthesize | Findings synthesized |
| 6 | **resolve-bots** | `/sp3cmar-bot-review` | Triage automated PR-review bot comments; re-poll until ~10-minute quiescence | No unresolved security/bug bot comments |
| 7 | **gate** | — | Apply the **risk-routed gate policy** (below) over all findings | BLOCK / ADVISE / route-to-human resolved |
| 8 | **approve** | `/sp3cmar-ship` | Ensure changelog + PR; route to **human async approval** (sync-block only for the high-risk cases below) | Human approves |

### Phase 3 detail — implement (fan-out)

For each task in the FAN-OUT plan:
- Create an isolated worktree via `/sp3cmar-worktree` (one worktree per task,
  branch slug derived from the task).
- Spawn one sub-agent with the Context Contract prompt above; its `## Inherited
  Context` block carries the AC, the relevant files, and the branch slug.
- The sub-agent implements, runs its task's tests, commits, pushes, and PUSHES a
  3ngram finding tagged `["subagent","branch:<slug>"]`.
- The orchestrator does not edit any files — it only collects branch names and
  findings.

When the router said INLINE, skip the fan-out: dispatch a single sub-agent for
the change rather than N parallel ones.

### Phase 4 detail — verify

- Run the task's test suite (and the repo's CI-equivalent checks). **Red tests
  BLOCK.**
- **Optional advisory:** run a frontend-acceptance pass when the change touches
  the frontend. Its verdict is **advisory (non-blocking)** at the gate. The
  frontend-acceptance agent itself is delivered in Slice 2; treat this step as a
  hook the gate already knows how to weight.

## Risk-Routed Gate (phase 7)

Synthesize every signal — CI/tests, reviewer findings, bot-review verdict,
changelog presence, frontend-acceptance verdict — and route each into one of
three lanes.

### BLOCK (must resolve before merge)

- Failing CI or failing tests.
- Security or correctness findings (from reviewers or bots).
- **Unresolved** security/bug bot comments (per `/sp3cmar-bot-review`'s
  merge-gate verdict).
- A **missing changelog** entry on a **release PR**.

### ADVISE (non-blocking — surface, do not block)

- Style / nit / formatting findings.
- Performance findings without a correctness impact.
- Tech-debt findings.
- The **frontend-acceptance verdict** (advisory regardless of outcome).

### Route to HUMAN (async approval)

The default approval path is **human, async**. The orchestrator hands a synthesized
report to a human and continues without holding a synchronous block — **except**
for the following, which require a **synchronous, blocking** human decision:

- Database **migrations**.
- **Irreversible operations** (data deletion, destructive backfills, secret
  rotation, anything not cleanly revertible).
- **`staging` → `main` releases**.

For everything else, async human approval is sufficient.

## Composition (do NOT reimplement)

This skill is glue. It must compose the following existing capabilities at their
phases rather than reimplementing them:

| Capability | Skill | Phase |
|------------|-------|-------|
| Acceptance-criteria gate | `/sp3cmar-acceptance` | specify, verify |
| Phase-0 context pull | `/sp3cmar-context` | context |
| Isolated implement worktrees | `/sp3cmar-worktree` | implement |
| Bot-comment triage + merge gate | `/sp3cmar-bot-review` | resolve-bots |
| Changelog + PR creation | `/sp3cmar-ship` | approve |
| Delegated code review | `/sp3cmar-review` | review |

**Out of scope (deferred):** Do NOT build a portable manifest from this runbook
here — that is **Slice 3** and is deferred. Keep the runbook declarative
(phases / stages / roles / gates) so it *can* compile to a manifest later, but do
not author the manifest in this skill.

## Output

Emit a single pipeline report directly in the conversation:

```markdown
# Pipeline: <topic / issue>

## Routing decision
Complexity router: <FAN-OUT (N worktrees) | INLINE>

## Phase status
| Phase | Status | Notes |
|-------|--------|-------|
| context | done | pulled 3ngram + GH + code |
| specify | done | N acceptance criteria |
| plan | done | M tasks |
| implement | done | M branches |
| verify | done | tests green; frontend-acceptance: <advisory verdict> |
| review | done | <synthesized findings> |
| resolve-bots | done | <merge-gate verdict> |
| gate | <CLEAR / BLOCKED / NEEDS-HUMAN> | <lane breakdown> |
| approve | <pending human / approved> | sync-block: <yes/no + reason> |

## Gate verdict
<BLOCK reasons / ADVICE / human-approval route>
```

The orchestrator writes no source files itself; the only working-tree changes are
those produced by sub-agents during the implement phase.
