"""
KIR AI Document Intelligence — Model Registry.

Provides a unified registry of all available AI clients.
"""

from __future__ import annotations

from app.ai.client import AIClient
from app.ai.ollama_client import OllamaClient
from app.ai.router import NineRouterClient


class ModelRegistry:
    """Registry holding initialized AI providers."""

    def __init__(self) -> None:
        self.providers: dict[str, AIClient] = {}

    def register(self, client: AIClient) -> None:
        """Register a provider client."""
        self.providers[client.provider_name] = client

    def get_provider(self, name: str) -> AIClient | None:
        """Get a registered provider by name."""
        return self.providers.get(name)

    @classmethod
    def setup_default(cls) -> ModelRegistry:
        """Initialize the default registry with 9Router and Ollama."""
        registry = cls()
        registry.register(NineRouterClient())
        registry.register(OllamaClient())
        return registry


# Global default registry instance
_registry: ModelRegistry | None = None

def get_registry() -> ModelRegistry:
    global _registry
    if _registry is None:
        _registry = ModelRegistry.setup_default()
    return _registry
