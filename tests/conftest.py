"""Shared test fixtures for Sp3cMar."""

import sys

import pytest


@pytest.fixture(autouse=True)
def _clear_sp3cmar_modules():
    """Clear cached sp3cmar modules before each test.

    This prevents stale module state from leaking between tests,
    especially when tests monkeypatch Path.home or other globals.
    """
    modules_to_clear = [k for k in list(sys.modules.keys()) if k.startswith("sp3cmar")]
    for mod in modules_to_clear:
        del sys.modules[mod]
