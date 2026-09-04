"""
Generate physical benchmark PDF artifact for Research Education domain.
"""

import asyncio
from pathlib import Path
from app.blueprints.content import AudienceLevel, KnowledgeDomain
from app.blueprints.production import TargetArtifactType
from app.orchestration.production_pipeline import MaterialProductionPipeline


async def main():
    sample_text = """
    # Transforming Everyday Observation into a Scientific Research Question

    ## 1. The Phenomenon of Water Quality Degradation
    In urban river ecosystems, community observers notice persistent algal blooms and turbidity changes.
    The primary research challenge is bridging the gap between raw visual observation and formal problem formulation.

    ## 2. Problem Formulation and Scope Limitation
    To make the study actionable, we limit the geographical scope to the Upper Ciliwung Basin
    and operationalize the measurement to dissolved oxygen (DO) and biochemical oxygen demand (BOD).

    ## 3. Scientific Hypothesis
    If residential runoff containing phosphates increases, then downstream dissolved oxygen will decrease inversely.
    """

    output_dir = Path("outputs/benchmark/research_education")
    
    from tests.integration.test_true_production_pipeline import build_mock_intel_agent
    intel_agent = build_mock_intel_agent()
    pipeline = MaterialProductionPipeline(intelligence_agent=intel_agent)

    result = await pipeline.produce_artifact(
        raw_input=sample_text,
        source_hint="research_problem_formulation.md",
        domain=KnowledgeDomain.RESEARCH_METHODOLOGY,
        audience=AudienceLevel.HIGH_SCHOOL,
        target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
        output_dir=output_dir,
    )

    print(f"Success: {result.success}")
    print(f"PDF Generated: {result.pdf_path}")
    print(f"Pages: {len(result.composition.pages)}")


if __name__ == "__main__":
    asyncio.run(main())
