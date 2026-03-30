---
description: Full-stack UI/UX audit — schema, components, design, landing page, coverage gaps
---

Orchestrate a multi-agent, read-only audit of a web application's frontend and backend. Discover the project structure, spawn parallel sub-agents to audit schema, components, design, landing page, and backend-to-UI coverage, then synthesize everything into a single structured report with proposed GitHub issues.

**This is a research and planning task only. DO NOT make any code changes.**

## Arguments

`$ARGUMENTS` controls scope:
- *(empty)* — full audit (all 5 agents)
- `frontend` — agents 2 + 3 only (component inventory + design audit)
- `backend` — agent 1 only (schema audit)
- `coverage` — agents 1 + 2 + 5 (schema + components + coverage matrix)
- `--skip-landing` — skip agent 4 (landing page audit)
- `--output <path>` — custom report path (default: `docs/ux-audit-YYYY-MM-DD.md`)
- `--no-issues` — skip GitHub issue generation in synthesis

## Steps

### 0. Discover project structure

Before spawning agents, map the project landscape. Run these checks and report the summary to the user before proceeding.

**Framework detection** — check for:
- `next.config.*` (Next.js)
- `nuxt.config.*` (Nuxt)
- `vite.config.*` or `svelte.config.*` (Vite/SvelteKit)
- `angular.json` (Angular)
- `remix.config.*` (Remix)
- `manage.py` + `settings.py` (Django)
- `Gemfile` with `rails` (Rails)
- `mix.exs` with `phoenix` (Phoenix)
- `go.mod` with common web frameworks (Go)

**Monorepo detection** — check for:
- `pnpm-workspace.yaml`, `turbo.json`, `nx.json`, `lerna.json`
- Root `packages/`, `apps/`, or `services/` directories
- If monorepo, identify which packages are frontend vs backend vs shared

**ORM / schema detection** — check for:
- `prisma/schema.prisma` (Prisma)
- `**/models.py` or `**/models/*.py` (Django/SQLAlchemy)
- `drizzle.config.*` or `**/schema.ts` with drizzle imports (Drizzle)
- `db/schema.rb` + `db/migrate/` (Rails ActiveRecord)
- `**/migrations/` or `alembic/` (generic migration dirs)
- `*.graphql` or `**/schema.graphql` (GraphQL schema)
- API route files with query parameter definitions

**Frontend directory mapping** — locate:
- Component root (`src/components/`, `components/`, `app/`, `pages/`)
- Route definitions (file-system routing or config-based)
- Shared layout and navigation files
- Design system / UI library usage (shadcn, MUI, Chakra, Tailwind, etc.)
- Theme configuration files

**Landing page detection** — check for:
- Separate directories: `landingpage/`, `marketing/`, `www/`, `landing/`
- Separate package in a monorepo with marketing-oriented naming
- If none found and `--skip-landing` was not passed, auto-skip agent 4 with a note

**Settings / config page detection** — check for:
- Settings routes (`/settings`, `/account`, `/preferences`, `/admin`)
- Settings-related components or pages

Report the discovery summary as a table:

```
| Aspect | Detected |
|--------|----------|
| Framework | ... |
| Monorepo | yes/no (tool: ...) |
| ORM / Schema | ... |
| Frontend root | ... |
| Component library | ... |
| Landing page | ... (path) or "not found" |
| Settings pages | ... |
```

If no recognized framework or frontend is detected, ask the user to specify the frontend and backend directories before proceeding.

### 1. Spawn agents in parallel

Launch agents concurrently using the Agent tool. Each agent receives the discovery context from Step 0. Only spawn agents relevant to the `$ARGUMENTS` scope.

---

#### Agent 1 — Schema Auditor

Read all database models, ORM schema files, migration files, and API route definitions discovered in Step 0. For each entity/model, produce:

- A table of all fields with type, whether filterable (has an API query param or index), whether sortable, and any enum or constrained values
- Note fields that are queryable via the API but not surfaced in the frontend
- Document primary keys, foreign keys, and relationship structure
- Pay special attention to: date/time fields, priority fields, type/category enums, status enums, scope/project relationships, and soft-delete or archival fields

