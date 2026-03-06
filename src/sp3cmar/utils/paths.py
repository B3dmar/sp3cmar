"""Path resolution utilities for Sp3cMar."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from sp3cmar.exceptions import PathTraversalError

logger = logging.getLogger(__name__)

# Backward-compatible re-export
__all__ = [
    "PathTraversalError",
    "construct_safe_output_path",
    "get_package_root",
    "get_template_path",
    "sanitize_slug",
]


def sanitize_slug(slug: str) -> str:
    """Validate a slug contains no path traversal characters.

    Args:
        slug: The slug to validate

    Returns:
        The slug if valid

    Raises:
        PathTraversalError: If slug contains path traversal characters
    """
    # Check for path traversal patterns
    if ".." in slug or "/" in slug or "\\" in slug:
        logger.warning("Path traversal detected in slug: %s", slug)
        raise PathTraversalError(f"Path traversal detected in slug: {slug}")

    # Also check for URL-encoded variants
    if re.search(r"%2[eEfF]", slug):  # %2e = ., %2f = /
        logger.warning("URL-encoded path traversal detected in slug: %s", slug)
        raise PathTraversalError(f"Path traversal detected in slug: {slug}")

    return slug


def construct_safe_output_path(target_dir: Path, filename: str) -> Path:
    """Construct a safe output path within target directory.

    Args:
        target_dir: The target directory (must exist)
        filename: The filename to add

    Returns:
        The full path, verified to be within target_dir

    Raises:
        PathTraversalError: If the resulting path escapes target_dir
    """
    # First sanitize the filename
    sanitize_slug(filename)

    # Construct and resolve the path
    output_path = (target_dir / filename).resolve()
    target_resolved = target_dir.resolve()

    # Verify the path is within the target directory
    try:
        output_path.relative_to(target_resolved)
    except ValueError as err:
        logger.warning("Path %s escapes target directory %s", output_path, target_resolved)
        raise PathTraversalError(
            f"Output path {output_path} escapes target directory {target_resolved}"
        ) from err

    return output_path


def get_package_root() -> Path:
    """Get the root directory of the sp3cmar package."""
    return Path(__file__).parent.parent


def get_template_path(template_name: str) -> Path:
    """Get path to a template directory.

    Args:
        template_name: Name of template (skills, agents)

    Returns:
        Path to the template directory
    """
    return get_package_root() / "templates" / template_name
