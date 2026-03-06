"""Sp3cMar CLI - global skill installer for feature/docs/review workflows."""

import logging
import sys
from pathlib import Path

import click
from rich.console import Console

from sp3cmar.exceptions import Sp3cMarError
from sp3cmar.providers import supported_providers

console = Console()
AI_CHOICES = supported_providers()

logger = logging.getLogger(__name__)


class Sp3cMarGroup(click.Group):
    """Click group that catches Sp3cMarError and prints clean messages."""

    def invoke(self, ctx: click.Context) -> None:
        try:
            super().invoke(ctx)
        except Sp3cMarError as exc:
            console.print(f"[red]Error:[/red] {exc}")
            logger.debug("Sp3cMarError details", exc_info=True)
            sys.exit(1)


@click.group(cls=Sp3cMarGroup)
@click.version_option()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging output")
def main(verbose: bool) -> None:
    """Sp3cMar: install and manage global skills for Claude Code/Codex."""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(levelname)s %(name)s:%(lineno)d %(message)s",
        force=True,
    )


@main.command()
@click.option(
    "--list", "list_skills", is_flag=True, help="List available skills without installing"
)
@click.option(
    "--clean", is_flag=True, help="Remove stale artifacts not in current skill/agent lists"
)
@click.option(
    "--ai",
    type=click.Choice(AI_CHOICES),
    default="claude",
    show_default=True,
    help="AI assistant provider",
)
def install(list_skills: bool, clean: bool, ai: str) -> None:
    """Install Sp3cMar skills globally for the selected AI provider."""
    from sp3cmar.commands.install import run_install

    run_install(list_skills, console, clean=clean, ai=ai)


@main.command()
@click.option(
    "--dry-run", is_flag=True, help="Preview what would be removed without making changes"
)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
@click.option(
    "--ai",
    type=click.Choice(AI_CHOICES),
    default="claude",
    show_default=True,
    help="AI assistant provider",
)
def uninstall(dry_run: bool, yes: bool, ai: str) -> None:
    """Remove Sp3cMar artifacts from global provider config."""
    from sp3cmar.commands.uninstall import run_uninstall

    run_uninstall(dry_run, yes, console, ai=ai)


@main.command()
@click.argument("skill", required=False)
def docs(skill: str | None) -> None:
    """Show documentation for Sp3cMar workflow or a specific skill."""
    from sp3cmar.commands.docs import run_docs

    run_docs(skill, console)


@main.command("build-plugin")
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    default=None,
    help="Output directory (default: ./cowork-plugin)",
)
def build_plugin(output: Path | None) -> None:
    """Generate Cowork plugin directory from source templates."""
    from sp3cmar.commands.build_plugin import run_build_plugin

    run_build_plugin(output, console)


if __name__ == "__main__":
    main()
