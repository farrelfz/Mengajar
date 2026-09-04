"""
KIR AI Document Intelligence — Model Selector.

Resolves a requested capability to the optimal available AIClient
based on application configuration (primary provider, offline mode).
"""

from __future__ import annotations

from app.ai.client import AICapability, AIClient
from app.ai.model_registry import ModelRegistry, get_registry
from app.config.settings import AppSettings, get_settings
from app.core.exceptions import ModelUnavailableError
from app.core.logging import get_logger

log = get_logger(__name__)


class ModelSelector:
    """Selects the appropriate provider for a given capability."""

    def __init__(
        self,
        registry: ModelRegistry | None = None,
        settings: AppSettings | None = None,
    ) -> None:
        self.registry = registry or get_registry()
        self.settings = settings or get_settings()

    def select(self, capability: AICapability, job_id: str | None = None) -> AIClient:
        """Select the primary client for a capability.

        Returns
        -------
        AIClient
            The client that should handle the request.

        Raises
        ------
        ModelUnavailableError
            If no configured provider can handle the capability.
        """
        # If offline_mode is True, force Ollama
        if self.settings.offline_mode or capability == AICapability.LOCAL_OFFLINE:
            provider = self._get_provider("ollama", capability, job_id)
            if provider:
                return provider
            raise ModelUnavailableError(
                "Offline mode requires Ollama, but it is not available or does not support capability",
                capability=capability.value,
                job_id=job_id,
            )

        # Primary configured provider
        primary_name = self.settings.primary_provider
        if primary_name == "auto":
            primary_name = "9router"

        provider = self._get_provider(primary_name, capability, job_id)
        if provider:
            return provider

        # Fallback to Ollama if primary doesn't support the capability
        if self.settings.fallback_to_ollama:
            log.info(
                "model_selector.primary_unsupported",
                capability=capability.value,
                primary=primary_name,
                job_id=job_id,
                action="fallback_to_ollama",
            )
            provider = self._get_provider("ollama", capability, job_id)
            if provider:
                return provider

        raise ModelUnavailableError(
            f"No provider available for capability: {capability.value}",
            capability=capability.value,
            job_id=job_id,
        )

    def _get_provider(self, name: str, capability: AICapability, job_id: str | None) -> AIClient | None:
        client = self.registry.get_provider(name)
        if client and capability in client.supported_capabilities:
            return client
        return None
