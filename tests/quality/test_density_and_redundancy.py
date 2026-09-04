"""
Unit tests for DensityEvaluator and RedundancyEvaluator.
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
from app.quality.redundancy_evaluator import RedundancyEvaluator


def test_density_evaluator_flags_overly_dense_slide():
    # Construct a 16:9 presentation page with excessive text (> 2000 chars)
    dense_text = "This is an extremely dense paragraph. " * 60  # ~2300 chars
    block = ContentBlock(
        component_family=ComponentFamily.TEXT_BLOCK,
        source_unit_ids=["u1"],
        raw_content=dense_text,
    )
    region = PageRegion(
        role=RegionRole.PRIMARY,
        blocks=[block],
    )
    page = PageComposition(
        page_number=1,
        page_type="content",
        composition_type="single_region",
        regions={RegionRole.PRIMARY: region},
    )
    comp = DocumentComposition(
        document_id="doc_test_dense",
        title="Dense Slide Test",
        mode=DocumentMode.PRESENTATION_16_9,
        theme_reference="default",
        source_blueprint_id="bp_1",
        pages=[page],
    )

    metrics, findings = DensityEvaluator.evaluate(comp, target_format="presentation_16_9")

    assert len(findings) >= 1
    assert findings[0].dimension == QualityDimension.INFORMATION_DENSITY
    assert findings[0].severity in [QualitySeverity.WARNING, QualitySeverity.ERROR]
    assert "excessive textual density" in findings[0].finding.lower()
    assert metrics[0].score < 1.0


def test_redundancy_evaluator_detects_duplicate_blocks():
    dup_text = "This is an identical substantial block of text explaining torque rotational principles."
    block1 = ContentBlock(
        component_family=ComponentFamily.TEXT_BLOCK,
        source_unit_ids=["u1"],
        raw_content=dup_text,
    )
    block2 = ContentBlock(
        component_family=ComponentFamily.TEXT_BLOCK,
        source_unit_ids=["u2"],
        raw_content=dup_text,
    )
    page1 = PageComposition(
        page_number=1,
        page_type="content",
        composition_type="single_region",
        regions={RegionRole.PRIMARY: PageRegion(role=RegionRole.PRIMARY, blocks=[block1])},
    )
    page2 = PageComposition(
        page_number=2,
        page_type="content",
        composition_type="single_region",
        regions={RegionRole.PRIMARY: PageRegion(role=RegionRole.PRIMARY, blocks=[block2])},
    )
    comp = DocumentComposition(
        document_id="doc_test_dup",
        title="Duplicate Test",
        mode=DocumentMode.A4_PORTRAIT,
        theme_reference="default",
        source_blueprint_id="bp_2",
        pages=[page1, page2],
    )

    metrics, findings = RedundancyEvaluator.evaluate(comp)

    assert len(findings) == 1
    assert findings[0].dimension == QualityDimension.REDUNDANCY
    assert findings[0].severity == QualitySeverity.WARNING
    assert "duplicate content block detected" in findings[0].finding.lower()
    assert metrics[0].score < 1.0
