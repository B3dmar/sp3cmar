# Building Search-Based Skills

How to build Claude Code skills that use 3ngram's unified `search`, `remember`, and read-only resources.

## Pattern: Context-Aware Skill

```markdown
# My Custom Skill

## Step 1: Load Context
Call `mcp__3ngram-prod-oss__search` with a topic matching your task domain.
One call covers memories AND indexed content, ranked by semantic similarity.
For read-only status data, also read the MCP resources for current commitments,
blockers, or suggested context.

## Step 2: Use Context
Reference the recalled memories in your analysis/output.

## Step 3: Remember Results
Call `mcp__3ngram-prod-oss__remember` to persist any new decisions or patterns.
```

## Key Tools

### `mcp__3ngram-prod-oss__search`
Unified semantic search across memories AND indexed content — there is no
separate content-search tool. Use natural language topics plus optional filters
like `project`, `scope`, or `memoryType`.

```
Topic: "authentication patterns for this project"
Returns: Ranked list of relevant memories and content with scores
```

### `mcp__3ngram-prod-oss__remember`
Persist a new memory. Pass `memoryType` (a valid enum: decision, commitment,
blocker, fact, preference, pattern, note, event), `topic`, `content`, and
optional `scope`/`project`/`tags`.

### Read-only resources
Use the MCP resources (via `ReadMcpResource`) for current status data —
commitments, blockers, suggested context — when you need it without triggering
a tool call.

## Tips

- One `search` call covers both memory retrieval and indexed documents; use resources for read-only status data
- Always include graceful degradation for when 3ngram is unavailable
- Classify memories precisely with a valid `memoryType` (`decision`, `pattern`, `commitment`, …)
- Use project-specific scopes to avoid cross-project noise
