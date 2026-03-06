"""sp3cmar — workflow and review commands for Claude Code and Codex."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("sp3cmar")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"
