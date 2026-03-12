"""Install Sp3cMar skills and agents globally."""

import logging
from collections.abc import Callable
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from rich.console import Console
from rich.table import Table

from sp3cmar.catalog import SKILL_SPECS_BY_FILENAME
from sp3cmar.constants import AGENTS, SKILL_CATEGORIES, SKILLS, agent_info, skill_info
from sp3cmar.providers import get_provider
from sp3cmar.providers.base import Provider
from sp3cmar.utils.files import (
    SymlinkError,
    safe_mkdir,
    safe_read_text,
    safe_rmdir,
    safe_unlink,
    safe_write_text,
)
from sp3cmar.utils.paths import get_template_path

logger = logging.getLogger(__name__)


def get_sp3cmar_version() -> str:
    """Get the installed sp3cmar version."""
    try:
        return version("sp3cmar")
    except PackageNotFoundError:
        logger.warning("sp3cmar package not found in installed packages")
        return "unknown"
    except ImportError as e:
        logger.warning("ImportError while getting sp3cmar version: %s", e)
        return "unknown"


def run_install(
    list_skills: bool,
    console: Console,
    *,
    clean: bool = False,
    ai: str = "claude",
) -> None:
    """Install Sp3cMar skills globally."""
    provider = get_provider(ai)
    skills_template_dir = get_template_path("skills")

    if list_skills:
        _list_skills(skills_template_dir, console)
        return

    paths = provider.get_paths(global_=True)
    target_dir = paths.commands_dir

    safe_mkdir(target_dir, parents=True, exist_ok=True)

    console.print("\n[bold]Installing Sp3cMar skills globally...[/bold]\n")

    installed, skipped = _install_artifacts(
        artifacts=SKILLS,
        template_dir=skills_template_dir,
        fallback_template_dir=None,
        target_dir=target_dir,
        resolve_target=provider.resolve_skill_target,
        render_content=provider.render_skill_content,
        console=console,
    )

    agents_installed: list[str] = []
    agents_skipped: list[str] = []
    agents_target_dir = paths.agents_dir
    if provider.supports_agents:
        agents_template_dir = get_template_path("agents")
        safe_mkdir(agents_target_dir, parents=True, exist_ok=True)

        console.print("\n[bold]Installing Sp3cMar agents globally...[/bold]\n")
        agents_installed, agents_skipped = _install_artifacts(
            artifacts=AGENTS,
            template_dir=agents_template_dir,
            fallback_template_dir=skills_template_dir,
            target_dir=agents_target_dir,
            resolve_target=provider.resolve_agent_target,
            render_content=provider.render_agent_content,
            console=console,
        )

        provider.sync_agent_registry(paths.config_dir)
    else:
        console.print("\n[bold]Installing Sp3cMar agents globally...[/bold]\n")
        console.print("  [dim]○[/dim] Agents not supported by this provider")

    _detect_stale_artifacts(provider, target_dir, agents_target_dir, clean, console)

    console.print("\n[bold green]Done![/bold green]")
    console.print(f"  Skills installed: {len(installed)}, skipped: {len(skipped)}")
    console.print(f"  Agents installed: {len(agents_installed)}, skipped: {len(agents_skipped)}")
    console.print(f"\n  Skills location: {target_dir}")
    console.print(f"  Agents location: {agents_target_dir}")

    console.print(f"\n[bold]Available commands ({provider.name}):[/bold]")
    _show_commands(console)


def _install_artifacts(
    *,
    artifacts: list[str],
    template_dir: Path,
    fallback_template_dir: Path | None,
    target_dir: Path,
    resolve_target: Callable[[Path, str], Path | None],
    render_content: Callable[[str, str], str],
    console: Console,
) -> tuple[list[str], list[str]]:
    """Install a list of artifacts (skills or agents), returning (installed, skipped)."""
    installed: list[str] = []
    skipped: list[str] = []

    for artifact in artifacts:
        target = resolve_target(target_dir, artifact)
        if target is None:
            skipped.append(artifact)
            continue

        source = template_dir / artifact
        if not source.exists() and fallback_template_dir is not None:
            source = fallback_template_dir / artifact
        if not source.exists():
            console.print(f"  [yellow]⚠[/yellow] {artifact} not found in package")
            skipped.append(artifact)
            continue

        rendered_content = render_content(artifact, safe_read_text(source))
        safe_mkdir(target.parent, parents=True, exist_ok=True)

        if target.exists():
            if target.is_symlink():
                raise SymlinkError(f"Refusing to overwrite symlink: {target}")
            if rendered_content == safe_read_text(target):
                console.print(f"  [dim]○[/dim] {artifact} (unchanged)")
                skipped.append(artifact)
                continue
            console.print(f"  [blue]↻[/blue] {artifact} (updated)")
        else:
            console.print(f"  [green]✓[/green] {artifact}")

        if target.is_symlink():
            raise SymlinkError(f"Refusing to copy to symlink: {target}")
        safe_write_text(target, rendered_content)
        installed.append(artifact)

    return installed, skipped


