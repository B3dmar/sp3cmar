"""Tests for sp3cmar install command."""

import pytest
from click.testing import CliRunner


@pytest.fixture
def runner():
    """Create a CLI runner."""
    return CliRunner()


class TestInstallSkills:
    """Test install command includes expected skills."""

    def test_install_list_shows_skills(self, runner):
        """Install --list shows available skills."""
        from sp3cmar.cli import main

        result = runner.invoke(main, ["install", "--list"])
        assert result.exit_code == 0

        assert "docs" in result.output
        assert "feature" in result.output
        assert "review" in result.output
        assert "seo-geo" in result.output
        assert "project-constitute" not in result.output

    def test_skills_list_complete(self):
        """SKILLS list has expected count."""
        from sp3cmar.constants import SKILLS

        expected_skills = [
            # Workflow
            "ship.md",
            "done.md",
            "morning.md",
            "post-merge.md",
            "worktree.md",
            "doc-audit.md",
            "workflow-audit.md",
            "staging-audit.md",
            "fix.md",
            "migrate.md",
            # Spec & review
            "feature.md",
            "review.md",
            "docs.md",
            # Plan & build
            "breakdown.md",
            "implement.md",
            # Ship
            "release-notes.md",
            # Ops
            "incident.md",
            # Growth
            "seo-geo.md",
            "ux-audit.md",
        ]

        for skill in expected_skills:
            assert skill in SKILLS, f"Missing skill: {skill}"

        assert len(SKILLS) == 19

    def test_skill_info_complete(self):
        """All skills in SKILLS have entries in skill_info."""
        from sp3cmar.constants import SKILLS, skill_info

        for skill in SKILLS:
            assert skill in skill_info, f"Missing skill_info: {skill}"
            cmd, desc = skill_info[skill]
            assert cmd.startswith("/sp3cmar-"), f"Bad command format: {cmd}"
            assert len(desc) > 10, f"Description too short: {desc}"
