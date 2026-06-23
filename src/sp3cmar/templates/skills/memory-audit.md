---
description: Audit 3ngram capture coverage — diff what sessions said vs what was persisted
---

# Memory Coverage Audit

Treats `~/.claude/projects/<slug>/` session transcripts as a ground-truth corpus. Extracts candidate memories from each transcript, diffs against what 3ngram actually persisted, and proposes capture-filter.json rule changes to close gaps.

This skill exists because the `PostToolUse` capture hook has a narrow filter (today: alembic migrations, CLAUDE.md writes, `.claude/plans/` writes, git commits). A lot of signal — feedback rules, project facts, decisions — never gets captured. This audit quantifies that gap and turns it into concrete filter updates.

## Arguments

`$ARGUMENTS` controls scope:
- *(empty)* — audit the 10 most recent sessions across all active projects
- `<project-slug>` — restrict to sessions from a specific Claude project dir (e.g. `engram`, `b3dmar-hq`)
- `--session <uuid>` — audit a single session by ID
- `--recent <N>` — audit N most recent sessions (default 10)
- `--since <YYYY-MM-DD>` — audit sessions started on or after date
- `--archetype <type>` — filter by session archetype (feature, content, incident, triage, release)
- `--dry-run` — analysis only, do not write report or propose filter updates

## Steps

### 1. Resolve target sessions

Map arguments to a list of `.jsonl` files under `~/.claude/projects/`. Strategy:

```bash
# Active projects (prefix indicates current or recently-active work)
ls -d ~/.claude/projects/-home-sebastianebg-projects-*/ 2>/dev/null

# Session files, sorted by mtime
find ~/.claude/projects/<slug>/ -maxdepth 1 -name "*.jsonl" -printf "%T@ %p\n" \
  | sort -rn | head -N | awk '{print $2}'
```

For each selected file record: session UUID, project path, start timestamp (first `.timestamp` in file), end timestamp (last), duration.

If zero sessions match, stop with `"ERROR: No sessions matched scope"`.

### 2. Extract candidate memories per session

For each session, scan user turns and significant assistant outputs. **Do not read `tool_result` bodies** — they are huge and rarely contain memorable signal. Focus on:

- User turns (all)
- Assistant text content (excluding tool-use details)
- Tool-use *invocations* (names + key parameters) — skip `content` of results

Classify each candidate by the global 3ngram memory taxonomy (see `/home/sebastianebg/.claude/CLAUDE.md`):

| Type | Signals that trigger a candidate |
|------|----------------------------------|
| `user` | User states role, preferences, knowledge, context about themselves |
| `feedback` | "don't", "stop", "never", "from now on", correction of tone/approach, or explicit confirmation ("yes exactly", "perfect, keep doing that") |
| `project` | Decisions made, deadlines, ownership, sequencing, scope changes — anything time-bound |
| `reference` | External system pointers — URLs, dashboard links, ticket numbers, doc locations |
| `commitment` | "I'll do X by Y", "next step is Z", plan headers, `/plan` invocations |
| `decision` | "we're going with X because Y", architectural choices, rejected alternatives |

Emit a **candidates table**: `{session_id, turn_index, type, summary, reason, timestamp}`.

Be conservative: if a candidate does not clearly match one type, skip it. False positives pollute the diff.

### 3. Query 3ngram for actual captures

For each session's time window, fetch what 3ngram persisted:

```python
mcp__3ngram-prod-oss__search(
  query="",                       # empty → time-window filter only
  created_after=session.start,
  created_before=session.end,
  limit=200,
)
```

Match memories back to their source session where possible — the capture hook stamps `source_session_id` in metadata if configured. If not, match by proximity of `created_at` to session turns.

### 4. Diff candidates vs actual

Produce per-session and aggregate diffs:

| Column | Meaning |
|--------|---------|
| **Captured** | Candidate exists in 3ngram (matched by semantic similarity > 0.7 or near-identical summary) |
| **Missed** | Candidate has no 3ngram match — capture gap |
| **Spurious** | 3ngram memory has no candidate — likely over-capture |
| **Partial** | Captured but wrong type / wrong scope |

