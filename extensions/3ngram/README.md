# 3ngram Extensions Cookbook

Skills and patterns that extend the [3ngram MCP](https://github.com/sebastianebg/engram) persistent memory server.

## What's Here

### Skills (`skills/`)

Ready-to-use Claude Code skills that depend on 3ngram MCP tools and resources:

| Skill | 3ngram Tools Used | Description |
|-------|-------------------|-------------|
| `morning-briefing.md` | `engram://overdue`, `engram://blockers`, `engram://commitments`, `search_memories` | Session startup with full context |
| `session-debrief.md` | `remember`, `resolve`, `engram://commitments` | Session close with memory extraction |
| `doc-audit.md` | `engram://commitments`, `search_memories` | Cross-ref docs with tracked decisions |

### Examples (`examples/`)

Cookbook patterns for building your own 3ngram-powered skills:

| Example | Description |
|---------|-------------|
| `custom-recall.md` | How to build skills that use `search_memories`, `search_content`, and resources |
| `memory-hooks.md` | Hook patterns for auto-capturing memories |

## Installation

Copy skills to your Claude Code commands directory:

```bash
cp extensions/3ngram/skills/*.md ~/.claude/commands/
```

Or install via CLI (if sp3cmar is installed):

```bash
# Skills are also available as engram extensions
ls extensions/3ngram/skills/
```

## Prerequisites

These skills require the 3ngram MCP server configured in your Claude Code settings:

```json
{
  "mcpServers": {
    "3ngram": {
      "command": "node",
      "args": ["path/to/engram/dist/index.js"],
      "env": {
        "ENGRAM_DATABASE_URL": "your-connection-string"
      }
    }
  }
}
```

## Graceful Degradation

All skills include fallback behavior when 3ngram is unavailable:
- Morning briefing falls back to git log + GitHub CLI
- Session debrief produces text output only
- Doc audit performs standard consistency checks

## Not Included

Skills already built into 3ngram MCP itself (briefing hook, debrief hook) are not
duplicated here. This cookbook covers use cases that extend beyond built-in capabilities.
