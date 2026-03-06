"""Claude provider adapter."""

from __future__ import annotations

import logging
from pathlib import Path

import yaml  # type: ignore[import-untyped]

from sp3cmar.constants import SKILLS, agent_info, skill_info
from sp3cmar.providers.base import ProviderPaths
from sp3cmar.utils.frontmatter import split_frontmatter

logger = logging.getLogger(__name__)


class ClaudeProvider:
    """Claude Code provider implementation."""

    name = "claude"
    supports_agents = True

    def get_paths(self, *, global_: bool, cwd: Path | None = None) -> ProviderPaths:
        config_dir = Path.home() / ".claude" if global_ else (cwd or Path.cwd()) / ".claude"

        return ProviderPaths(
            config_dir=config_dir,
            commands_dir=config_dir / "commands",
            agents_dir=config_dir / "agents",
        )

    def find_installed_skills(self, *, global_: bool, cwd: Path | None = None) -> list[str]:
        commands_dir = self.get_paths(global_=global_, cwd=cwd).commands_dir
        if not commands_dir.exists():
            return []

        sp3cmar_skills = {s.removesuffix(".md") for s in SKILLS}

        installed = []
        for skill_file in commands_dir.glob("sp3cmar-*.md"):
            skill_name = skill_file.stem.removeprefix("sp3cmar-")
            if skill_name in sp3cmar_skills:
                installed.append(skill_name)

        return sorted(installed)

    def is_cli_available(self) -> bool:
        import shutil

        return shutil.which("claude") is not None

    def resolve_skill_target(self, commands_dir: Path, skill_filename: str) -> Path:
        return commands_dir / f"sp3cmar-{skill_filename}"

    def resolve_agent_target(self, agents_dir: Path, agent_filename: str) -> Path:
        return agents_dir / f"sp3cmar-{agent_filename}"

    def iter_managed_skill_targets(self, commands_dir: Path) -> list[Path]:
        if not commands_dir.exists():
            return []
        return sorted(commands_dir.glob("sp3cmar-*.md"))

    def iter_managed_agent_targets(self, agents_dir: Path) -> list[Path]:
        if not agents_dir.exists():
            return []
        return sorted(agents_dir.glob("sp3cmar-*.md"))

    def render_skill_content(self, _skill_filename: str, source_content: str) -> str:
        return source_content

    def render_agent_content(self, agent_filename: str, source_content: str) -> str:
        agent_name = agent_filename.removesuffix(".md")
        meta, body = split_frontmatter(source_content)

        if "name" not in meta or not str(meta["name"]).strip():
            meta["name"] = f"sp3cmar-{agent_name}"
        if "description" not in meta or not str(meta["description"]).strip():
            _, desc = agent_info.get(
                agent_filename, skill_info.get(agent_filename, ("", "Sp3cMar agent"))
            )
            meta["description"] = desc

        meta["name"] = str(meta["name"]).strip()
        meta["description"] = " ".join(str(meta["description"]).split())
        frontmatter = yaml.safe_dump(meta, sort_keys=False).strip()
        return f"---\n{frontmatter}\n---\n\n{body.lstrip()}"

    def sync_agent_registry(self, config_dir: Path) -> None:  # noqa: ARG002
        """No-op: Claude Code discovers agents from the filesystem."""

    def clear_agent_registry(self, config_dir: Path) -> None:  # noqa: ARG002
        """No-op: Claude Code discovers agents from the filesystem."""
