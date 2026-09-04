"""Unit tests for SemanticClassifier contracts with mocked AI responses."""

import pytest

from app.ai.client import AICapability, AIClient, GenerationRequest, GenerationResponse
from app.ai.fallback import FallbackChain
from app.ai.model_registry import ModelRegistry
from app.ai.model_selector import ModelSelector
from app.config.settings import AppSettings
from app.intelligence.classifier import SemanticClassifier
from app.intelligence.output_validator import OutputValidator
from app.intelligence.schemas import ContentType, ContentUnit


class MockSemanticAI(AIClient):
    def __init__(self, response_json: str) -> None:
        self.response_json = response_json

    @property
    def provider_name(self) -> str:
        return "mock"

    @property
    def supported_capabilities(self) -> list[AICapability]:
        return [AICapability.SEMANTIC_REASONING, AICapability.STRUCTURED_OUTPUT]

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        return GenerationResponse(
            content=self.response_json,
            model_used="mock",
            provider="mock",
            capability_used=request.required_capability,
        )


def make_classifier(json_str: str) -> SemanticClassifier:
    mock_client = MockSemanticAI(json_str)
    registry = ModelRegistry()
    registry.register(mock_client)
    settings = AppSettings(
        primary_provider="mock",  # type: ignore
        fallback_to_ollama=False,
        offline_mode=False,
        nine_router_api_key="mock",
    )
    selector = ModelSelector(registry=registry, settings=settings)
    fallback_chain = FallbackChain(selector=selector, registry=registry, settings=settings)
    validator = OutputValidator(fallback_chain=fallback_chain, settings=settings)
    return SemanticClassifier(validator=validator)


@pytest.mark.asyncio
async def test_classifier_heading_bypass():
    """Verify structural TITLE units bypass LLM call and return immediately."""
    classifier = make_classifier('{"unit_id": "u1", "content_type": "problem"}')
    unit = ContentUnit(
        unit_id="u_title",
        source_order=0,
        raw_text="Judul",
        normalized_text="Judul",
        content_type=ContentType.TITLE,
    )
    res = await classifier.classify(unit)
    assert res.content_type == ContentType.TITLE


@pytest.mark.asyncio
async def test_classifier_explanation_contract():
    """Verify classification maps LLM output to ContentType.EXPLANATION."""
    classifier = make_classifier('{"unit_id": "u2", "content_type": "explanation", "reasons": ["Explains mechanism"]}')
    unit = ContentUnit(
        unit_id="u2",
        source_order=1,
        raw_text="Enzim bekerja dengan menurunkan energi aktivasi.",
        normalized_text="Enzim bekerja dengan menurunkan energi aktivasi.",
        content_type=ContentType.OTHER,
    )
    res = await classifier.classify(unit)
    assert res.content_type == ContentType.EXPLANATION
    assert "Explains mechanism" in res.reasons
