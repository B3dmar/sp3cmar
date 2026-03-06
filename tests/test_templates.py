"""Tests for template-constant alignment."""

from sp3cmar.constants import AGENTS, COWORK_AGENTS, COWORK_ONLY_SKILLS, COWORK_SKILLS, SKILLS
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
        expected = set(SKILLS) | set(COWORK_ONLY_SKILLS)
        orphans = skill_files - expected
        assert not orphans, f"Orphan skill templates: {orphans}"

    def test_no_orphan_agent_templates(self):
        agents_dir = get_template_path("agents")
        agent_files = {f.name for f in agents_dir.glob("*.md")}
        expected = set(AGENTS)
        orphans = agent_files - expected
        assert not orphans, f"Orphan agent templates: {orphans}"


class TestCoworkAlignment:
    """Verify Cowork constants are subsets of core constants."""

    def test_cowork_skills_subset_of_skills(self):
        for skill in COWORK_SKILLS:
            assert skill in SKILLS, f"COWORK_SKILLS entry not in SKILLS: {skill}"

    def test_cowork_agents_subset_of_agents(self):
        for agent in COWORK_AGENTS:
            assert agent in AGENTS, f"COWORK_AGENTS entry not in AGENTS: {agent}"

    def test_cowork_only_skills_not_in_skills(self):
        for skill in COWORK_ONLY_SKILLS:
            assert skill not in SKILLS, f"COWORK_ONLY_SKILLS entry should not be in SKILLS: {skill}"

    def test_cowork_only_skills_have_templates(self):
        skills_dir = get_template_path("skills")
        for skill in COWORK_ONLY_SKILLS:
            assert (skills_dir / skill).exists(), f"Missing COWORK_ONLY template: {skill}"
