"""Tests for Cowork provider adapter."""

import json
from pathlib import Path

from sp3cmar.providers import get_provider
from sp3cmar.providers.cowork import write_plugin_manifest


def test_get_provider_cowork() -> None:
    provider = get_provider("cowork")
    assert provider.name == "cowork"
    assert provider.supports_agents is True


def test_cowork_paths(tmp_path: Path) -> None:
    provider = get_provider("cowork")
    paths = provider.get_paths(global_=False, cwd=tmp_path)

    assert paths.config_dir == tmp_path / "cowork-plugin"
    assert paths.commands_dir == tmp_path / "cowork-plugin" / "skills"
    assert paths.agents_dir == tmp_path / "cowork-plugin" / "agents"


def test_cowork_resolve_skill_target(tmp_path: Path) -> None:
    provider = get_provider("cowork")
    target = provider.resolve_skill_target(tmp_path / "skills", "review-codebase.md")
    assert target == tmp_path / "skills" / "review-codebase" / "SKILL.md"


def test_cowork_resolve_agent_target(tmp_path: Path) -> None:
    provider = get_provider("cowork")
    target = provider.resolve_agent_target(tmp_path / "agents", "reviewer-correctness.md")
    assert target == tmp_path / "agents" / "reviewer-correctness" / "AGENT.md"


def test_cowork_render_skill_content() -> None:
    provider = get_provider("cowork")
    source = "---\ndescription: Test skill\n---\n\n# Instructions\nDo stuff."
    result = provider.render_skill_content("review-codebase.md", source)

    assert "name: review-codebase" in result
    assert "description: Test skill" in result
    assert "# Instructions" in result


def test_cowork_render_skill_content_fallback_description() -> None:
    provider = get_provider("cowork")
    source = "# Instructions\nDo stuff."
    result = provider.render_skill_content("review-codebase.md", source)

    assert "name: review-codebase" in result
    assert "description:" in result
    assert len(result.split("description: ")[1].split("\n")[0]) > 5


def test_cowork_render_agent_content() -> None:
    provider = get_provider("cowork")
    source = "---\ndescription: Test agent\n---\n\n# Agent\nReview stuff."
    result = provider.render_agent_content("reviewer-correctness.md", source)

    assert "name: reviewer-correctness" in result
    assert "description: Test agent" in result
    assert "# Agent" in result


def test_write_plugin_manifest(tmp_path: Path) -> None:
    write_plugin_manifest(tmp_path, "1.0.0")

    manifest_path = tmp_path / ".claude-plugin" / "plugin.json"
    assert manifest_path.exists()

    data = json.loads(manifest_path.read_text())
    assert data["name"] == "sp3cmar"
    assert data["version"] == "1.0.0"
    assert "author" in data
