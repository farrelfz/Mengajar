"""
Knowledge Provider Registry.
"""

from __future__ import annotations

from app.grounding.providers.base import KnowledgeProvider


class KnowledgeProviderRegistry:
    """Central registry of active knowledge retrieval providers."""

    _PROVIDERS: dict[str, KnowledgeProvider] = {}

    @classmethod
    def register(cls, provider: KnowledgeProvider) -> None:
        cls._PROVIDERS[provider.provider_id] = provider

    @classmethod
    def get(cls, provider_id: str) -> KnowledgeProvider | None:
        return cls._PROVIDERS.get(provider_id)

    @classmethod
    def list_all(cls) -> list[KnowledgeProvider]:
        return list(cls._PROVIDERS.values())

    @classmethod
    def clear(cls) -> None:
        cls._PROVIDERS.clear()
