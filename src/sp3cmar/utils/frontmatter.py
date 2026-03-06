"""Shared YAML frontmatter parsing for markdown templates."""

from __future__ import annotations

import re

import yaml  # type: ignore[import-untyped]


def split_frontmatter(content: str) -> tuple[dict[str, object], str]:
    """Parse optional YAML frontmatter from markdown content.

    Returns a tuple of (metadata_dict, body_text). If no frontmatter
    is present, returns an empty dict and the full content.
    """
    if content.startswith("---\n"):
        match = re.match(r"^---\n(.*?)\n---\n?(.*)$", content, re.DOTALL)
        if match:
            raw_meta = match.group(1)
            body = match.group(2)
            parsed = yaml.safe_load(raw_meta)
            if isinstance(parsed, dict):
                return parsed, body
            return {}, body
    return {}, content
