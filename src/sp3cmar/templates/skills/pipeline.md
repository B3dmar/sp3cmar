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

1. **Orchestrator pulls context once** at phase 0: a `mcp__3ngram__search` over
   the topic, the relevant GitHub state (issue, linked PRs, CI), and the relevant
   code (files, prior patterns). This is the `/sp3cmar-context` phase-0 pull.
2. **Orchestrator passes an `## Inherited Context` block** into every sub-agent
   prompt. That block carries the distilled findings the sub-agent needs:
   acceptance criteria, relevant files, prior decisions, the branch slug.
3. **Sub-agents do NOT call briefing/search themselves.** They do not invoke
   `mcp__3ngram__briefing` or `mcp__3ngram__search` for direction. They may read
   the repo. This avoids N sub-agents each re-pulling the same context (cost and
   drift).
4. **Sub-agents PUSH findings back to 3ngram** when done, via
   `mcp__3ngram__remember`, tagged `["subagent", "branch:<slug>"]` so the
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
