"""Canonical catalog for Sp3cMar skills, agents, and extensions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SkillSpec:
    """Machine-readable definition for an installable skill."""

    slug: str
    command: str
    description: str
    category: str
    providers: tuple[str, ...]
    triggers: tuple[str, ...] = ()
    requires_tools: tuple[str, ...] = ()
    requires_mcp: tuple[str, ...] = ()
    requires_env: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()

    @property
    def filename(self) -> str:
        return f"{self.slug}.md"

    def requirements_summary(self) -> str:
        parts = [
            *(f"tools:{tool}" for tool in self.requires_tools),
            *(f"mcp:{mcp}" for mcp in self.requires_mcp),
            *(f"env:{env}" for env in self.requires_env),
        ]
        return ", ".join(parts) if parts else "-"

    def manifest_entry(self) -> dict[str, object]:
        return {
            "name": self.slug,
            "filename": self.filename,
            "command": self.command,
            "description": self.description,
            "category": self.category,
            "providers": list(self.providers),
            "triggers": list(self.triggers),
            "requires_tools": list(self.requires_tools),
            "requires_mcp": list(self.requires_mcp),
            "requires_env": list(self.requires_env),
            "tags": list(self.tags),
        }


@dataclass(frozen=True)
class AgentSpec:
    """Machine-readable definition for an installable agent."""

    slug: str
    name: str
    description: str
    providers: tuple[str, ...] = ("claude", "codex")
    focus: tuple[str, ...] = ()

    @property
    def filename(self) -> str:
        return f"{self.slug}.md"

    def manifest_entry(self) -> dict[str, object]:
        return {
            "name": self.slug,
            "filename": self.filename,
            "role": self.name,
            "description": self.description,
            "providers": list(self.providers),
            "focus": list(self.focus),
        }


@dataclass(frozen=True)
class ExtensionSpec:
    """Machine-readable definition for non-core extensions."""

    slug: str
    description: str
    channel: str
    providers: tuple[str, ...] = ()
    requires_mcp: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()

    @property
    def filename(self) -> str:
        return f"{self.slug}.md"

    def manifest_entry(self) -> dict[str, object]:
        return {
            "name": self.slug,
            "filename": self.filename,
            "description": self.description,
            "channel": self.channel,
            "providers": list(self.providers),
            "requires_mcp": list(self.requires_mcp),
            "tags": list(self.tags),
        }


CORE_SKILL_SPECS: tuple[SkillSpec, ...] = (
    SkillSpec(
        slug="ship",
        command="/sp3cmar-ship",
        description="Lint, commit, push, and create PR in one step",
        category="Workflow",
        providers=("claude", "codex"),
        triggers=("ship", "open a PR", "finalize changes"),
        requires_tools=("git", "gh"),
        tags=("workflow", "release"),
    ),
    SkillSpec(
        slug="done",
        command="/sp3cmar-done",
        description="Debrief the session and close",
        category="Workflow",
        providers=("claude", "codex"),
        triggers=("done", "debrief", "wrap up"),
        requires_mcp=("engram",),
        tags=("workflow", "memory"),
    ),
    SkillSpec(
        slug="morning",
        command="/sp3cmar-morning",
        description="Morning briefing — context, commitments, priorities",
        category="Workflow",
        providers=("claude", "codex"),
        triggers=("morning", "briefing", "priorities"),
        requires_mcp=("engram",),
        tags=("workflow", "planning"),
    ),
    SkillSpec(
        slug="post-merge",
        command="/sp3cmar-post-merge",
        description="Post-merge cascade — update tracking artifacts",
        category="Workflow",
        providers=("claude", "codex"),
        triggers=("post-merge", "after merge", "cascade"),
        requires_mcp=("engram",),
        tags=("workflow", "tracking"),
    ),
    SkillSpec(
        slug="worktree",
        command="/sp3cmar-worktree",
        description="Git worktree lifecycle — start, done, list, stale",
        category="Workflow",
        providers=("claude", "codex"),
        triggers=("worktree", "parallel workspace"),
        requires_tools=("git",),
        tags=("workflow", "git"),
    ),
    SkillSpec(
        slug="doc-audit",
        command="/sp3cmar-doc-audit",
        description="Audit tracking artifacts for drift",
        category="Workflow",
        providers=("claude", "codex"),
        triggers=("doc audit", "drift", "tracking"),
        requires_mcp=("engram",),
        tags=("docs", "audit"),
    ),
    SkillSpec(
        slug="workflow-audit",
        command="/sp3cmar-workflow-audit",
        description="Analyze conversations for repeating patterns and automation opportunities",
        category="Workflow",
        providers=("claude", "codex"),
        triggers=("workflow audit", "automation opportunities"),
        requires_mcp=("engram",),
        tags=("workflow", "automation"),
    ),
    SkillSpec(
        slug="staging-audit",
        command="/sp3cmar-staging-audit",
        description="Pre-merge audit — open PRs, blockers, staging↔main delta, roadmap",
        category="Workflow",
        providers=("claude", "codex"),
        triggers=("staging audit", "pre-merge audit"),
        requires_tools=("git", "gh"),
        requires_mcp=("engram",),
        tags=("workflow", "release"),
    ),
    SkillSpec(
        slug="fix",
        command="/sp3cmar-fix",
        description="Auto-fix review findings via /simplify and /batch",
        category="Workflow",
        providers=("claude", "codex"),
        triggers=("fix findings", "batch fixes"),
        tags=("workflow", "repair"),
    ),
    SkillSpec(
        slug="migrate",
        command="/sp3cmar-migrate",
        description="Codebase migration — scan, plan, execute bulk refactors",
        category="Workflow",
        providers=("claude", "codex"),
        triggers=("migrate", "bulk refactor"),
        tags=("workflow", "migration"),
    ),
    SkillSpec(
        slug="feature",
        command="/sp3cmar-feature",
        description="Create PRD/spec artifacts with acceptance criteria",
        category="Spec & Review",
        providers=("claude", "codex"),
        triggers=("spec", "PRD", "acceptance criteria"),
        tags=("planning", "spec"),
    ),
    SkillSpec(
        slug="review",
        command="/sp3cmar-review",
        description="Unified code review — run one or all review types (all, pr, codebase, kill, test, debt, deps, env, contract)",
        category="Spec & Review",
        providers=("claude", "codex"),
        triggers=("review", "code review", "audit", "PR review", "architecture review", "kill report"),
        tags=("review",),
    ),
    SkillSpec(
        slug="docs",
        command="/sp3cmar-docs",
        description="Create and maintain high-quality, non-duplicative docs",
        category="Spec & Review",
        providers=("claude", "codex"),
        triggers=("docs", "documentation", "write docs"),
        tags=("docs",),
    ),
    SkillSpec(
        slug="breakdown",
        command="/sp3cmar-breakdown",
        description="Break approved spec into ordered stacked PRs under 200 lines",
        category="Plan & Build",
        providers=("claude", "codex"),
        triggers=("break down spec", "stacked PRs"),
        tags=("planning", "delivery"),
    ),
    SkillSpec(
        slug="implement",
        command="/sp3cmar-implement",
        description="Autonomous feature implementation — spec/issue to working PR",
        category="Plan & Build",
        providers=("claude", "codex"),
        triggers=("implement", "build this feature"),
        tags=("delivery", "implementation"),
    ),
    # review-contract and review-test merged into unified /sp3cmar-review
    SkillSpec(
        slug="release-notes",
        command="/sp3cmar-release-notes",
        description="Generate release notes from staging-to-main diff",
        category="Ship",
        providers=("claude", "codex"),
        triggers=("release notes", "staging to main"),
        requires_tools=("git",),
        tags=("release", "docs"),
    ),
    # review-env merged into unified /sp3cmar-review
    # review-debt and review-deps merged into unified /sp3cmar-review
    SkillSpec(
        slug="incident",
        command="/sp3cmar-incident",
        description="Incident response — trace errors, check deployments, generate postmortem",
        category="Ops",
        providers=("claude", "codex"),
        triggers=("incident", "outage", "postmortem"),
        requires_tools=("git",),
        tags=("ops", "incident"),
    ),
    SkillSpec(
        slug="seo-geo",
        command="/sp3cmar-seo-geo",
        description="Audit and improve technical SEO, schema markup, and AI-answer visibility",
        category="Growth",
        providers=("claude", "codex"),
        triggers=(
            "SEO",
            "GEO",
            "search visibility",
            "AI visibility",
            "schema markup",
            "JSON-LD",
            "metadata audit",
        ),
        requires_tools=("web", "git"),
        tags=("docs", "growth", "search"),
    ),
)

COWORK_ONLY_SKILL_SPECS: tuple[SkillSpec, ...] = (
    SkillSpec(
        slug="e2e-test",
        command="e2e-test",
        description="Frontend e2e testing via Playwright MCP",
        category="Cowork",
        providers=("cowork",),
        triggers=("e2e", "visual QA", "Playwright"),
        requires_mcp=("playwright",),
        tags=("qa", "frontend"),
    ),
    SkillSpec(
        slug="gsc-audit",
        command="gsc-audit",
        description="Google Search Console audit and reporting for site performance",
        category="Cowork",
        providers=("cowork",),
        triggers=(
            "Google Search Console",
            "GSC",
            "search console audit",
            "SEO report",
            "CTR report",
            "query performance",
        ),
        tags=("seo", "reporting", "growth"),
    ),
)

AGENT_SPECS: tuple[AgentSpec, ...] = (
    AgentSpec("feature", "Feature", "Create PRD/spec artifacts with acceptance criteria"),
    AgentSpec("review-pr", "Review PR", "Orchestrator: PR review with multi-agent dispatch"),
    AgentSpec("review-codebase", "Review Codebase", "Orchestrator: architecture review with 7 sub-reviewers"),
    AgentSpec("review-kill", "Review Kill", "Orchestrator: adversarial kill case with 6 teams"),
    AgentSpec("docs", "Docs", "Create and maintain high-quality, non-duplicative docs"),
    AgentSpec(
        "reviewer-correctness",
        "Correctness",
        "Reviewer: Bugs and logic errors",
        focus=("bugs", "logic"),
    ),
    AgentSpec(
        "reviewer-hardcoded",
        "Hardcoded Values",
        "Reviewer: Hardcoded values that should be config",
        focus=("configuration", "maintainability"),
    ),
    AgentSpec(
        "reviewer-contract",
        "API Contract",
        "Reviewer: Frontend-backend API contract alignment",
        focus=("api", "contracts"),
    ),
    AgentSpec(
        "reviewer-env",
        "Env Config",
        "Reviewer: Environment variable consistency",
        focus=("configuration", "environment"),
    ),
    AgentSpec(
        "reviewer-test",
        "Test Quality",
        "Reviewer: Test quality and coverage gaps",
        focus=("tests", "coverage"),
    ),
    AgentSpec(
        "reviewer-deps",
        "Dependencies",
        "Reviewer: Dependency health and CVEs",
        focus=("dependencies", "security"),
    ),
    AgentSpec(
        "reviewer-debt",
        "Tech Debt",
        "Reviewer: Technical debt quantification",
        focus=("maintenance", "debt"),
    ),
    AgentSpec(
        "migration-check",
        "Migration Safety",
        "Reviewer: Database migration safety",
        focus=("database", "migration"),
    ),
)

ENGRAM_EXTENSION_SPECS: tuple[ExtensionSpec, ...] = (
    ExtensionSpec(
        slug="morning-briefing",
        description="Session startup with 3ngram recall",
        channel="engram",
        providers=("claude",),
        requires_mcp=("3ngram",),
        tags=("engram", "workflow"),
    ),
    ExtensionSpec(
        slug="session-debrief",
        description="Session close with memory extraction",
        channel="engram",
        providers=("claude",),
        requires_mcp=("3ngram",),
        tags=("engram", "memory"),
    ),
    ExtensionSpec(
        slug="doc-audit",
        description="Cross-ref docs with 3ngram decisions",
        channel="engram",
        providers=("claude",),
        requires_mcp=("3ngram",),
        tags=("engram", "docs"),
    ),
)

SKILL_SPECS_BY_FILENAME: dict[str, SkillSpec] = {
    spec.filename: spec for spec in CORE_SKILL_SPECS + COWORK_ONLY_SKILL_SPECS
}


def build_manifest() -> dict[str, object]:
    """Build a machine-readable project manifest."""

    categories: dict[str, list[str]] = {}
    for spec in CORE_SKILL_SPECS:
        categories.setdefault(spec.category, []).append(spec.filename)

    return {
        "version": "1.0.0",
        "name": "sp3cmar",
        "description": "Workflow skills and reviewer agents for Claude Code, Codex, and Cowork",
        "repository": "https://github.com/b3dmar/sp3cmar",
        "skills": [spec.manifest_entry() for spec in CORE_SKILL_SPECS],
        "cowork_only_skills": [spec.manifest_entry() for spec in COWORK_ONLY_SKILL_SPECS],
        "agents": [spec.manifest_entry() for spec in AGENT_SPECS],
        "extensions": [spec.manifest_entry() for spec in ENGRAM_EXTENSION_SPECS],
        "categories": categories,
    }