def _detect_stale_artifacts(
    provider: Provider,
    skills_dir: Path,
    agents_dir: Path,
    clean: bool,
    console: Console,
) -> None:
    """Detect and optionally remove stale Sp3cMar artifacts."""
    expected_skills = {provider.resolve_skill_target(skills_dir, s) for s in SKILLS}
    expected_agents = {provider.resolve_agent_target(agents_dir, a) for a in AGENTS}
    expected_agents = {p for p in expected_agents if p is not None}

    stale_skills = [
        f for f in provider.iter_managed_skill_targets(skills_dir) if f not in expected_skills
    ]
    stale_agents = [
        f for f in provider.iter_managed_agent_targets(agents_dir) if f not in expected_agents
    ]

    stale = stale_skills + stale_agents
    if not stale:
        return

    console.print(f"\n[yellow]Found {len(stale)} stale artifact(s):[/yellow]")
    for file_path in stale:
        console.print(f"  [dim]{file_path.name}[/dim]")

    if clean:
        for file_path in stale_skills:
            if file_path.is_symlink():
                continue
            safe_unlink(file_path)
            _cleanup_empty_ancestors(file_path.parent, stop=skills_dir)
            console.print(f"  [red]Removed:[/red] {file_path.name}")
        for file_path in stale_agents:
            if file_path.is_symlink():
                continue
            safe_unlink(file_path)
            _cleanup_empty_ancestors(file_path.parent, stop=agents_dir)
            console.print(f"  [red]Removed:[/red] {file_path.name}")
    else:
        console.print("\n  Run with --clean to remove stale artifacts")


def _list_skills(template_dir: Path, console: Console) -> None:
    """List available skills without installing."""
    table = Table(title="Sp3cMar Skills")
    table.add_column("Skill", style="cyan", no_wrap=True)
    table.add_column("Command", style="green", no_wrap=True)
    table.add_column("Providers", style="magenta", no_wrap=True)
    table.add_column("Requirements", style="yellow")
    table.add_column("Description")

    for skill in SKILLS:
        cmd, desc = skill_info.get(skill, ("?", "?"))
        exists = "\u2713" if (template_dir / skill).exists() else "\u2717"
        spec = SKILL_SPECS_BY_FILENAME[skill]
        table.add_row(
            f"{exists} {skill}",
            cmd,
            ", ".join(spec.providers),
            spec.requirements_summary(),
            desc,
        )

    console.print(table)


def _cleanup_empty_ancestors(path: Path, *, stop: Path) -> None:
    """Remove empty directories from path up to (but not including) stop."""
    try:
        path.relative_to(stop)
    except ValueError:
        return

    current = path
    while current != stop and current.exists():
        if any(current.iterdir()):
            return
        safe_rmdir(current)
        current = current.parent


def _show_commands(console: Console) -> None:
    """Show command reference derived from SKILL_CATEGORIES."""
    for category, skills in SKILL_CATEGORIES.items():
        console.print(f"\n  [cyan]{category}[/cyan]")
        for skill in skills:
            cmd, desc = skill_info.get(skill, ("?", "?"))
            console.print(f"    {cmd:<30s} {desc}")

    agent_names = [agent_info.get(a, (a.removesuffix(".md"), ""))[0] for a in AGENTS]
    console.print(f"\n  [cyan]Agents ({len(AGENTS)})[/cyan]")
    console.print(f"    Available: {', '.join(agent_names)}")
