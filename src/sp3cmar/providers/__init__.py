"""Provider registry for assistant-specific integrations."""

from sp3cmar.providers.base import Provider
from sp3cmar.providers.claude import ClaudeProvider
from sp3cmar.providers.codex import CodexProvider
from sp3cmar.providers.cowork import CoworkProvider

_PROVIDERS: dict[str, Provider] = {
    "claude": ClaudeProvider(),
    "codex": CodexProvider(),
    "cowork": CoworkProvider(),
}


def supported_providers() -> tuple[str, ...]:
    """Return currently registered provider names."""
    return tuple(sorted(_PROVIDERS))


def get_provider(name: str = "claude") -> Provider:
    """Resolve provider by name."""
    try:
        return _PROVIDERS[name]
    except KeyError as exc:
        supported = ", ".join(sorted(_PROVIDERS))
        raise ValueError(
            f"Unsupported provider '{name}'. Supported providers: {supported}"
        ) from exc


__all__ = ["get_provider", "supported_providers"]
