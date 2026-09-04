"""Unit tests for RelationshipExtractor and VisualIntentDetector."""

import pytest

from app.ai.client import AICapability, AIClient, GenerationRequest, GenerationResponse
from app.ai.fallback import FallbackChain
from app.ai.model_registry import ModelRegistry
from app.ai.model_selector import ModelSelector
from app.config.settings import AppSettings
from app.intelligence.output_validator import OutputValidator
from app.intelligence.relationship_extractor import RelationshipExtractor
from app.intelligence.schemas import (
    ContentType,
    ContentUnit,
    RelationshipType,
    VisualIntent,
)
from app.intelligence.visual_intent_detector import VisualIntentDetector


class MockGenericAI(AIClient):
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


def make_validator(json_str: str) -> OutputValidator:
    mock_client = MockGenericAI(json_str)
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
    return OutputValidator(fallback_chain=fallback_chain, settings=settings)


@pytest.mark.asyncio
async def test_relationship_extractor_finds_traceability_edge():
    """Verify relationship extractor maps Conclusion -> answers -> Question."""
    validator = make_validator("""
    {
        "relationships": [
            {
                "source_unit_id": "u_conc",
                "target_unit_id": "u_q",
                "relationship_type": "answers",
                "confidence": "high",
                "is_required": true
            }
        ]
    }
    """)
    extractor = RelationshipExtractor(validator=validator)
    u1 = ContentUnit(unit_id="u_q", source_order=0, raw_text="Pertanyaan?", normalized_text="Pertanyaan?", content_type=ContentType.RESEARCH_QUESTION)
    u2 = ContentUnit(unit_id="u_conc", source_order=1, raw_text="Kesimpulan.", normalized_text="Kesimpulan.", content_type=ContentType.RESEARCH_CONCLUSION)

    res = await extractor.extract_relationships([u1, u2])
    assert len(res.relationships) == 1
    assert res.relationships[0].relationship_type == RelationshipType.ANSWERS
    assert res.relationships[0].source_unit_id == "u_conc"
    assert res.relationships[0].target_unit_id == "u_q"


@pytest.mark.asyncio
async def test_visual_intent_detector_detects_step_by_step():
    """Verify procedural steps receive STEP_BY_STEP visual intent."""
    validator = make_validator("""
    {
        "intents": [
            {
                "unit_id": "u_step1",
                "primary_intent": "step_by_step",
                "confidence": "high",
                "reasons": ["Sequential procedure"]
            }
        ]
    }
    """)
    detector = VisualIntentDetector(validator=validator)
    u1 = ContentUnit(unit_id="u_step1", source_order=0, raw_text="1. Haluskan daun.", normalized_text="1. Haluskan daun.", content_type=ContentType.PROCEDURE)

    res = await detector.detect_intents([u1])
    assert len(res.intents) == 1
    assert res.intents[0].primary_intent == VisualIntent.STEP_BY_STEP
