"""Tests for Codex provider install/uninstall behavior."""

from click.testing import CliRunner


def test_install_codex_global_uses_home(tmp_path, monkeypatch):
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)

    from sp3cmar.cli import main

    runner = CliRunner()
    result = runner.invoke(main, ["install", "--ai", "codex"])

    assert result.exit_code == 0
    assert (tmp_path / ".codex" / "skills" / "sp3cmar-docs" / "SKILL.md").exists()
    assert (tmp_path / ".codex" / "skills" / "sp3cmar-feature" / "SKILL.md").exists()
    assert (tmp_path / ".codex" / "agents" / "sp3cmar-docs.toml").exists()
    assert (tmp_path / ".codex" / "agents" / "sp3cmar-review-pr.toml").exists()
    config_toml = (tmp_path / ".codex" / "config.toml").read_text()
    assert "# BEGIN SP3CMAR AGENTS" in config_toml
    assert "[agents.sp3cmar-docs]" in config_toml


def test_uninstall_codex_global_removes_skill_files(tmp_path, monkeypatch):
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)

    skills_dir = tmp_path / ".codex" / "skills"
    docs_dir = skills_dir / "sp3cmar-docs"
    docs_dir.mkdir(parents=True)
    (docs_dir / "SKILL.md").write_text("# Docs")
    agents_dir = tmp_path / ".codex" / "agents"
    agents_dir.mkdir(parents=True)
    (agents_dir / "sp3cmar-docs.toml").write_text('developer_instructions = """x"""')
    (tmp_path / ".codex" / "config.toml").write_text(
        '# BEGIN SP3CMAR AGENTS\n[agents.sp3cmar-docs]\ndescription = "Docs"\nconfig_file = "agents/sp3cmar-docs.toml"\n# END SP3CMAR AGENTS\n'
    )

    from sp3cmar.cli import main

    runner = CliRunner()
    result = runner.invoke(main, ["uninstall", "--yes", "--ai", "codex"])

    assert result.exit_code == 0
    assert not (docs_dir / "SKILL.md").exists()
    assert not (agents_dir / "sp3cmar-docs.toml").exists()
    config_path = tmp_path / ".codex" / "config.toml"
    assert not config_path.exists() or "# BEGIN SP3CMAR AGENTS" not in config_path.read_text()


def test_install_codex_writes_valid_frontmatter(tmp_path, monkeypatch):
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)

    from sp3cmar.cli import main

    runner = CliRunner()
    result = runner.invoke(main, ["install", "--ai", "codex"])
    assert result.exit_code == 0

    skill_file = tmp_path / ".codex" / "skills" / "sp3cmar-review-codebase" / "SKILL.md"
    content = skill_file.read_text()
    assert content.startswith("---\n")
    assert "name: sp3cmar-review-codebase" in content
    assert "description:" in content

    agent_file = tmp_path / ".codex" / "agents" / "sp3cmar-review-codebase.toml"
    agent_content = agent_file.read_text()
    assert 'description = "' in agent_content
    assert 'developer_instructions = """' in agent_content
