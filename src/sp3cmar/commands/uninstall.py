"""Uninstall Sp3cMar artifacts from global provider scope."""

import logging
from pathlib import Path

from rich.console import Console

from sp3cmar.constants import AGENTS, SKILLS
from sp3cmar.providers import get_provider
from sp3cmar.providers.base import Provider
from sp3cmar.utils.files import safe_rmdir, safe_unlink

logger = logging.getLogger(__name__)


def run_uninstall(
    dry_run: bool,
    yes: bool,
    console: Console,
    *,
    ai: str = "claude",
) -> None:
    """Remove Sp3cMar artifacts from global config."""
    provider = get_provider(ai)
    targets = _collect_targets(provider)

    if not targets:
        console.print("[yellow]No Sp3cMar files found globally.[/yellow]")
        return

    if dry_run:
        _print_dry_run(targets, console)
        return

    if not yes and not _confirm(targets, console):
        console.print("\nCancelled.")
        return

    console.print("\n[bold]Removing global artifacts...[/bold]")
    removed_count = _remove_files(targets, console)
    _cleanup_empty_dirs(provider, console)
    provider.clear_agent_registry(provider.get_paths(global_=True).config_dir)

    console.print(f"\n[bold green]Done![/bold green] Removed {removed_count} file(s).")
    _print_guidance(console)


def _collect_targets(provider: Provider) -> list[Path]:
    """Collect provider-specific global Sp3cMar skill/agent target files."""
    targets: list[Path] = []

    paths = provider.get_paths(global_=True)
    commands_dir = paths.commands_dir
    if commands_dir.exists():
        for skill in SKILLS:
            target = provider.resolve_skill_target(commands_dir, skill)
            if target.exists() and not target.is_symlink():
                targets.append(target)

    if provider.supports_agents:
        agents_dir = paths.agents_dir
        if agents_dir.exists():
            for agent in AGENTS:
                agent_target = provider.resolve_agent_target(agents_dir, agent)
                if (
                    agent_target is not None
                    and agent_target.exists()
                    and not agent_target.is_symlink()
                ):
                    targets.append(agent_target)

    return targets


def _print_dry_run(targets: list[Path], console: Console) -> None:
    """Print dry-run preview of planned actions."""
    console.print("\n[bold][DRY RUN] The following actions would be performed:[/bold]\n")
    for file_path in targets:
        console.print(f"  [dim][DRY RUN][/dim] Remove: {file_path}")
    console.print()


def _confirm(targets: list[Path], console: Console) -> bool:
    """Show summary and prompt for confirmation. Returns True to proceed."""
    console.print("\n[bold]The following will be removed:[/bold]\n")
    console.print(f"  Global files: {len(targets)}")
    for file_path in targets:
        console.print(f"    {file_path.name}")

    try:
        response = console.input("\n[bold]Proceed? [y/N]: [/bold]")
    except EOFError:
        return False

    return response.strip().lower() == "y"


def _remove_files(targets: list[Path], console: Console) -> int:
    """Remove target files, reporting per-file errors. Returns count removed."""
    removed = 0
    for file_path in targets:
        try:
            safe_unlink(file_path)
            console.print(f"  [green]✓[/green] Removed {file_path.name}")
            removed += 1
        except FileNotFoundError:
            console.print(f"  [dim]○[/dim] {file_path.name} (already gone)")
        except OSError as err:
            console.print(f"  [red]✗[/red] Failed {file_path.name}: {err}")
    return removed


def _cleanup_empty_dirs(provider: Provider, console: Console) -> None:
    """Remove empty provider subdirectories left after uninstall."""
    paths = provider.get_paths(global_=True)

    for directory in [paths.commands_dir, paths.agents_dir]:
        try:
            if (
                directory.exists()
                and directory.is_dir()
                and not directory.is_symlink()
                and not any(directory.iterdir())
            ):
                safe_rmdir(directory)
                console.print(f"  [dim]Removed empty {directory}[/dim]")
        except OSError:
            continue


def _print_guidance(console: Console) -> None:
    """Print post-uninstall guidance."""
    console.print("\nIf installed via pipx/uv and no longer needed:")
    console.print("  pip uninstall sp3cmar")
    console.print("  # or")
    console.print("  uv tool uninstall sp3cmar")
