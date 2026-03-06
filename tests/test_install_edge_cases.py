"""Tests for sp3cmar install command edge cases."""

from click.testing import CliRunner


def test_install_no_flags_defaults_to_global(tmp_path, monkeypatch):
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)

    from sp3cmar.cli import main

    runner = CliRunner()
    result = runner.invoke(main, ["install"])

    assert result.exit_code == 0
    assert (tmp_path / ".claude" / "commands" / "sp3cmar-docs.md").exists()


def test_install_updates_changed_skill(tmp_path, monkeypatch):
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)

    commands_dir = tmp_path / ".claude" / "commands"
    commands_dir.mkdir(parents=True)
    target = commands_dir / "sp3cmar-docs.md"
    target.write_text("# stale")

    from sp3cmar.cli import main

    runner = CliRunner()
    result = runner.invoke(main, ["install", "--ai", "claude"])

    assert result.exit_code == 0
    assert "updated" in result.output
    assert target.read_text() != "# stale"


def test_install_skips_unchanged_skills(tmp_path, monkeypatch):
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)

    from sp3cmar.cli import main

    runner = CliRunner()
    first = runner.invoke(main, ["install", "--ai", "claude"])
    second = runner.invoke(main, ["install", "--ai", "claude"])

    assert first.exit_code == 0
    assert second.exit_code == 0
    assert "unchanged" in second.output
