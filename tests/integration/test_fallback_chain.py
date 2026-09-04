"""Integration tests for FallbackChain execution and error handling."""

import pytest

from app.ai.client import AICapability, AIClient, GenerationRequest, GenerationResponse
from app.ai.fallback import FallbackChain
from app.ai.model_registry import ModelRegistry
from app.ai.model_selector import ModelSelector
from app.config.settings import AppSettings
from app.core.exceptions import FallbackExhaustedError, ProviderError


class FailingAIClient(AIClient):
    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def provider_name(self) -> str:
        return self._name

    @property
    def supported_capabilities(self) -> list[AICapability]:
        return [AICapability.SEMANTIC_REASONING]

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        raise ProviderError(f"{self._name} is down!", provider=self._name)


class WorkingAIClient(AIClient):
    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def provider_name(self) -> str:
        return self._name

    @property
    def supported_capabilities(self) -> list[AICapability]:
        return [AICapability.SEMANTIC_REASONING]

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        return GenerationResponse(
            content="success response",
            model_used="working-model",
            provider=self._name,
            capability_used=request.required_capability,
        )


@pytest.mark.asyncio
async def test_fallback_switches_from_primary_to_ollama_on_failure():
    """Verify that a failure in primary provider triggers failover to Ollama."""
    primary_fail = FailingAIClient("9router")
    ollama_work = WorkingAIClient("ollama")

    registry = ModelRegistry()
    registry.register(primary_fail)
    registry.register(ollama_work)

    settings = AppSettings(
        primary_provider="9router",
        fallback_to_ollama=True,
        offline_mode=False,
        nine_router_api_key="mock",
    )
    selector = ModelSelector(registry=registry, settings=settings)
    fallback_chain = FallbackChain(selector=selector, registry=registry, settings=settings)

    req = GenerationRequest(system_prompt="sys", user_prompt="usr", required_capability=AICapability.SEMANTIC_REASONING)
    res = await fallback_chain.execute(req)

    assert res.provider == "ollama"
    assert res.fallback_used is True
    assert res.content == "success response"


@pytest.mark.asyncio
async def test_fallback_exhausted_raises_error():
    """Verify FallbackExhaustedError is raised if all configured providers fail."""
    primary_fail = FailingAIClient("9router")
    ollama_fail = FailingAIClient("ollama")

    registry = ModelRegistry()
    registry.register(primary_fail)
    registry.register(ollama_fail)

    settings = AppSettings(
        primary_provider="9router",
        fallback_to_ollama=True,
        offline_mode=False,
        nine_router_api_key="mock",
    )
    selector = ModelSelector(registry=registry, settings=settings)
    fallback_chain = FallbackChain(selector=selector, registry=registry, settings=settings)

    req = GenerationRequest(system_prompt="sys", user_prompt="usr", required_capability=AICapability.SEMANTIC_REASONING)
    with pytest.raises(FallbackExhaustedError) as exc_info:
        await fallback_chain.execute(req)

    assert "9router" in exc_info.value.tried_providers
    assert "ollama" in exc_info.value.tried_providers
