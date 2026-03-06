"""Tests for sp3cmar docs command."""

from click.testing import CliRunner


class TestDocsCommand:
    """Test sp3cmar docs command."""

    def test_docs_no_argument_shows_overview(self):
        from sp3cmar.cli import main

        runner = CliRunner()
        result = runner.invoke(main, ["docs"])

        assert result.exit_code == 0
        assert "Sp3cMar Workflow" in result.output
        assert "/sp3cmar-docs" in result.output

    def test_docs_valid_skill_shows_content(self):
        from sp3cmar.cli import main

        runner = CliRunner()
        result = runner.invoke(main, ["docs", "docs"])

        assert result.exit_code == 0
        assert "documentation" in result.output.lower()

    def test_docs_invalid_skill_shows_error(self):
        from sp3cmar.cli import main

        runner = CliRunner()
        result = runner.invoke(main, ["docs", "nonexistent"])

        assert "Unknown skill" in result.output

    def test_docs_skill_with_slash_prefix(self):
        from sp3cmar.cli import main

        runner = CliRunner()
        result = runner.invoke(main, ["docs", "/docs"])

        assert result.exit_code == 0
        assert "Unknown skill" not in result.output
