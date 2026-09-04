"""Integration tests for IntelligencePipeline end-to-end flow."""


import pytest

from app.agents.content_intelligence_agent import ContentIntelligenceAgent
from app.agents.document_planner import DocumentPlanner
from app.agents.quality_critic import QualityCritic
from app.ai.client import AICapability, AIClient, GenerationRequest, GenerationResponse
from app.ai.fallback import FallbackChain
from app.ai.model_registry import ModelRegistry
from app.ai.model_selector import ModelSelector
from app.config.settings import AppSettings
from app.intelligence.blueprint_proposer import BlueprintProposer
from app.intelligence.classifier import SemanticClassifier
from app.intelligence.importance_scorer import ImportanceScorer
from app.intelligence.normalizer import InputNormalizer
from app.intelligence.output_validator import OutputValidator
from app.intelligence.relationship_extractor import RelationshipExtractor
from app.intelligence.research_role_detector import ResearchRoleDetector
from app.intelligence.schemas import (
    DocumentGenre,
    DocumentMode,
    JobState,
)
from app.intelligence.segmenter import ContentSegmenter
from app.intelligence.traceability_engine import ResearchTraceabilityEngine
from app.intelligence.visual_intent_detector import VisualIntentDetector
from app.orchestration.pipeline import IntelligencePipeline


class MockIntegrationAI(AIClient):
    """Deterministic mock client that routes structured JSON based on step/prompt."""

    @property
    def provider_name(self) -> str:
        return "mock_integration"

    @property
    def supported_capabilities(self) -> list[AICapability]:
        return [
            AICapability.SEMANTIC_REASONING,
            AICapability.STRUCTURED_OUTPUT,
            AICapability.CRITIQUE,
        ]

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        step = request.step or ""
        if "semantic_classification" in step:
            resp = '{"unit_id": "u", "content_type": "explanation", "reasons": ["Mocked"]}'
        elif "research_role_detection" in step:
            resp = '{"unit_id": "u", "content_type": "finding", "research_role": "research_finding", "kti_bab": "BAB_4", "is_core_component": true}'
        elif "relationship_extraction" in step:
            resp = '{"relationships": []}'
        elif "visual_intent_detection" in step:
            resp = '{"intents": []}'
        elif "quality_critique" in step:
            resp = '{"is_acceptable": true, "critical_issues": [], "warnings": []}'
        else:
            resp = "{}"

        return GenerationResponse(
            content=resp,
            model_used="mock-integration-model",
            provider=self.provider_name,
            capability_used=request.required_capability,
        )


def build_test_pipeline() -> IntelligencePipeline:
    mock_ai = MockIntegrationAI()
    registry = ModelRegistry()
    registry.register(mock_ai)
    settings = AppSettings(
        primary_provider="mock_integration",  # type: ignore
        fallback_to_ollama=False,
        offline_mode=False,
        nine_router_api_key="mock",
    )
    selector = ModelSelector(registry=registry, settings=settings)
    fallback_chain = FallbackChain(selector=selector, registry=registry, settings=settings)
    validator = OutputValidator(fallback_chain=fallback_chain, settings=settings)

    normalizer = InputNormalizer()
    segmenter = ContentSegmenter()
    classifier = SemanticClassifier(validator=validator)
    role_detector = ResearchRoleDetector(validator=validator)
    rel_extractor = RelationshipExtractor(validator=validator)
    scorer = ImportanceScorer()
    visual_detector = VisualIntentDetector(validator=validator)
    traceability_engine = ResearchTraceabilityEngine()

    intel_agent = ContentIntelligenceAgent(
        normalizer=normalizer,
        segmenter=segmenter,
        classifier=classifier,
        research_role_detector=role_detector,
        relationship_extractor=rel_extractor,
        importance_scorer=scorer,
        visual_intent_detector=visual_detector,
        traceability_engine=traceability_engine,
    )
    proposer = BlueprintProposer()
    planner_agent = DocumentPlanner(proposer=proposer, validator=validator)
    critic_agent = QualityCritic(validator=validator)

    return IntelligencePipeline(
        intelligence_agent=intel_agent,
        planner_agent=planner_agent,
        critic_agent=critic_agent,
    )


@pytest.mark.asyncio
async def test_end_to_end_pipeline_execution():
    """Verify raw markdown flows through all 7 pipeline stages to a complete BlueprintProposal."""
    pipeline = build_test_pipeline()

    sample_md = """
# BAB 1 PENDAHULUAN
Penelitian ini membahas pemanfaatan bahan alam.

## 1.1 Rumusan Masalah
Bagaimana efektivitas ekstrak?
"""
    job = await pipeline.run(
        raw_input=sample_md,
        source_hint="sample_integration.md",
        document_genre=DocumentGenre.RESEARCH_REPORT,
        document_mode=DocumentMode.A4_TUTORIAL,
    )

    assert job.state == JobState.COMPLETE
    assert job.analysis_result is not None
    assert len(job.analysis_result.content_units) >= 4
    assert job.blueprint_proposal is not None
    assert len(job.blueprint_proposal.content_groups) >= 2
    assert job.blueprint_proposal.document_genre == DocumentGenre.RESEARCH_REPORT
    assert job.completed_at is not None
