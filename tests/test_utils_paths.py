"""Tests for sp3cmar.utils.paths module."""


class TestGetTemplatePath:
    """Test get_template_path function."""

    def test_get_template_path_returns_skills_dir(self):
        from sp3cmar.utils.paths import get_template_path

        skills_path = get_template_path("skills")
        assert skills_path.exists()
        assert skills_path.name == "skills"

    def test_get_template_path_returns_agents_dir(self):
        from sp3cmar.utils.paths import get_template_path

        agents_path = get_template_path("agents")
        assert agents_path.exists()
        assert agents_path.name == "agents"
