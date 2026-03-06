# Building Recall-Based Skills

How to build Claude Code skills that use 3ngram's `recall` and `search` tools.

## Pattern: Context-Aware Skill

```markdown
# My Custom Skill

## Step 1: Load Context
Call `mcp__3ngram__recall` with a query matching your task domain.
This returns relevant memories ranked by semantic similarity.

## Step 2: Use Context
Reference the recalled memories in your analysis/output.

## Step 3: Remember Results
Call `mcp__3ngram__remember` to persist any new decisions or patterns.
```

## Key Tools

### `mcp__3ngram__recall`
Semantic search across all memories. Use natural language queries.

```
Query: "authentication patterns for this project"
Returns: Ranked list of relevant memories with scores
```

### `mcp__3ngram__search`
Structured search with filters (scope, classification, date range).

```
Query: "API design"
Scope: "my-project"
Classification: "decision"
```

### `mcp__3ngram__suggested_context`
AI-suggested relevant memories based on current conversation context.
No query needed — it infers relevance automatically.

## Tips

- Use `recall` for broad semantic search, `search` for filtered lookups
- Always include graceful degradation for when 3ngram is unavailable
- Classify memories precisely: `decision`, `pattern`, `context`, `commitment`
- Use project-specific scopes to avoid cross-project noise
