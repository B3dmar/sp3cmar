---
description: Render a markdown plan or 3ngram memory as a single-file interactive HTML artifact
---

Render a plan, batch manifest, or 3ngram memory as a self-contained interactive HTML page so a human can engage with it as a "compute allocator" — not stare at 1000 lines of markdown until their eyes glaze over.

Concept origin: Thariq Shihipar (Anthropic), *How I AI* podcast — replacing markdown with HTML for AI-powered development. The model output is identical; the human engagement is not.

## Arguments

`$ARGUMENTS` accepts (resolved in this order):

- **`<path-to-markdown>`** — explicit `.md` file path (absolute, or relative to `cwd`)
- **`<memory-id>`** — numeric ID → pull via `mcp__3ngram__search(memory_ids=[N])` and render the memory body
- **`<topic-string>`** — non-numeric, no `.md` extension → `mcp__3ngram__search(query="<topic>", limit=5)` and render the top hit (confirm with user before rendering if the top score is below 0.6)
- **(no arg)** — render the most-recent `~/.claude/plans/*.md` by `mtime`

Optional flags (postfix):

- `--out <path>` — override default output location
- `--open` — after writing, attempt `xdg-open <path>` (Linux) / `open <path>` (macOS); silently skip if unavailable

## Output

Default destination: `~/.claude/plans/html/<source-slug>.html` (create `~/.claude/plans/html/` if missing).

`<source-slug>` derivation:
- From file: basename without `.md` extension
- From memory ID: `memory-<id>-<topic-slugified>`
- From topic: slugified topic + 8-char hash suffix

After write, print the absolute path on a single line so the user can click / paste into a browser.

## Render template

The HTML must be **a single self-contained file**. Allowed external loads:
- Google Fonts (Inter, JetBrains Mono, Source Serif 4) via `<link>` to `fonts.googleapis.com`
- Mermaid via `<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js">` *only if the source contains a flow/sequence/decision tree worth diagramming*

Nothing else loaded from the network. No CSS files, no JS modules, no images.

### Required structure (in order)

