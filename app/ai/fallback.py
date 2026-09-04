"""
KIR AI Document Intelligence — AI Fallback Execution Chain.

Executes generation requests with automatic fallback routing.
If the primary provider fails (timeout, error), it routes to the secondary.
"""

from __future__ import annotations

from app.ai.client import GenerationRequest, GenerationResponse
from app.ai.model_registry import ModelRegistry, get_registry
from app.ai.model_selector import ModelSelector
from app.config.settings import AppSettings, get_settings
from app.core.exceptions import AIError, FallbackExhaustedError
from app.core.logging import get_logger

log = get_logger(__name__)


class FallbackChain:
    """Executes a GenerationRequest through the fallback hierarchy."""

    def __init__(
        self,
        selector: ModelSelector | None = None,
        registry: ModelRegistry | None = None,
        settings: AppSettings | None = None,
    ) -> None:
        self.selector = selector or ModelSelector()
        self.registry = registry or get_registry()
        self.settings = settings or get_settings()

    async def execute(self, request: GenerationRequest) -> GenerationResponse:
        """Execute request with fallback handling.

        Hierarchy:
        1. Primary provider (via ModelSelector)
        2. Ollama (if enabled in settings)
        """
        tried_providers: list[str] = []

        # 1. Primary execution
        primary_client = self.selector.select(request.required_capability, request.job_id)
        
        log.debug(
            "fallback_chain.attempt_primary",
            provider=primary_client.provider_name,
            job_id=request.job_id,
            step=request.step,
        )
        
        try:
            response = await primary_client.generate(request)
            return response
        except AIError as exc:
            tried_providers.append(primary_client.provider_name)
            log.warning(
                "fallback_chain.primary_failed",
                provider=primary_client.provider_name,
                error=str(exc),
                job_id=request.job_id,
                step=request.step,
            )

        # 2. Fallback to Ollama (if not already tried and if enabled)
        if self.settings.fallback_to_ollama and "ollama" not in tried_providers:
            ollama_client = self.registry.get_provider("ollama")
            if ollama_client and request.required_capability in ollama_client.supported_capabilities:
                log.info(
                    "fallback_chain.attempt_fallback",
                    provider="ollama",
                    job_id=request.job_id,
                    step=request.step,
                )
                try:
                    response = await ollama_client.generate(request)
                    response.fallback_used = True
                    return response
                except AIError as exc:
                    tried_providers.append("ollama")
                    log.warning(
                        "fallback_chain.fallback_failed",
                        provider="ollama",
                        error=str(exc),
                        job_id=request.job_id,
                        step=request.step,
                    )

        # 3. Exhausted
        raise FallbackExhaustedError(
            "All providers in the fallback chain failed.",
            tried_providers=tried_providers,
            job_id=request.job_id,
            step=request.step,
        )
