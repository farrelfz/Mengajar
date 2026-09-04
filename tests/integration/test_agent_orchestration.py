"""Integration tests for Agent Orchestration boundaries and handoffs."""


from app.agents.document_planner import DocumentPlanner
from app.agents.quality_critic import QualityCritic
from app.intelligence.blueprint_proposer import BlueprintProposer
from app.intelligence.schemas import (
    AnalysisResult,
    ContentType,
    ContentUnit,
    DocumentGenre,
)


def test_document_planner_transforms_analysis_without_modifying_source_units():
    """Verify DocumentPlanner preserves original content units intact."""
    proposer = BlueprintProposer()
    planner = DocumentPlanner(proposer=proposer)

    u1 = ContentUnit(source_order=0, raw_text="Teks asli 1", normalized_text="Teks asli 1", content_type=ContentType.EXPLANATION)
    u2 = ContentUnit(source_order=1, raw_text="Teks asli 2", normalized_text="Teks asli 2", content_type=ContentType.EXPLANATION)

    analysis = AnalysisResult(
        job_id="job-orch-1",
        source_file="orch.md",
        content_units=[u1, u2],
        document_genre=DocumentGenre.GENERAL,
    )

    import asyncio
    proposal = asyncio.run(planner.plan(analysis))

    assert proposal.source_analysis_id == "job-orch-1"
    all_group_uids = [uid for g in proposal.content_groups for uid in g.unit_ids]
    assert u1.unit_id in all_group_uids
    assert u2.unit_id in all_group_uids


def test_quality_critic_identifies_unacceptable_blueprints():
    """Verify QualityCritic flags critical issues in blueprint proposal."""
    from app.ai.client import AICapability, AIClient, GenerationRequest, GenerationResponse
    from app.ai.fallback import FallbackChain
    from app.ai.model_registry import ModelRegistry
    from app.ai.model_selector import ModelSelector
    from app.config.settings import AppSettings
    from app.intelligence.output_validator import OutputValidator
    from app.intelligence.schemas import BlueprintProposal

    class MockCriticAI(AIClient):
        @property
        def provider_name(self) -> str:
            return "mock_critic"

        @property
        def supported_capabilities(self) -> list[AICapability]:
            return [AICapability.CRITIQUE, AICapability.STRUCTURED_OUTPUT]

        async def generate(self, request: GenerationRequest) -> GenerationResponse:
            return GenerationResponse(
                content='{"is_acceptable": false, "critical_issues": ["Orphan conclusion detected"], "warnings": []}',
                model_used="critic-mock",
                provider=self.provider_name,
                capability_used=request.required_capability,
            )

    mock_client = MockCriticAI()
    registry = ModelRegistry()
    registry.register(mock_client)
    settings = AppSettings(primary_provider="mock_critic", fallback_to_ollama=False, nine_router_api_key="mock")  # type: ignore
    selector = ModelSelector(registry=registry, settings=settings)
    fallback_chain = FallbackChain(selector=selector, registry=registry, settings=settings)
    validator = OutputValidator(fallback_chain=fallback_chain, settings=settings)

    critic = QualityCritic(validator=validator)
    proposal = BlueprintProposal(
        source_analysis_id="job-critic",
        document_title="Bad Doc",
    )

    import asyncio
    res = asyncio.run(critic.critique_blueprint(proposal, "job-critic"))
    assert res.is_acceptable is False
    assert "Orphan conclusion detected" in res.critical_issues
