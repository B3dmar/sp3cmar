"""Sp3cMar artifact definitions — single source of truth."""

SKILL_PREFIX = "sp3cmar-"

SKILLS = [
    # Workflow commands
    "ship.md",
    "done.md",
    "morning.md",
    "post-merge.md",
    "worktree.md",
    "doc-audit.md",
    "workflow-audit.md",
    "staging-audit.md",
    "fix.md",
    "migrate.md",
    # Spec & review
    "feature.md",
    "review-codebase.md",
    "review-kill.md",
    "review-pr.md",
    "docs.md",
    # Plan & build
    "breakdown.md",
    "implement.md",
    "review-contract.md",
    # Review
    "review-test.md",
    # Ship
    "release-notes.md",
    "review-env.md",
    # Maintain
    "review-debt.md",
    "review-deps.md",
    # Ops
    "incident.md",
]

AGENTS = [
    "feature.md",
    "review-codebase.md",
    "review-kill.md",
    "review-pr.md",
    "docs.md",
    "reviewer-correctness.md",
    # New reviewers
    "reviewer-hardcoded.md",
    "reviewer-contract.md",
    "reviewer-env.md",
    "reviewer-test.md",
    "reviewer-deps.md",
    "reviewer-debt.md",
    "migration-check.md",
]

skill_info: dict[str, tuple[str, str]] = {
    # Workflow commands
    "ship.md": ("/sp3cmar-ship", "Lint, commit, push, and create PR in one step"),
    "done.md": ("/sp3cmar-done", "Debrief the session and close"),
    "morning.md": ("/sp3cmar-morning", "Morning briefing — context, commitments, priorities"),
    "post-merge.md": ("/sp3cmar-post-merge", "Post-merge cascade — update tracking artifacts"),
    "worktree.md": ("/sp3cmar-worktree", "Git worktree lifecycle — start, done, list, stale"),
    "doc-audit.md": ("/sp3cmar-doc-audit", "Audit tracking artifacts for drift"),
    "workflow-audit.md": (
        "/sp3cmar-workflow-audit",
        "Analyze conversations for repeating patterns and automation opportunities",
    ),
    "staging-audit.md": (
        "/sp3cmar-staging-audit",
        "Pre-merge audit — open PRs, blockers, staging↔main delta, roadmap",
    ),
    "fix.md": ("/sp3cmar-fix", "Auto-fix review findings via /simplify and /batch"),
    "migrate.md": ("/sp3cmar-migrate", "Codebase migration — scan, plan, execute bulk refactors"),
    # Spec & review
    "feature.md": ("/sp3cmar-feature", "Create PRD/spec artifacts with acceptance criteria"),
    "review-codebase.md": ("/sp3cmar-review-codebase", "Run codebase architecture review"),
    "review-kill.md": ("/sp3cmar-review-kill", "Run adversarial kill report"),
    "review-pr.md": ("/sp3cmar-review-pr", "Review PR for correctness, risks, and doc impact"),
    "docs.md": ("/sp3cmar-docs", "Create and maintain high-quality, non-duplicative docs"),
    # Plan & build
    "breakdown.md": (
        "/sp3cmar-breakdown",
        "Break approved spec into ordered stacked PRs under 200 lines",
    ),
    "implement.md": (
        "/sp3cmar-implement",
        "Autonomous feature implementation — spec/issue to working PR",
    ),
    "review-contract.md": (
        "/sp3cmar-review-contract",
        "Validate frontend-backend API contract alignment",
    ),
    # Review
    "review-test.md": (
        "/sp3cmar-review-test",
        "Audit test quality, coverage gaps, and test smells",
    ),
    # Ship
    "release-notes.md": (
        "/sp3cmar-release-notes",
        "Generate release notes from staging-to-main diff",
    ),
    "review-env.md": (
        "/sp3cmar-review-env",
        "Audit environment variable consistency across configs",
    ),
    # Maintain
    "review-debt.md": (
        "/sp3cmar-review-debt",
        "Quantify tech debt — TODOs, hotspots, and trend tracking",
    ),
    "review-deps.md": (
        "/sp3cmar-review-deps",
        "Audit dependency health, CVEs, unused deps, and license conflicts",
    ),
    # Ops
    "incident.md": (
        "/sp3cmar-incident",
        "Incident response — trace errors, check deployments, generate postmortem",
    ),
}

SKILL_CATEGORIES: dict[str, list[str]] = {
    "Workflow": [
        "ship.md",
        "done.md",
        "morning.md",
        "post-merge.md",
        "worktree.md",
        "doc-audit.md",
        "workflow-audit.md",
        "staging-audit.md",
        "fix.md",
        "migrate.md",
    ],
    "Spec & Review": [
        "feature.md",
        "review-codebase.md",
        "review-kill.md",
        "review-pr.md",
        "docs.md",
    ],
    "Plan & Build": ["breakdown.md", "implement.md", "review-contract.md"],
    "Review": ["review-test.md"],
    "Ship": ["release-notes.md", "review-env.md"],
    "Maintain": ["review-debt.md", "review-deps.md"],
    "Ops": ["incident.md"],
}

COWORK_SKILLS: list[str] = []

COWORK_AGENTS: list[str] = []

COWORK_ONLY_SKILLS = [
    "e2e-test.md",
]

ENGRAM_SKILLS = [
    "morning-briefing.md",
    "session-debrief.md",
    "doc-audit.md",
]

agent_info: dict[str, tuple[str, str]] = {
    "feature.md": ("Feature", "Create PRD/spec artifacts with acceptance criteria"),
    "review-codebase.md": ("Review Codebase", "Run codebase architecture review"),
    "review-kill.md": ("Review Kill", "Run adversarial kill report"),
    "review-pr.md": ("Review PR", "Review PR for correctness, risks, and doc impact"),
    "docs.md": ("Docs", "Create and maintain high-quality, non-duplicative docs"),
    "reviewer-correctness.md": ("Correctness", "Reviewer: Bugs and logic errors"),
    # New reviewers
    "reviewer-hardcoded.md": (
        "Hardcoded Values",
        "Reviewer: Hardcoded values that should be config",
    ),
    "reviewer-contract.md": ("API Contract", "Reviewer: Frontend-backend API contract alignment"),
    "reviewer-env.md": ("Env Config", "Reviewer: Environment variable consistency"),
    "reviewer-test.md": ("Test Quality", "Reviewer: Test quality and coverage gaps"),
    "reviewer-deps.md": ("Dependencies", "Reviewer: Dependency health and CVEs"),
    "reviewer-debt.md": ("Tech Debt", "Reviewer: Technical debt quantification"),
    "migration-check.md": ("Migration Safety", "Reviewer: Database migration safety"),
}
