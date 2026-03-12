"""Backward-compatible constants derived from the canonical catalog."""

from sp3cmar.catalog import (
    AGENT_SPECS,
    CORE_SKILL_SPECS,
    COWORK_ONLY_SKILL_SPECS,
    ENGRAM_EXTENSION_SPECS,
)

SKILL_PREFIX = "sp3cmar-"

SKILLS = [spec.filename for spec in CORE_SKILL_SPECS]
AGENTS = [spec.filename for spec in AGENT_SPECS]

skill_info: dict[str, tuple[str, str]] = {
    spec.filename: (spec.command, spec.description)
    for spec in CORE_SKILL_SPECS + COWORK_ONLY_SKILL_SPECS
}

SKILL_CATEGORIES: dict[str, list[str]] = {}
for spec in CORE_SKILL_SPECS:
    SKILL_CATEGORIES.setdefault(spec.category, []).append(spec.filename)

COWORK_SKILLS: list[str] = []
COWORK_AGENTS: list[str] = []
COWORK_ONLY_SKILLS = [spec.filename for spec in COWORK_ONLY_SKILL_SPECS]
ENGRAM_SKILLS = [spec.filename for spec in ENGRAM_EXTENSION_SPECS]

agent_info: dict[str, tuple[str, str]] = {
    spec.filename: (spec.name, spec.description) for spec in AGENT_SPECS
}
