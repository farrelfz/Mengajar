"""
Adversarial Case E: Format-aware extreme density overload across physical formats.
"""

import pytest

from app.composition.schemas import (
    ContentBlock,
    DocumentComposition,
    PageComposition,
    PageRegion,
    RegionRole,
)
from app.design.schemas import ComponentFamily
from app.intelligence.schemas import DocumentMode
from app.quality.contracts import QualityDimension, QualitySeverity
from app.quality.density_evaluator import DensityEvaluator


def test_extreme_density_overload_on_presentation():
    # 2,200 chars on 16:9 presentation slide (threshold: warning > 1200, error > 1800)
    extreme_text = "Extreme wall of text with redundant explanations. " * 45  # ~2250 chars
    page = PageComposition(
        page_number=1,
        page_type="content",
        composition_type="single_region",
        regions={
            RegionRole.PRIMARY: PageRegion(
                role=RegionRole.PRIMARY,
                blocks=[ContentBlock(component_family=ComponentFamily.TEXT_BLOCK, source_unit_ids=["u1"], raw_content=extreme_text)],
            )
        },
    )
    comp = DocumentComposition(
        document_id="doc_extreme_dense",
        title="Density Overload",
        mode=DocumentMode.PRESENTATION_16_9,
        theme_reference="default",
        source_blueprint_id="bp_dense",
        pages=[page],
    )

    metrics_pres, findings_pres = DensityEvaluator.evaluate(comp, target_format="presentation_16_9")

    assert len(findings_pres) >= 1
    assert any(f.severity == QualitySeverity.ERROR for f in findings_pres)
    assert any("excessive textual density" in f.finding.lower() for f in findings_pres)
    assert metrics_pres[0].score <= 0.70

    # On A4 portrait, 2250 chars is acceptable (< 3500)
    metrics_a4, findings_a4 = DensityEvaluator.evaluate(comp, target_format="a4_portrait")
    assert len(findings_a4) == 0
    assert metrics_a4[0].score == 1.0