1. **`<head>`** — title = source title; favicon `data:` URI; meta description from lede
2. **Top bar** — small, sticky. Left: source path / memory ID with `file://` or `engram://` link. Right: generated-at timestamp + token cost (if you can measure it).
3. **Lede** — 1–3 sentences answering "why does this exist". If the source markdown has a `## Context` or top paragraph, use it. Otherwise infer from the first heading + first paragraph.
4. **Outcome** — what "done" looks like. One paragraph. If the source has a `## Success criteria` / `## Acceptance` / `## Validation` section, derive from there.
5. **Tasks / checklist** — interactive `<input type=checkbox>` for every `- [ ]` line in the source. Each checkbox writes its state to `localStorage` under a key derived from the source path + task index, so progress survives reloads. Strikethrough completed items.
6. **Decision matrix** — *only if the source has 2+ named alternatives* (e.g. "Option A / Option B", "Approach 1 / Approach 2"). Render as `<table>` with one column per alternative and one row per criterion (cost, reversibility, scope, etc.). Recommended option gets a coloured cell highlight.
7. **Flow diagram** — *only if the source describes a sequence of steps, a state machine, or decision branches*. Render as `<pre class="mermaid">` with a `flowchart TD` or `sequenceDiagram`. Skip silently if the source is purely declarative.
8. **Code / diff blocks** — wrap any fenced code blocks (` ``` `) from the source in `<details>` (default-collapsed). Render contents in a monospace block; preserve whitespace.
9. **References** — link out to GitHub issues (`#NNNN` → `https://github.com/B3dmar/engram/issues/NNNN`), PRs (`PR #NNNN`), 3ngram memories (`#NNNNN` with 5+ digits → annotate "memory #" prefix; do not invent URLs).
10. **Footer** — one line: "Rendered by `/sp3cmar-html-plan` on `<ISO date>`. Source: `<path>`."

### Styling

Use 3ngram-design oklch tokens. The renderer should inline these as `:root` CSS custom properties — do **not** `@import` an external stylesheet.

If `~/.claude/skills/3ngram-design/colors_and_type.css` exists, read it and inline the `:root` block plus the semantic colour classes you actually use. If the skill is unavailable, fall back to this minimal palette:

```css
:root {
  --bg: oklch(98% 0.005 250);
  --surface: oklch(100% 0 0);
  --text: oklch(20% 0.02 250);
  --muted: oklch(45% 0.02 250);
  --accent: oklch(60% 0.18 245);    /* primary action */
  --success: oklch(65% 0.15 145);
  --warn: oklch(75% 0.15 75);
  --danger: oklch(60% 0.20 25);
  --border: oklch(90% 0.01 250);
  --code-bg: oklch(96% 0.005 250);
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: oklch(15% 0.01 250);
    --surface: oklch(20% 0.015 250);
    --text: oklch(95% 0.005 250);
    --muted: oklch(70% 0.02 250);
    --border: oklch(30% 0.01 250);
    --code-bg: oklch(25% 0.01 250);
  }
}
body { font-family: 'Inter', system-ui, sans-serif; background: var(--bg); color: var(--text); max-width: 880px; margin: 2rem auto; padding: 0 1.5rem; line-height: 1.55; }
h1, h2, h3 { font-family: 'Source Serif 4', Georgia, serif; }
code, pre { font-family: 'JetBrains Mono', ui-monospace, monospace; background: var(--code-bg); }
```

### Checkbox persistence (copy-paste verbatim, adjust storage key)

```html
<script>
(function () {
  const KEY_PREFIX = 'sp3cmar-html-plan:' + document.location.pathname + ':';
  document.querySelectorAll('input[type=checkbox][data-task-id]').forEach((el) => {
    const k = KEY_PREFIX + el.dataset.taskId;
    el.checked = localStorage.getItem(k) === '1';
    if (el.checked) el.closest('li')?.classList.add('done');
    el.addEventListener('change', () => {
      localStorage.setItem(k, el.checked ? '1' : '0');
      el.closest('li')?.classList.toggle('done', el.checked);
    });
  });
})();
</script>
<style>li.done { text-decoration: line-through; color: var(--muted); }</style>
```

### What NOT to render

- Do not invent tasks, sections, or alternatives that aren't in the source
- Do not summarise — if the source is verbose, render it verbose; the user picked HTML so they could scan/collapse, not be summarised
- Do not include analytics, tracking pixels, or any phone-home script
- Do not embed `<iframe>` or external images
- Do not produce multi-file output

## Verification (before printing the output path)

Run a self-check before declaring success:

1. File exists at the target path and is > 1 KB
2. File contains exactly one `<html>` tag and the doctype
3. Every `<input type=checkbox>` has a `data-task-id` attribute (otherwise localStorage persistence won't bind)
4. Every external URL is on the allowlist (`fonts.googleapis.com`, `fonts.gstatic.com`, `cdn.jsdelivr.net/npm/mermaid@`)
5. The rendered file size is < 200 KB (large = probably accidentally embedded an asset)

If any check fails, print the failure and the output path with a "⚠ verification failed" prefix instead of the clean path.

## 3ngram capture

If this is the **first** render in a session, call `mcp__3ngram__remember` once with:
- `topic`: `Used /sp3cmar-html-plan on <source>`
- `memory_type`: `event`
- `tags`: `["sp3cmar-html-plan", "html-rendering"]`
- `content`: include source path, output path, and one-line subjective note ("checklist persistence worked", "mermaid diagram was useful", "would not use again for this source type", etc. — leave blank if the user hasn't reacted yet)

This is how we accumulate Phase 1 verdict data without asking the user to write notes.

## When to refuse

Refuse and explain instead of rendering if:
- Source path doesn't exist
- Source is > 100 KB markdown (over budget; suggest splitting)
- Source is non-markdown (PDF, image) — different tool needed
- User asks to render production source files (`backend/src/`, `frontend/src/`, etc.) — out of scope, this is for plans and notes only
