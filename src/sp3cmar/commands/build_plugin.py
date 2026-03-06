"""Build Cowork plugin directory from templates."""

import logging
from pathlib import Path

from rich.console import Console

from sp3cmar.constants import (
    COWORK_AGENTS,
    COWORK_ONLY_SKILLS,
    COWORK_SKILLS,
)
from sp3cmar.providers.cowork import CoworkProvider, write_plugin_manifest
from sp3cmar.utils.files import safe_mkdir, safe_read_text, safe_write_text
from sp3cmar.utils.paths import get_template_path

logger = logging.getLogger(__name__)


def run_build_plugin(output: Path | None, console: Console) -> None:
    """Generate the cowork-plugin directory from source templates."""
    from sp3cmar import __version__

    provider = CoworkProvider()
    plugin_dir = output or Path.cwd() / "cowork-plugin"

    console.print(f"\n[bold]Building Cowork plugin → {plugin_dir}[/bold]\n")

    skills_dir = plugin_dir / "skills"
    agents_dir = plugin_dir / "agents"
    safe_mkdir(skills_dir, parents=True, exist_ok=True)
    safe_mkdir(agents_dir, parents=True, exist_ok=True)

    skills_template_dir = get_template_path("skills")
    agents_template_dir = get_template_path("agents")

    skill_count = _build_skills(
        COWORK_SKILLS + COWORK_ONLY_SKILLS,
        skills_template_dir,
        skills_dir,
        provider,
        console,
    )

    agent_count = _build_agents(
        COWORK_AGENTS,
        agents_template_dir,
        skills_template_dir,
        agents_dir,
        provider,
        console,
    )

    write_plugin_manifest(plugin_dir, __version__)
    console.print("  [green]✓[/green] plugin.json")

    console.print(f"\n[bold green]Done![/bold green] {skill_count} skills, {agent_count} agents")
    console.print(f"  Plugin directory: {plugin_dir}")


def _build_skills(
    skills: list[str],
    template_dir: Path,
    output_dir: Path,
    provider: CoworkProvider,
    console: Console,
) -> int:
    count = 0
    for skill_filename in skills:
        source = template_dir / skill_filename
        if not source.exists():
            console.print(f"  [yellow]⚠[/yellow] {skill_filename} (template not found)")
            continue

        content = safe_read_text(source)
        rendered = provider.render_skill_content(skill_filename, content)
        target = provider.resolve_skill_target(output_dir, skill_filename)

        safe_mkdir(target.parent, parents=True, exist_ok=True)
        safe_write_text(target, rendered)
        console.print(f"  [green]✓[/green] skills/{skill_filename.removesuffix('.md')}/SKILL.md")
        count += 1

    return count


def _build_agents(
    agents: list[str],
    agents_template_dir: Path,
    skills_template_dir: Path,
    output_dir: Path,
    provider: CoworkProvider,
    console: Console,
) -> int:
    count = 0
    for agent_filename in agents:
        source = agents_template_dir / agent_filename
        if not source.exists():
            source = skills_template_dir / agent_filename
        if not source.exists():
            console.print(f"  [yellow]⚠[/yellow] {agent_filename} (template not found)")
            continue

        content = safe_read_text(source)
        rendered = provider.render_agent_content(agent_filename, content)
        target = provider.resolve_agent_target(output_dir, agent_filename)

        safe_mkdir(target.parent, parents=True, exist_ok=True)
        safe_write_text(target, rendered)
        console.print(f"  [green]✓[/green] agents/{agent_filename.removesuffix('.md')}/AGENT.md")
        count += 1

    return count