Adapt to the detected ORM:
- **Prisma**: Parse `model` blocks, `@relation`, `@unique`, enums
- **Django**: Parse `models.Model` subclasses, `class Meta`, field types, `choices`
- **SQLAlchemy**: Parse `Column()`, `relationship()`, `Index()`
- **Drizzle**: Parse `createTable()`, column definitions, indexes
- **Rails**: Parse `db/schema.rb` + model files with `belongs_to`, `has_many`, validations, scopes
- **Other**: Document raw schema files and note the format

Also document API endpoints and their query parameters (filters, sorts, pagination).

Output format:

```
## Schema Audit

### Entity: [Name]
| Field | Type | Filterable | Sortable | Enum values | Exposed in UI | Notes |
|-------|------|------------|----------|-------------|---------------|-------|
```

---

#### Agent 2 — Frontend Component Inventory

Walk the entire frontend directory structure. For each page/route, document:

- The route path and file path
- All components rendered on that page
- All filter, sort, and search controls currently present (if any)
- Data fields displayed to the user
- Interactive actions available (create, edit, delete, archive, resolve, dismiss, etc.)
- Empty states — do they exist? What do they say?
- Hardcoded values, disabled controls, or TODO/FIXME comments indicating planned but unbuilt features
- Shared components that appear on multiple pages

For settings/config pages, also document:
- Each settings tab or section
- What each control does
- Whether settings have explanatory text for new users
- Any missing controls (backend-configurable values with no UI)

Output format:

```
## Component Inventory

### Page: [Name] ([route]) — [file path]
**Components:** [list]
**Current filters/sort controls:** [list or "none"]
**Data fields shown:** [list]
**Actions available:** [list]
**Empty states:** [description or "none found"]
**Observations:** [anything notable, including TODOs or disabled features]
```

---

#### Agent 3 — Design & UX Audit

Evaluate each page and shared component against these categories. Rate each issue **Critical / High / Medium / Low**:

| Category | What to assess |
|----------|----------------|
| **Visual tone** | Does the design match the product's target audience? Is it approachable or intimidating? |
| **Typography** | Is heading/body/label hierarchy clear? Are font sizes and weights consistent? |
| **Color system** | Token-based or hardcoded? Dark/light mode support? Status colors consistent? |
| **Empty states** | Do they exist? Are they helpful, encouraging, and actionable? |
| **Onboarding** | What does a brand-new user see? Is there a first-use flow or guidance? |
| **Navigation** | Can a user find what they need without understanding the data model? |
| **Information density** | Are pages overwhelming or appropriately scannable? Progressive disclosure used? |
| **Component consistency** | Are similar patterns (pills, filters, cards, side panels) visually consistent? |
| **Accessibility** | Visible focus states, sufficient contrast, label clarity, ARIA usage |
| **Responsive** | Any responsive behavior, or desktop-only? Mobile breakpoints? |

For **settings/config pages** specifically, also assess:
- Is the settings area discoverable from the main navigation?
- Do configuration options explain what they do for a new user?
- Is there a logical grouping/hierarchy, or a flat list of controls?
- Are there any missing danger-zone actions (account deletion, data export, etc.)?

Do NOT propose solutions. Only identify and rate problems.

Output format:

```
## Design & UX Audit

### Page: [Name]
| Issue | Severity | Description |
|-------|----------|-------------|

### Cross-Page Pattern Issues
| Issue | Severity | Pages affected | Description |
|-------|----------|----------------|-------------|
```

---

#### Agent 4 — Landing Page Audit

Skip this agent if no landing page was detected in Step 0 or `--skip-landing` was passed.

Audit the landing page with fresh eyes as a potential user who has never heard of this product:

- Where does it live in the repo and how is it deployed/served?
- Does it explain what the product does in plain language within the first viewport?
- Does the value proposition land for the target audience?
- Is the visual design consistent with (or divergent from) the main app?
- What is missing: social proof, use cases, pricing clarity, setup instructions, CTAs?
- Is there a signup/onboarding flow? Where does it lead?
- How does the tone compare to the product itself?

Rate each finding **Critical / High / Medium / Low**.

Output format:

