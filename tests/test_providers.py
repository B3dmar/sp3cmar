"""Tests for provider registry and Claude provider adapter."""

from pathlib import Path

import pytest

from sp3cmar.providers import get_provider


def test_get_provider_claude() -> None:
    provider = get_provider("claude")
    assert provider.name == "claude"


def test_get_provider_unknown_raises() -> None:
    with pytest.raises(ValueError, match="Unsupported provider"):
        get_provider("nope")


def test_get_provider_codex() -> None:
    provider = get_provider("codex")
    assert provider.name == "codex"
    assert provider.supports_agents is True


def test_claude_provider_local_paths(tmp_path: Path) -> None:
    provider = get_provider("claude")
    paths = provider.get_paths(global_=False, cwd=tmp_path)

    assert paths.config_dir == tmp_path / ".claude"
    assert paths.commands_dir == tmp_path / ".claude" / "commands"
    assert paths.agents_dir == tmp_path / ".claude" / "agents"