For matching use `mcp__3ngram-prod-oss__search` with the candidate summary as the query, scoped to the session window — semantic match, not string match.

### 5. Aggregate + analyze

Roll up across all audited sessions:

- **Recall per type**: `captured / (captured + missed)` by memory type
- **Precision per type**: `captured / (captured + spurious)`
- **Top missed patterns**: cluster the `Missed` rows by surface form (e.g. "user feedback about X", "project decision about Y") and count
- **Capture-hook blind spots**: which tool/event combinations produced candidates but no captures? (e.g. "`Edit` on `content/**` → 14 candidates, 0 captures")

### 6. Propose capture-filter updates

For the top 3-5 missed patterns, propose concrete rule additions to `~/projects/engram/scripts/hooks/capture-filter.json`. Each proposed rule must include:

- **Matcher**: tool name + path/content regex
- **Memory type**: target classification
- **Rationale**: number of missed candidates this rule would have caught
- **Risk**: potential false-positive rate (estimated from the audit data)

Do not modify `capture-filter.json` directly — only propose. The user applies.

### 7. Write report

Unless `--dry-run`, write:

```
sp3cmar/reviews/memory-audit/v<YYYY-MM-DD>/REPORT.md
```

Report structure:

```markdown
# Memory Coverage Audit — <date>

## Scope
- Sessions audited: N (list with project × duration × archetype)
- Time range: <start> → <end>

## Coverage Summary
| Memory Type | Candidates | Captured | Missed | Recall |
|-------------|-----------|----------|--------|--------|
| user | ... | ... | ... | ...% |
| feedback | ... | ... | ... | ...% |
| project | ... | ... | ... | ...% |
| reference | ... | ... | ... | ...% |
| commitment | ... | ... | ... | ...% |
| decision | ... | ... | ... | ...% |

## Top Missed Patterns
1. [Pattern]: N occurrences across M sessions. Example turn: ...
2. ...

## Capture Blind Spots
- [Tool]:[Path] → N candidates, 0 captures
- ...

## Proposed Filter Rules
1. ...

## Spurious Captures
- [Memory type] captured N times without candidate basis: ...

## Sessions Audited
<table>
```

### 8. Persist audit findings

Capture the audit itself to 3ngram so future sessions know when this was last run and what was proposed:

```python
mcp__3ngram-prod-oss__remember(
  content="Memory coverage audit <date>: overall recall X%, top miss = <pattern>. Proposed N filter rules, see sp3cmar/reviews/memory-audit/v<date>/REPORT.md",
  memory_type="project",
  scope="work",
  tags=["meta:memory-audit", "capture-filter"],
)
```

## Rules

1. **Read-only on 3ngram** — never call `remember` / `archive_memories` / `reclassify_memory` during audit steps 1-7. Only step 8 writes, and only one summary memory.
2. **Do not modify `capture-filter.json`** — propose only. Rule application is a separate manual step so the user can sanity-check false-positive risk.
3. **Skip `tool_result` bodies** when parsing transcripts. They balloon token count without adding analytic signal.
4. **Be conservative on candidates**. A candidate that doesn't clearly fit a type should be dropped, not fuzzed. Over-candidates make the "Missed" column meaningless.
5. **Session matching is best-effort**. If the capture hook doesn't stamp `source_session_id`, match by timestamp proximity — and acknowledge uncertainty in the report.
6. **Don't audit the current session**. Transcript isn't finalized yet.

## When to invoke

- Monthly, as a standing review — quantifies whether the capture hook is keeping up as workflows evolve
- After significant changes to `capture-filter.json` — validate the new rules hit their target patterns
- When onboarding a new workflow archetype — check whether memories about it are being captured correctly
- After a missed handoff ("why didn't 3ngram remember that decision?") — run scoped to the session where the decision was made
