---
description: Analyze Claude Code conversations for repeating patterns and automation opportunities
---

Spawn a team of parallel agents to analyze conversation history, session transcripts, and existing automation infrastructure. Identify repeating patterns, manual toil, and concrete opportunities to improve the workflow via skills, commands, agents, hooks, or CLAUDE.md rules.

## Arguments

`$ARGUMENTS` controls scope:
- *(empty)* — full audit across all projects
- `<project-name>` — focus on a specific project (e.g., `engram`, `seb-life`)
- `--quick` — analyze history.jsonl only, skip session deep-dives

## Steps

### 1. Map the landscape

Before spawning agents, gather structural context:

- `~/.claude/history.jsonl` — count lines, check date range
- `~/.claude/projects/` — list project dirs, count sessions per project, sort by volume
- `~/.claude/commands/` — list existing commands
- `~/.claude/agents/` — list existing agents
- `~/.claude/skills/` — list existing skills
- `~/.claude/settings.json` — read hooks, permissions, plugins
- Per-project `.claude/commands/` directories for the top projects

Report the landscape summary to the user before proceeding.

### 2. Spawn analysis agents in parallel

Launch 4 agents concurrently using the Task tool:

**Agent 1 — Prompt pattern analysis**
Mine `~/.claude/history.jsonl` for:
- Top 20 most common prompt patterns (grouped by similarity, with counts)
- Common slash command usage frequency
- Session lifecycle overhead (confirmations, retries, /clear, /exit, /mcp)
- Git operation prompts (commit, push, PR, merge) with variant counts
- Temporal patterns (daily routine, weekly rhythm, peak hours)
- Per-project breakdown of activity

**Agent 2 — Conversation deep-dive**
For the top 3 projects by session count, read the 10 most recent JSONL session files from `~/.claude/projects/<project>/`:
- Multi-step workflow sequences that repeat
- Instructions given repeatedly that should be CLAUDE.md rules
- Session archetypes (feature dev, bug fix, review, daily note, deploy)
- Pain points (frustration signals, retries, corrections)
- Workflow gaps between sessions

**Agent 3 — Automation infrastructure audit**
Read all existing commands, agents, skills, hooks, and CLAUDE.md files:
- Map what's covered vs gaps
- Identify stale/orphaned artifacts
- Check for command/agent duplication
- Evaluate hook effectiveness
- Assess plugin and permission configuration
- Compare what's automated to what's done frequently

**Agent 4 — Development workflow patterns**
Analyze git worktree usage, branch patterns, and CI/CD interactions:
- Worktree creation/teardown frequency and lifecycle
- Branch naming consistency
- PR workflow patterns
- CI failure and retry rates
- Deployment patterns

### 3. Synthesize findings

After all agents return, combine their reports into a single structured output:

```
## Workflow Audit — YYYY-MM-DD

### Key Numbers
| Metric | Value |
|--------|-------|
| Total prompts analyzed | N |
| Active sessions | N |
| Overhead ratio | N% |
| Top project | name (N sessions) |

### Top 10 Automation Opportunities (ranked by impact)

#### 1. [Title] — [type: command/hook/CLAUDE.md rule/agent]
**Saves ~N prompts/month.** [Evidence from analysis.]
[What to build and how it works.]

#### 2. ...
(continue for top 10)

### Quick Wins (cleanup items)
- [ ] [item with specific file/setting to change]
- [ ] ...

### CLAUDE.md Rules to Add
- [ ] [rule with rationale]
- [ ] ...

### Recommended New Commands
| Command | Purpose | Estimated impact |
|---------|---------|-----------------|
| ... | ... | ... |
```

### 4. Prioritize recommendations

Rank by:
1. **Frequency x effort** — how often the manual step occurs vs how hard it is to automate
2. **Overhead reduction** — prompts/session saved
3. **Error reduction** — CI failures, retries, corrections avoided

Separate into:
- **Immediate** — CLAUDE.md rules, settings changes, cleanup (do now)
- **High-value** — new commands/skills (build this week)
- **Product features** — things that should be built into the application, not Claude Code (create issues)

## Rules

1. Agents must READ files, not modify them. This is an analysis-only audit.
2. Do not fabricate numbers — all counts must come from actual data.
3. Be specific in recommendations — name the command, write the CLAUDE.md rule, specify the hook.
4. Always show evidence (prompt counts, session examples) for each recommendation.
5. If Engram MCP is available, check for existing commitments related to workflow improvements.
