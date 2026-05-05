"""Security regression tests for install command symlink handling."""

import os

from click.testing import CliRunner


def test_install_rejects_symlinked_skill_target(tmp_path, monkeypatch):
    """Install should fail if an existing skill target is a symlink."""
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)

    commands_dir = tmp_path / ".claude" / "commands"
    commands_dir.mkdir(parents=True)

    evil_target = tmp_path / "evil.txt"
    evil_target.write_text("evil")
    symlink = commands_dir / "sp3cmar-ship.md"
    os.symlink(evil_target, symlink)

    from sp3cmar.cli import main

    runner = CliRunner()
    result = runner.invoke(main, ["install", "--ai", "claude"])

    assert result.exit_code != 0
    assert "Refusing to overwrite symlink" in result.output
