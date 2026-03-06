"""Tests for build-plugin command."""

import json
from pathlib import Path

from click.testing import CliRunner

from sp3cmar.constants import COWORK_AGENTS, COWORK_SKILLS


def test_build_plugin_creates_directory(tmp_path: Path) -> None:
    from sp3cmar.cli import main

    runner = CliRunner()
    output = tmp_path / "plugin-out"
    result = runner.invoke(main, ["build-plugin", "--output", str(output)])
    assert result.exit_code == 0

    assert (output / ".claude-plugin" / "plugin.json").exists()


def test_build_plugin_creates_skills(tmp_path: Path) -> None:
    from sp3cmar.cli import main

    runner = CliRunner()
    output = tmp_path / "plugin-out"
    result = runner.invoke(main, ["build-plugin", "--output", str(output)])
    assert result.exit_code == 0

    for skill in COWORK_SKILLS:
        skill_name = skill.removesuffix(".md")
        skill_path = output / "skills" / skill_name / "SKILL.md"
        assert skill_path.exists(), f"Missing skill: {skill_name}"


def test_build_plugin_creates_agents(tmp_path: Path) -> None:
    from sp3cmar.cli import main

    runner = CliRunner()
    output = tmp_path / "plugin-out"
    result = runner.invoke(main, ["build-plugin", "--output", str(output)])
    assert result.exit_code == 0

    for agent in COWORK_AGENTS:
        agent_name = agent.removesuffix(".md")
        agent_path = output / "agents" / agent_name / "AGENT.md"
        assert agent_path.exists(), f"Missing agent: {agent_name}"


def test_build_plugin_manifest_valid(tmp_path: Path) -> None:
    from sp3cmar.cli import main

    runner = CliRunner()
    output = tmp_path / "plugin-out"
    runner.invoke(main, ["build-plugin", "--output", str(output)])

    manifest = json.loads((output / ".claude-plugin" / "plugin.json").read_text())
    assert manifest["name"] == "sp3cmar"
    assert "version" in manifest


def test_cli_help_lists_build_plugin() -> None:
    from sp3cmar.cli import main

    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert "build-plugin" in result.output
