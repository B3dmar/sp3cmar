---
description: Audit and improve technical SEO, schema markup, and AI-answer visibility
triggers:
  - SEO
  - GEO
  - search visibility
  - AI visibility
  - schema markup
  - JSON-LD
  - metadata audit
providers:
  - claude
  - codex
requires_tools:
  - web
  - git
---

# SEO/GEO Audit Skill

Use this skill when the user wants to improve discoverability of a technical product, docs site, landing page, or content library in both:

- Traditional search engines: Google, Bing
- AI answer engines: ChatGPT, Perplexity, Claude, Gemini, Copilot

## Goal

Produce concrete recommendations or code changes that improve:

- Crawlability and indexing
- Metadata quality
- Structured data coverage
- Internal linking and topic structure
- "Answer-first" content design that is easier for AI systems to cite

## Working Rules

1. Always inspect the real site or page before recommending changes. If the URL is public, browse it.
2. Treat current search/AI behavior as time-sensitive. Verify claims instead of relying on memory.
3. Prefer technical, implementable recommendations over generic marketing advice.
4. If working inside a codebase, map each recommendation to the relevant files or templates.
5. Distinguish between:
   - **Technical SEO**: robots, sitemap, canonicals, metadata, headings, schema, rendering
   - **Content SEO**: keyword targeting, page intent, internal links, information architecture
   - **GEO**: citation likelihood in AI answers, factual density, source attribution, answer-first structure

## Audit Workflow

### Step 1: Scope

Identify:

- The target URL, domain, or repo
- The page type: marketing page, docs, blog, changelog, product page, FAQ
- The main query or topic it should rank or be cited for
- The intended audience and geographic/language constraints

### Step 2: Technical Crawlability Review

Check:

- `<title>` quality and uniqueness
- Meta description presence and quality
- Canonical tags
- Heading hierarchy
- Robots directives and `robots.txt`
- Sitemap presence and coverage
- Open Graph / Twitter tags
- Server-side rendering or hydration issues that affect indexing
- Page speed or obvious asset/rendering problems

When possible, inspect:

- Home page HTML
- Target page HTML
- `/robots.txt`
- `/sitemap.xml`

### Step 3: Structured Data Review

Check whether relevant JSON-LD exists and whether it matches the page intent.

Use the closest fitting schema type when applicable:

- `SoftwareApplication`
- `Product`
- `Article`
- `TechArticle`
- `FAQPage`
- `Organization`
- `BreadcrumbList`

If schema is missing or weak:

- Propose the exact JSON-LD block to add
- Place it in the most relevant template/component
- Keep fields factual and avoid fabricated claims

### Step 4: Content and Query Fit

Evaluate whether the page clearly answers the target query.

Look for:

- An answer-first opening
- Clear, scannable headings
- Definitions near the top
- Concrete examples
- Tables or comparison blocks where useful
- Citations or references for non-obvious claims
- Internal links to supporting pages

Flag pages that are:

- Too vague
- Too brand-heavy
- Too thin to be cited
- Buried without internal links
- Competing with other pages on the same topic

### Step 5: GEO Review

Optimize for citation likelihood in AI-generated answers.

Prefer content that is:

- Fact-dense and explicit
- Structured around direct questions and direct answers
- Supported by named sources or primary references
- Updated and dated when freshness matters
- Broken into sections that can be quoted or summarized cleanly

Improve pages by adding:

- Short definitional paragraphs
- FAQ sections only when they add real value
- Comparison tables
- Source-backed claims and references
- Clear terminology and entity naming

Avoid:

- Keyword stuffing
- Empty FAQ spam
- Boilerplate content with no original information
- Schema that contradicts visible page content

## Codebase Mode

If you are working inside the repository, map findings to exact files and propose or implement changes such as:

- Metadata updates in page templates/layouts
- Canonical generation fixes
- Sitemap generation fixes
- Robots rules
- JSON-LD components
- Heading/content structure edits
- Internal links between docs or marketing pages

If the user asked for implementation, make the changes and summarize the SEO/GEO impact.

## Deliverable

Return a concise report with:

## SEO/GEO Report

**Target**: {url or repo area}
**Intent**: {main query / audience}

### Findings

- `Critical`: Issues blocking crawlability, indexing, or canonicalization
- `High`: Missing or incorrect metadata/schema on important pages
- `Medium`: Weak answer structure, thin content, poor internal linking
- `Low`: Polish improvements

### Recommended Changes

- Exact technical fixes
- Exact content-structure fixes
- Exact schema additions

### Implementation Map

- File or template references for each change

### GEO Notes

- Why the page is or is not likely to be cited by AI systems

If you cannot inspect the live page, state that clearly and limit conclusions to codebase evidence only.
