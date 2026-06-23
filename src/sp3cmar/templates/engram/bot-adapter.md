---
description: Scaffold a new chat-platform bot adapter for engram (Slack, Telegram, WhatsApp, Teams, etc.)
---

# Bot Adapter Scaffold — engram

Scaffold a new platform adapter under `engram/backend/src/engram/bots/<platform>/` using existing adapters as the template. Discord shipped first; Slack and WhatsApp were hand-scaffolded 2026-05-04. This skill encodes that flow so the next platform takes minutes, not an afternoon.

## Arguments

`$ARGUMENTS`:
- `<platform>` — required. One of `slack | telegram | whatsapp | teams | google-chat | linkedin | imessage` or any new chat platform name. Lowercase, hyphenated.
- `--reference <existing>` — optional. Existing adapter to mirror (default: `discord`, the most-mature reference).
- `--no-pr` — skip the draft PR step at the end.
- `--dry-run` — print the plan and exit before writing files.

## Prerequisites

Run from the engram repo root (`~/projects/engram`). If not in engram, STOP and tell the user to `cd` there first.

## Steps

### 1. Read reference adapters

Pick the reference adapter (default `discord`) and read its layout end-to-end before generating anything:

```
backend/src/engram/bots/<reference>/
  __init__.py
  adapter.py        # handler interface, message normalization
  models.py         # platform-specific schemas
  webhook.py        # signature verification, inbound webhook handler
  tests/
```

If a second adapter exists (e.g. `slack`), read it too — diffing two real implementations surfaces the contract more reliably than reading one.

Capture:
- The handler interface (method names, return shapes)
- How inbound messages are normalized to engram's internal `Message` model
- The auth/signature verification pattern
- How the adapter integrates with `services/bot_dispatch.py` (or equivalent)
- Where platform config keys live in `core/settings.py`

### 2. Confirm directory layout

Create the target tree (do not overwrite if anything exists — abort and ask):

```
backend/src/engram/bots/<platform>/
  __init__.py
  adapter.py
  models.py
  webhook.py
  tests/
    __init__.py
    test_webhook.py
    test_adapter.py
```

Plus FastAPI route registration in `api/routes/bots.py` (or wherever the existing adapters wire their webhook URL).

### 3. Generate boilerplate

Use the reference adapter as a literal template. Replace platform names, signature schemes, and message field mappings — keep the structure.

Required pieces:
- **Webhook signature verification** — every platform has its own scheme (Slack `X-Slack-Signature` HMAC, Telegram secret token, WhatsApp X-Hub-Signature-256). Look up the platform's spec; do not invent.
- **Inbound message → engram `Message` mapping** — text, sender id, channel id, thread/reply id, attachments, timestamp.
- **Outbound reply formatter** — engram `Reply` → platform-specific JSON payload. Honor markdown limitations and length caps per platform.
- **Error handling** — webhook returns 2xx fast, queue work async; log signature failures distinctly from parse failures.
- **Bot dispatch integration** — call into the existing `services/bot_dispatch.py` so the new platform shares context-resolution and reply logic with Discord/Slack.

### 4. Add platform config

Add platform-specific settings to `backend/src/engram/core/settings.py` following the existing pattern:

- `<PLATFORM>_BOT_TOKEN` (or equivalent — OAuth credentials, signing secret, verify token)
- `<PLATFORM>_WEBHOOK_URL` if applicable
- Any feature flags (e.g. `<PLATFORM>_ENABLED`)

Use the same pydantic-settings pattern as Discord/Slack — env-var driven, optional with sensible defaults, never hardcode credentials.

### 5. Add database migration (if needed)

If the new platform requires a row in `integrations` (or a new bot-specific table), generate an alembic migration:

```bash
cd backend && uv run alembic revision -m "add <platform> bot integration"
```

Edit the generated file under `backend/alembic/versions/<slot>_add_<platform>_bot_integration.py`. Use the next free slot — check `engram/CLAUDE.md` for the current slot ceiling (currently around 147).

If no schema change is needed (most cases — the existing `integrations` table is platform-agnostic), skip this step.

### 6. Smoke test

Add `backend/tests/bots/<platform>/test_webhook.py`:
- Signature verification: valid, invalid, missing
- Inbound message normalization: at least one happy-path payload from real platform docs
- Echo dispatch: webhook → dispatch → reply formatter

Run:

```bash
cd backend && uv run pytest tests/bots/<platform>/ -v
```

### 7. Frontend integration admin (if needed)

If the integrations admin page lists bots, add the new platform:
- `frontend/src/app/(app)/integrations/page.tsx` (or wherever the list lives)
- Connect/disconnect flow if OAuth-based

Skip this step for purely webhook-token platforms (Telegram, WhatsApp Business API) until the user explicitly asks for an admin UI.

### 8. Lint and type-check

```bash
cd backend && uv run ruff check src/engram/bots/<platform>/ tests/bots/<platform>/
cd backend && uv run ruff format src/engram/bots/<platform>/ tests/bots/<platform>/
cd backend && uv run mypy src/engram/bots/<platform>/
```

### 9. Open draft PR (skip if `--no-pr`)

Branch convention: `feat/bot-<platform>`. Use `/sp3cmar-ship` if installed, otherwise:

```bash
git checkout -b feat/bot-<platform>
git add backend/src/engram/bots/<platform>/ backend/tests/bots/<platform>/ backend/src/engram/core/settings.py
git commit -m "feat(bots): scaffold <platform> adapter"
git push -u origin feat/bot-<platform>
gh pr create --draft --base staging --title "feat(bots): <platform> adapter scaffold" --body "..."
```

### 10. Persist a 3ngram commitment

If 3ngram MCP is connected, save a commitment so follow-up wiring (real credentials, smoke against the live platform, admin UI) doesn't get forgotten:

```
mcp__3ngram-prod-oss__remember(
  text="Scaffolded <platform> bot adapter (PR #<N>). Next: wire real credentials, end-to-end smoke, optional admin UI.",
  classification="commitment",
  scope="work"
)
```

## Reference

- Discord adapter: `backend/src/engram/bots/discord/` — most-mature, started earliest
- Slack adapter: `backend/src/engram/bots/slack/` — hand-scaffolded 2026-05-04
- WhatsApp adapter: `backend/src/engram/bots/whatsapp/` — hand-scaffolded 2026-05-04
- Bot dispatch service: `backend/src/engram/services/bot_dispatch.py`
- Integrations table: `backend/alembic/versions/<slot>_add_integrations_table.py`
