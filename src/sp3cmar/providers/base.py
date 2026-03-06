"""Provider interface for AI-assistant specific integration points."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class ProviderPaths:
    """Resolved provider-specific target paths."""

    config_dir: Path
    commands_dir: Path
    agents_dir: Path


class Provider(Protocol):
    """Interface each AI provider adapter must implement."""

    name: str
    supports_agents: bool

    def get_paths(self, *, global_: bool, cwd: Path | None = None) -> ProviderPaths:
        """Return provider-specific config/commands/agents paths."""

    def find_installed_skills(self, *, global_: bool, cwd: Path | None = None) -> list[str]:
        """Return installed Sp3cMar skills (without extension)."""

    def is_cli_available(self) -> bool:
        """Whether the provider CLI is available in PATH."""

    def resolve_skill_target(self, commands_dir: Path, skill_filename: str) -> Path:
        """Return target path for a packaged skill template filename."""

    def resolve_agent_target(self, agents_dir: Path, agent_filename: str) -> Path | None:
        """Return target path for a packaged agent template filename, or None if unsupported."""

    def iter_managed_skill_targets(self, commands_dir: Path) -> list[Path]:
        """Enumerate installed provider-managed Sp3cMar skill target files."""

    def iter_managed_agent_targets(self, agents_dir: Path) -> list[Path]:
        """Enumerate installed provider-managed Sp3cMar agent target files."""

    def render_skill_content(self, skill_filename: str, source_content: str) -> str:
        """Return provider-ready SKILL.md content."""

    def render_agent_content(self, agent_filename: str, source_content: str) -> str:
        """Return provider-ready agent content."""

    def sync_agent_registry(self, config_dir: Path) -> None:
        """Register Sp3cMar agents in provider config. No-op if not applicable."""

    def clear_agent_registry(self, config_dir: Path) -> None:
        """Remove Sp3cMar agent registrations from provider config. No-op if not applicable."""