```
## Landing Page Audit

**Location:** [path]
**Deployment:** [how it is served, if determinable]

### Findings
| Area | Issue | Severity |
|------|-------|----------|

### Missing Elements
[list]

### Tone & Consistency Assessment
[paragraph]
```

---

#### Agent 5 — Backend-to-UI Coverage Matrix

Cross-reference schema fields and API capabilities (from Agent 1's scope) with frontend controls (from Agent 2's scope). This agent does its own reads rather than waiting for other agents.

For each entity that has a user-facing page, create a matrix:

- Rows: filterable or sortable backend fields
- Columns: UI pages where this entity appears
- Cell values: `Y` Exposed | `~` Partial (only some values, or read-only) | `N` Missing | `-` N/A

Then produce a prioritized gap list:

| Priority | Criteria |
|----------|----------|
| **P0 (Critical)** | Fields a user would expect to filter on given the page's purpose (e.g., date range on a timeline, status on a task list) |
| **P1 (High)** | Fields that power users would want (e.g., source filter, sort by updated date) |
| **P2 (Medium)** | Admin or analytical filters that improve confidence (e.g., entity type filter, time range on analytics) |
| **P3 (Low)** | Internal or metadata fields unlikely to be user-facing |

Also audit settings pages for backend coverage: are all backend-configurable values surfaced in the UI?

Output format:

```
## Backend-to-UI Coverage Matrix

### Entity: [Name]
| Field | Page1 | Page2 | Page3 | ... |
|-------|-------|-------|-------|-----|

### Prioritized Gap List
| Priority | Entity | Field | Missing from | Rationale |
|----------|--------|-------|--------------|-----------|
```

---

### 2. Synthesize report

After all agents return, combine everything into a single structured file.

Write the report to `$OUTPUT_PATH` (default: `docs/ux-audit-YYYY-MM-DD.md` using today's date). Create the `docs/` directory if it does not exist.

```
# UI/UX Audit — {project-name} — YYYY-MM-DD

## Executive Summary
[~300 words: current state, top 5 most impactful gaps, recommended sequencing]

## 1. Schema Audit
[Agent 1 output]

## 2. Component Inventory
[Agent 2 output]

## 3. Design & UX Audit
[Agent 3 output]

## 4. Landing Page Audit
[Agent 4 output, or "Skipped — no landing page detected"]

## 5. Backend-to-UI Coverage Matrix
[Agent 5 output]
```

Unless `--no-issues` was passed, also include:

```
## 6. Proposed GitHub Issue Structure

### ux-overhaul — Visual & UX issues
[Issues for: theming, typography, empty states, onboarding, nav, component consistency]

### coverage — Backend-to-UI gaps
[Issues for: missing filters, sort controls, date pickers, interactivity gaps]

### settings-ux — Settings & config improvements
[Issues for: discoverability, onboarding guidance, missing controls, billing/quota clarity]

### landing — Landing page improvements
[Issues for: copy, value prop, CTAs, social proof, design consistency]
```

For each issue:

```
### [MILESTONE] Issue title
**Labels:** [bug | enhancement | ux | coverage | landing]
**Description:** [1-2 sentences]
**Acceptance criteria:**
- [ ] ...
```

Order issues within each milestone by severity (Critical first).

### 3. Present results

Show the **Executive Summary** in the conversation. Then print the report file path so the user can review the full output.

If a `roadmap.md` exists at the repo root, suggest (but do not automatically append) a roadmap additions block the user can paste in.

## Rules

1. **Read-only.** Do not modify any application code, config, or assets.
2. All findings must reference specific **file paths and line numbers** where possible.
3. Severity ratings must be justified with **concrete evidence**, not assumptions.
4. Do not fabricate data. If a section cannot be completed due to missing files, say so explicitly.
5. The coverage matrix must only flag gaps where the backend **provably supports** a capability the frontend does not expose.
6. If the project structure is unrecognizable or has no clear frontend, report what was found and stop gracefully rather than guessing.
7. Agents must be selective in what they read. Summarize rather than quote entire files. Focus on route definitions, model schemas, and component interfaces — not every implementation detail.
8. If Engram MCP is available, check for existing commitments or decisions related to UI/UX work and incorporate them into the executive summary.
