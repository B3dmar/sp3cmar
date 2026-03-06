"""Codex provider adapter."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from sp3cmar.constants import AGENTS, SKILLS, agent_info, skill_info
from sp3cmar.providers.base import ProviderPaths
from sp3cmar.utils.files import safe_read_text, safe_unlink, safe_write_text
from sp3cmar.utils.frontmatter import split_frontmatter

logger = logging.getLogger(__name__)

MANAGED_BEGIN = "# BEGIN SP3CMAR AGENTS"
MANAGED_END = "# END SP3CMAR AGENTS"


class CodexProvider:
    """Codex provider implementation.

    Codex skills are directory-based:
      <config>/skills/<skill-name>/SKILL.md
    """

    name = "codex"
    supports_agents = True

    def get_paths(self, *, global_: bool, cwd: Path | None = None) -> ProviderPaths:
        config_dir = Path.home() / ".codex" if global_ else (cwd or Path.cwd()) / ".codex"
        return ProviderPaths(
            config_dir=config_dir,
            commands_dir=config_dir / "skills",
            agents_dir=config_dir / "agents",
        )

    def find_installed_skills(self, *, global_: bool, cwd: Path | None = None) -> list[str]:
        skills_dir = self.get_paths(global_=global_, cwd=cwd).commands_dir
        if not skills_dir.exists():
            return []

        sp3cmar_skills = {s.removesuffix(".md") for s in SKILLS}
        installed = []
        for skill_file in skills_dir.glob("sp3cmar-*/SKILL.md"):
            skill_name = skill_file.parent.name.removeprefix("sp3cmar-")
            if skill_name in sp3cmar_skills:
                installed.append(skill_name)
        return sorted(installed)

    def is_cli_available(self) -> bool:
        import shutil

        return shutil.which("codex") is not None

    def resolve_skill_target(self, commands_dir: Path, skill_filename: str) -> Path:
        skill_name = skill_filename.removesuffix(".md")
        return commands_dir / f"sp3cmar-{skill_name}" / "SKILL.md"

    def resolve_agent_target(self, agents_dir: Path, agent_filename: str) -> Path | None:
        agent_name = agent_filename.removesuffix(".md")
        return agents_dir / f"sp3cmar-{agent_name}.toml"

    def iter_managed_skill_targets(self, commands_dir: Path) -> list[Path]:
        if not commands_dir.exists():
            return []
        return sorted(commands_dir.glob("sp3cmar-*/SKILL.md"))

    def iter_managed_agent_targets(self, agents_dir: Path) -> list[Path]:
        if not agents_dir.exists():
            return []
        return sorted(agents_dir.glob("sp3cmar-*.toml"))

    def render_skill_content(self, skill_filename: str, source_content: str) -> str:
        """Ensure Codex-required frontmatter fields are present."""
        skill_name = skill_filename.removesuffix(".md")
        meta, body = split_frontmatter(source_content)

        if "description" not in meta or not str(meta["description"]).strip():
            # Fall back to constants mapping if template doesn't provide description.
            _, desc = skill_info.get(skill_filename, ("", "Sp3cMar skill"))
            meta["description"] = desc
        name = f"sp3cmar-{skill_name}"
        description = _normalize_description(str(meta["description"]))
        frontmatter = f"name: {name}\ndescription: {description}"
        return f"---\n{frontmatter}\n---\n\n{body.lstrip()}"

    def render_agent_content(self, agent_filename: str, source_content: str) -> str:
        meta, body = split_frontmatter(source_content)

        if "description" not in meta or not str(meta["description"]).strip():
            _, desc = agent_info.get(
                agent_filename, skill_info.get(agent_filename, ("", "Sp3cMar agent"))
            )
            meta["description"] = desc

        description = _normalize_description(str(meta["description"]))
        instructions = _escape_multiline_toml(body.strip())
        return (
            f'description = "{_escape_toml_string(description)}"\n'
            f'developer_instructions = """\n{instructions}\n"""\n'
        )

    def sync_agent_registry(self, config_dir: Path) -> None:
        """Register Sp3cMar agents in ~/.codex/config.toml."""
        from sp3cmar.utils.files import safe_mkdir

        config_file = config_dir / "config.toml"
        current = (
            safe_read_text(config_file)
            if config_file.exists() and not config_file.is_symlink()
            else ""
        )

        lines = [MANAGED_BEGIN]
        for agent in AGENTS:
            role = f"sp3cmar-{agent.removesuffix('.md')}"
            _, desc = agent_info.get(agent, skill_info.get(agent, ("", "Sp3cMar agent")))
            lines.extend(
                [
                    f"[agents.{role}]",
                    f'description = "{_escape_toml_string(desc)}"',
                    f'config_file = "agents/{role}.toml"',
                    "",
                ]
            )
        lines.append(MANAGED_END)
        block = "\n".join(lines)

        updated = _replace_managed_block(current, block)
        safe_mkdir(config_dir, parents=True, exist_ok=True)
        safe_write_text(config_file, updated)

    def clear_agent_registry(self, config_dir: Path) -> None:
        """Remove Sp3cMar-managed role registrations from ~/.codex/config.toml."""
        config_file = config_dir / "config.toml"
        if not config_file.exists() or config_file.is_symlink():
            return
        cleaned = _strip_managed_block(safe_read_text(config_file)).strip()
        if cleaned:
            safe_write_text(config_file, cleaned + "\n")
        else:
            safe_unlink(config_file)


def _normalize_description(description: str) -> str:
    """Collapse multiline descriptions for stable frontmatter rendering."""
    return " ".join(description.split())


def _escape_toml_string(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
    )


def _escape_multiline_toml(value: str) -> str:
    return value.replace('"""', '\\"""')


def _replace_managed_block(current: str, block: str) -> str:
    if MANAGED_BEGIN in current and MANAGED_END in current:
        pattern = re.compile(
            rf"{re.escape(MANAGED_BEGIN)}.*?{re.escape(MANAGED_END)}",
            re.DOTALL,
        )
        replaced = pattern.sub(block, current, count=1).strip()
        return replaced + "\n"

    base = current.strip()
    if not base:
        return block + "\n"
    return base + "\n\n" + block + "\n"


def _strip_managed_block(current: str) -> str:
    if MANAGED_BEGIN in current and MANAGED_END in current:
        pattern = re.compile(
            rf"\n?{re.escape(MANAGED_BEGIN)}.*?{re.escape(MANAGED_END)}\n?",
            re.DOTALL,
        )
        return pattern.sub("\n", current, count=1)
    return current
