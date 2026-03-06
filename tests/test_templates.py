"""Tests for template-constant alignment."""

from sp3cmar.constants import AGENTS, SKILLS
from sp3cmar.utils.paths import get_template_path


class TestTemplateAlignment:
    """Verify every constant has a template and no orphans exist."""

    def test_every_skill_has_template(self):
        skills_dir = get_template_path("skills")
        for skill in SKILLS:
            assert (skills_dir / skill).exists(), f"Missing skill template: {skill}"

    def test_every_agent_has_template(self):
        agents_dir = get_template_path("agents")
        skills_dir = get_template_path("skills")
        for agent in AGENTS:
            agent_path = agents_dir / agent
            skill_fallback = skills_dir / agent
            assert agent_path.exists() or skill_fallback.exists(), (
                f"Missing agent template (checked agents/ and skills/): {agent}"
            )

    def test_no_orphan_skill_templates(self):
        skills_dir = get_template_path("skills")
        skill_files = {f.name for f in skills_dir.glob("*.md")}
        expected = set(SKILLS)
        orphans = skill_files - expected
        assert not orphans, f"Orphan skill templates: {orphans}"

    def test_no_orphan_agent_templates(self):
        agents_dir = get_template_path("agents")
        agent_files = {f.name for f in agents_dir.glob("*.md")}
        expected = set(AGENTS)
        orphans = agent_files - expected
        assert not orphans, f"Orphan agent templates: {orphans}"
