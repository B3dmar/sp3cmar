# sp3cmar

Workflow skills and reviewer agents for Claude Code, Codex, and Cowork.

12 core skills, 2 Cowork skills, 2 3ngram extensions, and 13 agents that bring structured workflows to AI-assisted development: code reviews, shipping, audits, technical SEO/GEO, and more.

## Installation

### Claude Code (CLI)

```bash
uv tool install sp3cmar --from git+https://github.com/b3dmar/sp3cmar.git
sp3cmar install --ai claude
```

Skills are installed as slash commands: `/sp3cmar-ship`, `/sp3cmar-review`, etc.

### Codex (CLI)

```bash
sp3cmar install --ai codex
```

### Cowork (no Python required)

1. Clone this repo (or download `cowork-plugin/` from a release)
2. In Claude Desktop > Cowork > Customize > Add Plugin > point to `cowork-plugin/`
3. Skills auto-activate based on task context

### 3ngram Extensions (no Python required)

Copy skills that enhance the [3ngram MCP](https://github.com/sebastianebg/engram):

```bash
cp extensions/3ngram/skills/*.md ~/.claude/commands/
```

See [`extensions/3ngram/README.md`](extensions/3ngram/README.md) for details.

### Update

```bash
uv tool upgrade sp3cmar
sp3cmar install
```

Only changed skills are overwritten; unchanged skills are skipped.

### Uninstall

```bash
sp3cmar uninstall --yes
uv tool uninstall sp3cmar
```

## Skills

### Workflow

| Skill | Description |
|-------|-------------|
| `/sp3cmar-ship` | Lint, commit, push, and create PR |
| `/sp3cmar-done` | Session debrief and close |
| `/sp3cmar-post-merge` | Post-merge cascade updates |
| `/sp3cmar-worktree` | Git worktree lifecycle |
| `/sp3cmar-doc-audit` | Audit tracking artifacts for drift |
| `/sp3cmar-milestone-audit` | Audit milestone scope, issue hierarchy, and release readiness |
| `/sp3cmar-workflow-audit` | Analyze conversations for automation |
| `/sp3cmar-memory-audit` | Audit 3ngram capture coverage |
| `/sp3cmar-staging-audit` | Pre-merge audit |

### Analysis

| Skill | Description |
|-------|-------------|
| `/sp3cmar-review` | Unified code review (sub-types: `all`, `pr`, `codebase`, `kill`, `test`, `debt`, `deps`, `env`, `contract`) |
| `/sp3cmar-seo-geo` | Technical SEO/GEO audit |
| `/sp3cmar-release-notes` | Generate release notes |

### Cowork

| Skill | Description |
|-------|-------------|
| `e2e-test` | Frontend e2e testing via Playwright MCP |
| `gsc-audit` | Google Search Console audit and reporting |

### 3ngram Extensions

| Skill | Description |
|-------|-------------|
| `session-debrief` | Session close with memory extraction |
| `doc-audit` | Cross-ref docs with 3ngram decisions |

## Agents

5 orchestrator agents and 8 focused reviewers:

| Agent | Focus |
|-------|-------|
| `feature` | PRD/spec creation |
| `review-pr` | PR review orchestrator |
| `review-codebase` | Architecture review orchestrator |
| `review-kill` | Adversarial kill case orchestrator |
| `docs` | Documentation authoring |
| `reviewer-correctness` | Bugs and logic errors |
| `reviewer-hardcoded` | Hardcoded values to extract |
| `reviewer-contract` | API contract alignment |
| `reviewer-env` | Environment variable consistency |
| `reviewer-test` | Test quality and coverage |
| `reviewer-deps` | Dependency health and CVEs |
| `reviewer-debt` | Tech debt quantification |
| `migration-check` | Database migration safety |

## CLI Reference

```
sp3cmar install [--ai claude|codex] [--list] [--clean]
sp3cmar uninstall [--ai claude|codex] [--dry-run] [--yes]
sp3cmar catalog [--output PATH]
sp3cmar build-plugin [--output PATH]
sp3cmar docs [SKILL]
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT
