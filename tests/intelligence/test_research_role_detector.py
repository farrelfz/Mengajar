"""Unit tests for ResearchRoleDetector contracts."""

import pytest

from app.ai.client import AICapability, AIClient, GenerationRequest, GenerationResponse
from app.ai.fallback import FallbackChain
from app.ai.model_registry import ModelRegistry
from app.ai.model_selector import ModelSelector
from app.config.settings import AppSettings
from app.intelligence.output_validator import OutputValidator
from app.intelligence.research_role_detector import ResearchRoleDetector
from app.intelligence.schemas import ContentType, ContentUnit, KtiBab


class MockRoleAI(AIClient):
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


def make_detector(json_str: str) -> ResearchRoleDetector:
    mock_client = MockRoleAI(json_str)
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
    return ResearchRoleDetector(validator=validator)


@pytest.mark.asyncio
async def test_detect_research_problem_bab1():
    """Verify research problem in BAB 1 is classified with RESEARCH_PROBLEM role."""
    detector = make_detector(
        '{"unit_id": "u1", "content_type": "problem", "research_role": "research_problem", "kti_bab": "BAB_1", "is_core_component": true}'
    )
    unit = ContentUnit(
        unit_id="u1",
        source_order=1,
        raw_text="Penggunaan pestisida sintetis mencemari lingkungan.",
        normalized_text="Penggunaan pestisida sintetis mencemari lingkungan.",
        content_type=ContentType.PROBLEM,
    )
    res = await detector.detect(unit)
    assert res.research_role == ContentType.RESEARCH_PROBLEM
    assert res.kti_bab == KtiBab.BAB_1
    assert res.is_core_component is True


@pytest.mark.asyncio
async def test_detect_research_finding_bab4():
    """Verify statistical findings in BAB 4 are classified with RESEARCH_FINDING role."""
    detector = make_detector(
        '{"unit_id": "u4", "content_type": "finding", "research_role": "research_finding", "kti_bab": "BAB_4", "is_core_component": true}'
    )
    unit = ContentUnit(
        unit_id="u4",
        source_order=4,
        raw_text="Peningkatan konsentrasi berkorelasi positif terhadap mortalitas (p < 0.05).",
        normalized_text="Peningkatan konsentrasi berkorelasi positif terhadap mortalitas (p < 0.05).",
        content_type=ContentType.FINDING,
    )
    res = await detector.detect(unit)
    assert res.research_role == ContentType.RESEARCH_FINDING
    assert res.kti_bab == KtiBab.BAB_4
