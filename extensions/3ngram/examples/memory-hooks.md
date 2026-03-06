# Memory Hook Patterns

How to use Claude Code hooks to auto-capture memories with 3ngram.

## Overview

Claude Code hooks let you run scripts in response to events. Combined with
3ngram MCP, you can automatically capture git commits, tool usage, and session
lifecycle events as persistent memories.

## Hook Types

### SessionStart — Load Context

```json
{
  "hooks": {
    "SessionStart": [{
      "command": "your-briefing-script.sh",
      "timeout": 10000
    }]
  }
}
```

Script calls 3ngram API to load relevant memories into the session.

### PostToolUse — Capture Events

```json
{
  "hooks": {
    "PostToolUse": [{
      "command": "your-capture-script.sh",
      "timeout": 5000,
      "events": ["Bash"]
    }]
  }
}
```

Filter on specific tool events (e.g., only capture after Bash calls).
Parse stdin for tool result, extract meaningful content, post to 3ngram API.

### SessionEnd — Debrief

```json
{
  "hooks": {
    "SessionEnd": [{
      "command": "your-debrief-script.sh",
      "timeout": 10000
    }]
  }
}
```

Script summarizes the session and posts a debrief memory.

## Hook Script Pattern

```bash
#!/bin/bash
# Read tool event from stdin
EVENT=$(cat)

# Extract relevant fields
TOOL=$(echo "$EVENT" | jq -r '.tool_name // empty')
RESULT=$(echo "$EVENT" | jq -r '.result // empty')

# Post to 3ngram API
curl -s -X POST "$ENGRAM_API_URL/memories" \
  -H "Content-Type: application/json" \
  -d "{\"content\": \"$RESULT\", \"scope\": \"$PROJECT\"}"
```

## Best Practices

- Keep hook scripts fast (< 5s) to avoid blocking the session
- Use `timeout` to prevent hangs
- Filter events to reduce noise — not every tool call is worth remembering
- Use `jq` for JSON parsing in shell scripts
- Set `ENGRAM_HOOK_DEBUG=1` to debug hook payloads
