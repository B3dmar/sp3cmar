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

        assert "ship" in result.output
        assert "review" in result.output
        assert "seo-geo" in result.output
        assert "project-constitute" not in result.output
        # Retired skills must not appear (April 2026 audit)
        assert "/sp3cmar-feature" not in result.output
        assert "/sp3cmar-docs" not in result.output
        assert "/sp3cmar-breakdown" not in result.output
        assert "/sp3cmar-implement" not in result.output
        assert "/sp3cmar-ux-audit" not in result.output

    def test_skills_list_complete(self):
        """SKILLS list has expected count."""
        from sp3cmar.constants import SKILLS

        expected_skills = [
            # Workflow
            "ship.md",
            "done.md",
            "post-merge.md",
            "worktree.md",
            "doc-audit.md",
            "milestone-audit.md",
            "workflow-audit.md",
            "memory-audit.md",
            "staging-audit.md",
            "issue.md",
            # Spec & review
            "review.md",
            # Ship
            "release-notes.md",
            # Growth
            "seo-geo.md",
        ]

        for skill in expected_skills:
            assert skill in SKILLS, f"Missing skill: {skill}"

        # Retired in April 2026 audit
        retired_skills = [
            "feature.md",
            "docs.md",
            "breakdown.md",
            "implement.md",
            "ux-audit.md",
        ]
        for skill in retired_skills:
            assert skill not in SKILLS, f"Retired skill still present: {skill}"

        assert len(SKILLS) == 13

    def test_skill_info_complete(self):
        """All skills in SKILLS have entries in skill_info."""
        from sp3cmar.constants import SKILLS, skill_info

        for skill in SKILLS:
            assert skill in skill_info, f"Missing skill_info: {skill}"
            cmd, desc = skill_info[skill]
            assert cmd.startswith("/sp3cmar-"), f"Bad command format: {cmd}"
            assert len(desc) > 10, f"Description too short: {desc}"
