"""Cowork plugin provider adapter."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from sp3cmar.constants import COWORK_ONLY_SKILLS, COWORK_SKILLS, skill_info
from sp3cmar.providers.base import ProviderPaths
from sp3cmar.utils.files import safe_write_text
from sp3cmar.utils.frontmatter import split_frontmatter

logger = logging.getLogger(__name__)

PLUGIN_NAME = "sp3cmar"


class CoworkProvider:
    """Cowork plugin provider implementation.

    Cowork plugins use a directory-based layout:
      <plugin-root>/skills/<skill-name>/SKILL.md
      <plugin-root>/agents/<agent-name>/AGENT.md
      <plugin-root>/.claude-plugin/plugin.json
    """

    name = "cowork"
    supports_agents = True

    def get_paths(self, *, global_: bool, cwd: Path | None = None) -> ProviderPaths:  # noqa: ARG002
        plugin_dir = (cwd or Path.cwd()) / "cowork-plugin"
        return ProviderPaths(
            config_dir=plugin_dir,
            commands_dir=plugin_dir / "skills",
            agents_dir=plugin_dir / "agents",
        )

    def find_installed_skills(self, *, global_: bool, cwd: Path | None = None) -> list[str]:
        skills_dir = self.get_paths(global_=global_, cwd=cwd).commands_dir
        if not skills_dir.exists():
            return []

        all_cowork = {s.removesuffix(".md") for s in COWORK_SKILLS + COWORK_ONLY_SKILLS}
        installed = []
        for skill_file in skills_dir.glob("*/SKILL.md"):
            skill_name = skill_file.parent.name
            if skill_name in all_cowork:
                installed.append(skill_name)
        return sorted(installed)

    def is_cli_available(self) -> bool:
        return True

    def resolve_skill_target(self, commands_dir: Path, skill_filename: str) -> Path:
        skill_name = skill_filename.removesuffix(".md")
        return commands_dir / skill_name / "SKILL.md"

    def resolve_agent_target(self, agents_dir: Path, agent_filename: str) -> Path:
        agent_name = agent_filename.removesuffix(".md")
        return agents_dir / agent_name / "AGENT.md"

    def iter_managed_skill_targets(self, commands_dir: Path) -> list[Path]:
        if not commands_dir.exists():
            return []
        return sorted(commands_dir.glob("*/SKILL.md"))

    def iter_managed_agent_targets(self, agents_dir: Path) -> list[Path]:
        if not agents_dir.exists():
            return []
        return sorted(agents_dir.glob("*/AGENT.md"))

    def render_skill_content(self, skill_filename: str, source_content: str) -> str:
        """Render skill with Cowork-compatible frontmatter."""
        skill_name = skill_filename.removesuffix(".md")
        meta, body = split_frontmatter(source_content)

        if "description" not in meta or not str(meta["description"]).strip():
            _, desc = skill_info.get(skill_filename, ("", "Sp3cMar skill"))
            meta["description"] = desc

        description = " ".join(str(meta["description"]).split())
        frontmatter = f"name: {skill_name}\ndescription: {description}"
        return f"---\n{frontmatter}\n---\n\n{body.lstrip()}"

    def render_agent_content(self, agent_filename: str, source_content: str) -> str:
        """Render agent as AGENT.md with frontmatter."""
        from sp3cmar.constants import agent_info

        agent_name = agent_filename.removesuffix(".md")
        meta, body = split_frontmatter(source_content)

        if "description" not in meta or not str(meta["description"]).strip():
            _, desc = agent_info.get(agent_filename, ("", "Sp3cMar agent"))
            meta["description"] = desc

        description = " ".join(str(meta["description"]).split())
        frontmatter = f"name: {agent_name}\ndescription: {description}"
        return f"---\n{frontmatter}\n---\n\n{body.lstrip()}"

    def sync_agent_registry(self, config_dir: Path) -> None:  # noqa: ARG002
        """No-op: Cowork discovers agents from the filesystem."""

    def clear_agent_registry(self, config_dir: Path) -> None:  # noqa: ARG002
        """No-op: Cowork discovers agents from the filesystem."""


def write_plugin_manifest(plugin_dir: Path, version: str) -> None:
    """Write .claude-plugin/plugin.json manifest."""
    from sp3cmar.utils.files import safe_mkdir

    meta_dir = plugin_dir / ".claude-plugin"
    safe_mkdir(meta_dir, parents=True, exist_ok=True)

    manifest = {
        "name": PLUGIN_NAME,
        "version": version,
        "description": "Workflow skills and reviewer agents for Claude Cowork",
        "author": "b3dmar",
    }

    safe_write_text(meta_dir / "plugin.json", json.dumps(manifest, indent=2) + "\n")
