"""Tests for the sp3cmar catalog."""

import json

from click.testing import CliRunner


def test_catalog_command_outputs_valid_json() -> None:
    from sp3cmar.cli import main

    runner = CliRunner()
    result = runner.invoke(main, ["catalog"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["name"] == "sp3cmar"
    assert any(skill["name"] == "seo-geo" for skill in payload["skills"])


def test_catalog_command_can_write_file(tmp_path) -> None:
    from sp3cmar.cli import main

    runner = CliRunner()
    output = tmp_path / "catalog.json"
    result = runner.invoke(main, ["catalog", "--output", str(output)])

    assert result.exit_code == 0
    payload = json.loads(output.read_text())
    assert any(agent["name"] == "reviewer-correctness" for agent in payload["agents"])
