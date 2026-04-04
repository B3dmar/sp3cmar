# Building Search-Based Skills

How to build Claude Code skills that use 3ngram's `search_memories`, `search_content`, and read-only resources.

## Pattern: Context-Aware Skill

```markdown
# My Custom Skill

## Step 1: Load Context
Call `mcp__3ngram__search_memories` with a topic matching your task domain.
This returns relevant memories ranked by semantic similarity. For read-only status data, also read resources like `engram://commitments` or `engram://blockers`.

## Step 2: Use Context
Reference the recalled memories in your analysis/output.

## Step 3: Remember Results
Call `mcp__3ngram__remember` to persist any new decisions or patterns.
```

## Key Tools

### `mcp__3ngram__search_memories`
Semantic search across all memories. Use natural language topics plus optional filters like `project`, `scope`, or `memory_type`.

```
Topic: "authentication patterns for this project"
Returns: Ranked list of relevant memories with scores
```

### `mcp__3ngram__search_content`
Semantic search across indexed docs, notes, and content chunks.

```
Query: "API design"
Scope: "my-project"
Returns: Relevant indexed content
```

### Read-only resources
Use `engram://commitments`, `engram://blockers`, and `engram://suggested-context` when you need current status data without triggering a tool call.

## Tips

- Use `search_memories` for memory retrieval, `search_content` for indexed documents, and `engram://...` resources for read-only status data
- Always include graceful degradation for when 3ngram is unavailable
- Classify memories precisely: `decision`, `pattern`, `context`, `commitment`
- Use project-specific scopes to avoid cross-project noise
