"""
Regression test for A4 landscape pagination (verifying 4 steps produce 4 pages, not 8).
"""
from pathlib import Path
import pytest
import pymupdf

from app.blueprints.content import KnowledgeDomain, AudienceLevel
from app.blueprints.production import TargetArtifactType
from app.orchestration.production_pipeline import MaterialProductionPipeline
from tests.integration.test_true_production_pipeline import build_mock_intel_agent


SAMPLE_TOPIC_TEXT = """# Rotational Dynamics & Torque
Torque is the rotational equivalent of linear force.
When an external force is applied at a distance from a pivot, it creates a turning effect.

## Key Principles
- Torque depends on force magnitude and lever arm length.
- Perpendicular forces produce maximum torque.
- Balanced torques result in rotational equilibrium.

## Worked Example
A 50 N force is applied perpendicularly to a 2.0 m lever arm.
Calculate the resulting torque.
The torque is calculated as tau = r * F = 2.0 * 50 = 100 N*m.
"""


@pytest.mark.asyncio
async def test_a4_landscape_produces_exact_page_count(tmp_path: Path):
    """
    Verify that A4 Landscape rendering produces 1 physical PDF page per composition step,
    confirming the resolution of RISK-01 (CSS height specificity conflict).
    """
    agent = build_mock_intel_agent()
    pipeline = MaterialProductionPipeline(intelligence_agent=agent)

    output_dir = tmp_path / "landscape_regression"
    result = await pipeline.produce_artifact(
        raw_input=SAMPLE_TOPIC_TEXT,
        source_hint="rotational_torque.md",
        domain=KnowledgeDomain.PHYSICS,
        audience=AudienceLevel.HIGH_SCHOOL,
        target_artifact=TargetArtifactType.TEACHING_PRESENTATION,
        output_dir=output_dir,
        target_format="a4_landscape",
    )

    assert result.success is True
    assert result.pdf_path is not None
    assert Path(result.pdf_path).exists()

    # Inspect physical PDF with PyMuPDF
    doc = pymupdf.open(result.pdf_path)
    page_count = len(doc)
    expected_pages = len(result.composition.pages)
    assert page_count == expected_pages, f"Expected exactly {expected_pages} pages for {expected_pages} composition steps in A4 landscape, got {page_count}"

    for page in doc:
        rect = page.rect
        # 297mm x 210mm in points is ~841.89 pt x 595.28 pt
        assert abs(rect.width - 841.89) < 2.0
        assert abs(rect.height - 595.28) < 2.0

    doc.close()
