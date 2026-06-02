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
- (No web fonts. Use the system sans stack inline — nothing loaded from `fonts.googleapis.com`. System fonts render instantly and legibly.)
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

**Light, neutral, and legible by default.** Clean white cards on an off-white ground, dark navy ink, generous line-height, one blue accent for links/actions. Do **NOT** use a dark theme, a `prefers-color-scheme: dark` block, heavy serif display faces, or low-contrast text — those read as dated and hurt legibility. Inline the palette as `:root` custom properties; do **not** `@import` a stylesheet. Use the **system sans stack** (no web fonts) so text renders instantly. Headings are sans, not serif.

```css
:root {
  --bg: #f4f6fb;        /* page ground */
  --card: #ffffff;      /* cards, tables, code blocks */
  --ink: #1c2333;       /* primary text (AA on --bg) */
  --ink-soft: #5d6680;  /* secondary text */
  --muted: #8089a0;     /* tertiary / labels / done items */
  --line: #e4e8f2;      /* hairline borders */
  --accent: #2563eb;    /* links + primary action (blue) */
  --ok: #0d9488;        /* shipped / yes (teal) */
  --warn: #d97706;      /* attention / partial (amber) */
  --danger: #dc2626;    /* missing / no (red) */
  --code-bg: #eef1f7;
  --shadow: 0 1px 2px rgba(20,30,60,.05), 0 10px 28px rgba(20,30,60,.07);
}
* { box-sizing: border-box; }
body {
  font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Inter, Roboto, Helvetica, Arial, sans-serif;
  color: var(--ink); line-height: 1.6; max-width: 980px; margin: 0 auto; padding: 0 24px 4rem;
  -webkit-font-smoothing: antialiased;
  background:
    radial-gradient(1100px 520px at 12% -8%, #e9efff 0%, rgba(233,239,255,0) 60%),
    radial-gradient(900px 460px at 100% 0%, #e6fbf6 0%, rgba(230,251,246,0) 55%),
    var(--bg);
}
h1 { font-size: clamp(26px,3.4vw,38px); letter-spacing: -.025em; margin: 1.6rem 0 .4rem; }
h2 { font-size: 21px; letter-spacing: -.015em; margin: 2.4rem 0 .6rem; border-bottom: 1px solid var(--line); padding-bottom: .4rem; }
h3 { font-size: 12px; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: var(--ink-soft); margin: 1.4rem 0 .5rem; }
a { color: var(--accent); text-decoration: none; } a:hover { text-decoration: underline; }
table, pre { background: var(--card); border: 1px solid var(--line); border-radius: 12px; box-shadow: var(--shadow); }
table { border-collapse: separate; border-spacing: 0; width: 100%; overflow: hidden; margin: .8rem 0; font-size: 13.5px; }
th, td { text-align: left; padding: 10px 12px; border-bottom: 1px solid var(--line); vertical-align: top; }
th { font-size: 11px; letter-spacing: .06em; text-transform: uppercase; color: var(--ink-soft); font-weight: 700; background: #fafbfe; }
code { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: .88em; background: var(--code-bg); padding: 1px 5px; border-radius: 5px; }
pre { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; padding: 14px 16px; font-size: 12.5px; line-height: 1.5; overflow-x: auto; }
.badge { font-size: 10px; font-weight: 700; letter-spacing: .04em; padding: 2px 7px; border-radius: 999px; border: 1px solid currentColor; }
```

Keep the top bar and any cards on `var(--card)` with `var(--shadow)`; reserve color for meaning (accent = action/link, ok = done/yes, warn = partial, danger = missing). Everything else stays ink-on-paper.

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
