"""
Integration Test: True Production Pipeline from Raw Material Request.

Validates the full automated chain without manual blueprint assembly:
Raw Material Request -> ContentIntelligenceAgent -> MaterialBlueprintGenerator ->
LibraryResolver -> CompositionBridge -> MasterRenderEngine -> Real Playwright PDF.
"""

from pathlib import Path
import pytest

from app.ai.client import AICapability, AIClient, GenerationRequest, GenerationResponse
from app.ai.fallback import FallbackChain
from app.ai.model_registry import ModelRegistry
from app.ai.model_selector import ModelSelector
from app.agents.content_intelligence_agent import ContentIntelligenceAgent
from app.blueprints.content import AudienceLevel, KnowledgeDomain
from app.blueprints.production import TargetArtifactType
from app.config.settings import AppSettings
from app.intelligence.classifier import SemanticClassifier
from app.intelligence.importance_scorer import ImportanceScorer
from app.intelligence.normalizer import InputNormalizer
from app.intelligence.output_validator import OutputValidator
from app.intelligence.relationship_extractor import RelationshipExtractor
from app.intelligence.research_role_detector import ResearchRoleDetector
from app.intelligence.segmenter import ContentSegmenter
from app.intelligence.traceability_engine import ResearchTraceabilityEngine
from app.intelligence.visual_intent_detector import VisualIntentDetector
from app.orchestration.production_pipeline import MaterialProductionPipeline


class MockPipelineAI(AIClient):
    """Mock AI client returning valid structured responses for pipeline steps."""

    @property
    def provider_name(self) -> str:
        return "mock_pipeline_ai"

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
            resp = '{"unit_id": "u", "content_type": "problem", "research_role": "research_problem", "kti_bab": "BAB_1", "is_core_component": true}'
        elif "relationship_extraction" in step:
            resp = '{"relationships": []}'
        elif "visual_intent_detection" in step:
            resp = '{"intents": [{"unit_id": "u", "intent_type": "problem_formulation", "recommended_representation": "diagram"}]}'
        else:
            resp = "{}"

        return GenerationResponse(
            content=resp,
            model_used="mock-model",
            provider=self.provider_name,
            capability_used=request.required_capability,
        )


def build_mock_intel_agent() -> ContentIntelligenceAgent:
    mock_ai = MockPipelineAI()
    registry = ModelRegistry()
    registry.register(mock_ai)
    settings = AppSettings(
        primary_provider="mock_pipeline_ai",  # type: ignore
        fallback_to_ollama=False,
        offline_mode=False,
        nine_router_api_key="mock",
    )
    selector = ModelSelector(registry=registry, settings=settings)
    fallback_chain = FallbackChain(selector=selector, registry=registry, settings=settings)
    validator = OutputValidator(fallback_chain=fallback_chain, settings=settings)

    return ContentIntelligenceAgent(
        normalizer=InputNormalizer(),
        segmenter=ContentSegmenter(),
        classifier=SemanticClassifier(validator=validator),
        research_role_detector=ResearchRoleDetector(validator=validator),
        relationship_extractor=RelationshipExtractor(validator=validator),
        importance_scorer=ImportanceScorer(),
        visual_intent_detector=VisualIntentDetector(validator=validator),
        traceability_engine=ResearchTraceabilityEngine(),
    )


@pytest.mark.asyncio
async def test_true_production_pipeline_research_problem(tmp_path: Path):
    raw_material_request = """
    # Transforming Phenomenon into a Research Question

    ## Definition
    A research problem is a statement about an area of concern, a condition to be improved,
    or a troubling question that exists in scholarly literature or in practice.

    ## Key Phenomenon & Problem Identification
    Students observe everyday phenomena such as river sedimentation or water quality decay.
    The primary challenge is identifying the underlying gap between ideal ecological balance
    and factual pollution levels.

    ## Formulation and Scope Limitation
    To construct a testable research question, researchers must limit the geographical and temporal
    scope and identify specific measurable variables.
    """

    output_dir = tmp_path / "research_education_benchmark"
    intel_agent = build_mock_intel_agent()
    pipeline = MaterialProductionPipeline(intelligence_agent=intel_agent)

    result = await pipeline.produce_artifact(
        raw_input=raw_material_request,
        source_hint="research_problem_guide.md",
        domain=KnowledgeDomain.RESEARCH_METHODOLOGY,
        audience=AudienceLevel.HIGH_SCHOOL,
        target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
        output_dir=output_dir,
    )

    # 1. Pipeline Success Check
    assert result.success is True, f"Pipeline failed with errors: {result.errors}"
    assert result.pdf_path is not None
    assert Path(result.pdf_path).exists()

    # 2. Automated Blueprint Verification
    bp = result.material_blueprint
    assert bp.content.metadata.title != ""
    assert len(bp.content.objectives) >= 1
    assert len(bp.pedagogy.sequence) >= 3

    # 3. Composition & Asset Verification
    comp = result.composition
    assert len(comp.pages) >= 3
    cap_ids = [p.metadata.get("capability_id") for p in comp.pages]
    assert any("problem.funnel" in cid or "presentation" in cid for cid in cap_ids)

    # 4. Verify PDF file properties
    pdf_file = Path(result.pdf_path)
    assert pdf_file.stat().st_size > 0
