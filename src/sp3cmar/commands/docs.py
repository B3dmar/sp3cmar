"""sp3cmar docs command - Show documentation."""

import logging

from rich.console import Console
from rich.markdown import Markdown

logger = logging.getLogger(__name__)


def run_docs(skill: str | None, console: Console) -> None:
    """Show documentation for Sp3cMar or a specific skill."""

    if skill:
        _show_skill_docs(skill, console)
    else:
        _show_overview(console)


def _show_overview(console: Console) -> None:
    """Show general documentation."""
    overview = """
# Sp3cMar Workflow

## CLI Commands

| Command | Purpose |
|---------|---------|
| `sp3cmar install` | Install global skills and agents for selected provider |
| `sp3cmar uninstall` | Remove global skills and agents |
| `sp3cmar docs` | Show this documentation |

## Skills (5)

**Core**

| Skill | Purpose |
|-------|---------|
| `/sp3cmar-feature` | Create PRD/spec artifact with acceptance criteria |
| `/sp3cmar-docs` | Create and maintain docs with dedup guidance |

**Review**

| Skill | Purpose |
|-------|---------|
| `/sp3cmar-review-codebase` | Architecture review (versioned, delta tracking) |
| `/sp3cmar-review-kill` | Adversarial "kill case" review |
| `/sp3cmar-review-pr` | Review PR for correctness, risk, and documentation impact |

## Workflow

1. **Specify** - `/sp3cmar-feature "description"`
2. **Implement** - use native Claude/Codex plan mode and maintainable tests
3. **Docs quality** - `/sp3cmar-docs`
4. **Review** - `/sp3cmar-review-pr` (plus codebase/kill as needed)

Run `sp3cmar docs [skill]` for detailed skill documentation.
"""
    console.print(Markdown(overview))


def _show_skill_docs(skill: str, console: Console) -> None:
    """Show documentation for a specific skill."""
    from sp3cmar.utils.paths import get_template_path

    normalized_skill = skill.lstrip("/").lower()
    skill_file = get_template_path("skills") / f"{normalized_skill}.md"

    if not skill_file.exists():
        console.print(f"[red]Unknown skill: {normalized_skill}[/red]")
        console.print("Run [cyan]sp3cmar docs[/cyan] to see available skills.")
        return

    from sp3cmar.utils.files import safe_read_text

    content = safe_read_text(skill_file)
    console.print(Markdown(content))
