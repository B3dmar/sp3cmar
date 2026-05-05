"""Tests for global-only sp3cmar uninstall command."""

import pytest
from click.testing import CliRunner


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def cli_main():
    from sp3cmar.cli import main

    return main


def test_uninstall_removes_global_artifacts(runner, cli_main, tmp_path, monkeypatch):
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)

    commands_dir = tmp_path / ".claude" / "commands"
    commands_dir.mkdir(parents=True)
    (commands_dir / "sp3cmar-ship.md").write_text("skill")

    agents_dir = tmp_path / ".claude" / "agents"
    agents_dir.mkdir(parents=True)
    (agents_dir / "sp3cmar-reviewer-correctness.md").write_text("agent")

    result = runner.invoke(cli_main, ["uninstall", "--yes", "--ai", "claude"])

    assert result.exit_code == 0
    assert not (commands_dir / "sp3cmar-ship.md").exists()
    assert not (agents_dir / "sp3cmar-reviewer-correctness.md").exists()


def test_uninstall_nothing_found(runner, cli_main, tmp_path, monkeypatch):
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)

    result = runner.invoke(cli_main, ["uninstall", "--ai", "claude"])

    assert result.exit_code == 0
    assert "no sp3cmar files found globally" in result.output.lower()


def test_uninstall_dry_run_no_changes(runner, cli_main, tmp_path, monkeypatch):
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)

    commands_dir = tmp_path / ".claude" / "commands"
    commands_dir.mkdir(parents=True)
    target = commands_dir / "sp3cmar-ship.md"
    target.write_text("skill")

    result = runner.invoke(cli_main, ["uninstall", "--dry-run", "--ai", "claude"])

    assert result.exit_code == 0
    assert "[DRY RUN]" in result.output
    assert target.exists()


def test_uninstall_confirmation_rejects(runner, cli_main, tmp_path, monkeypatch):
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)

    commands_dir = tmp_path / ".claude" / "commands"
    commands_dir.mkdir(parents=True)
    target = commands_dir / "sp3cmar-ship.md"
    target.write_text("skill")

    result = runner.invoke(cli_main, ["uninstall", "--ai", "claude"], input="n\n")

    assert result.exit_code == 0
    assert target.exists()
