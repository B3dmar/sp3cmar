"""Tests for Sp3cMar CLI."""

from click.testing import CliRunner

from sp3cmar.cli import main


def test_help_lists_core_commands() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "install" in result.output
    assert "uninstall" in result.output
    assert "docs" in result.output
    assert "catalog" in result.output
