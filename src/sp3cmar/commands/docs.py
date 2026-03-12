"""sp3cmar docs command - show overview or skill documentation."""

from __future__ import annotations

import logging

from rich.console import Console
from rich.markdown import Markdown

from sp3cmar.catalog import CORE_SKILL_SPECS
from sp3cmar.utils.files import safe_read_text
from sp3cmar.utils.paths import get_template_path

logger = logging.getLogger(__name__)


def run_docs(skill: str | None, console: Console) -> None:
    """Show documentation for Sp3cMar or a specific skill."""

    if skill:
        _show_skill_docs(skill, console)
    else:
        _show_overview(console)


def _show_overview(console: Console) -> None:
    """Show dynamic overview documentation derived from the catalog."""

    category_rows: list[str] = []
    categories: dict[str, list[tuple[str, str]]] = {}
    for spec in CORE_SKILL_SPECS:
        categories.setdefault(spec.category, []).append((spec.command, spec.description))

    for category, rows in categories.items():
        category_rows.append(f"## {category}\n")
        category_rows.append("| Command | Purpose |")
        category_rows.append("|---------|---------|")
        for command, description in rows:
            category_rows.append(f"| `{command}` | {description} |")
        category_rows.append("")

    overview = "\n".join(
        [
            "# Sp3cMar Workflow",
            "",
            "## CLI Commands",
            "",
            "| Command | Purpose |",
            "|---------|---------|",
            "| `sp3cmar install` | Install global skills and agents for selected provider |",
            "| `sp3cmar uninstall` | Remove global skills and agents |",
            "| `sp3cmar docs` | Show workflow and skill documentation |",
            "| `sp3cmar catalog` | Export the machine-readable skill/agent catalog as JSON |",
            "",
            f"## Skills ({len(CORE_SKILL_SPECS)})",
            "",
            *category_rows,
            "## Workflow",
            "",
            "1. **Specify** - `/sp3cmar-feature`",
            "2. **Implement** - use native Claude/Codex planning and maintainable tests",
            "3. **Review** - `/sp3cmar-review-pr` or specialist review skills",
            "4. **Ship** - `/sp3cmar-ship` or `/sp3cmar-release-notes`",
            "",
            "Run `sp3cmar docs [skill]` for detailed skill documentation.",
        ]
    )
    console.print(Markdown(overview))


def _normalize_skill_slug(skill: str) -> str:
    normalized = skill.strip().lower()
    normalized = normalized.lstrip("/")
    if normalized.startswith("sp3cmar-"):
        normalized = normalized.removeprefix("sp3cmar-")
    return normalized


def _show_skill_docs(skill: str, console: Console) -> None:
    """Show documentation for a specific skill."""

    normalized_skill = _normalize_skill_slug(skill)
    skill_file = get_template_path("skills") / f"{normalized_skill}.md"

    if not skill_file.exists():
        console.print(f"[red]Unknown skill: {normalized_skill}[/red]")
        console.print("Run [cyan]sp3cmar docs[/cyan] to see available skills.")
        return

    content = safe_read_text(skill_file)
    console.print(Markdown(content))
