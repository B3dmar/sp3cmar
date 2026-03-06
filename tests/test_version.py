"""Tests for version consistency."""

import re
from pathlib import Path

import pytest
import tomllib
from click.testing import CliRunner

import sp3cmar
from sp3cmar.cli import main as cli


@pytest.fixture
def cli_runner():
    """Provide a Click CLI test runner."""
    return CliRunner()


def test_package_version_matches_pyproject():
    """
    Given: The sp3cmar package
    When: Comparing __version__ to pyproject.toml
    Then: They match exactly
    """
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        pyproject = tomllib.load(f)

    pyproject_version = pyproject["project"]["version"]

    assert sp3cmar.__version__ == pyproject_version, (
        f"Version mismatch: __init__.py has {sp3cmar.__version__!r}, "
        f"pyproject.toml has {pyproject_version!r}"
    )


def test_cli_version_matches_package(cli_runner):
    """
    Given: The sp3cmar CLI
    When: Running sp3cmar --version
    Then: Version matches package __version__
    """
    result = cli_runner.invoke(cli, ["--version"])

    assert sp3cmar.__version__ in result.output, (
        f"CLI version output {result.output!r} does not contain "
        f"package version {sp3cmar.__version__!r}"
    )


def test_version_is_valid_semver():
    """
    Given: The sp3cmar package version
    When: Parsing as semver
    Then: It parses without error
    """
    semver_pattern = r"^\d+\.\d+\.\d+(-[a-zA-Z0-9]+(\.[a-zA-Z0-9]+)*)?$"

    assert re.match(semver_pattern, sp3cmar.__version__), (
        f"Version {sp3cmar.__version__!r} is not valid semver"
    )
