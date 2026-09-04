"""
Adversarial Case F: Multi-page duplicate content detection.
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
from app.quality.redundancy_evaluator import RedundancyEvaluator


def test_three_page_duplicate_content_heavily_penalized():
    dup_span = "Detailed paragraph defining the mathematical derivation of torque rotational vectors across spatial frames."
    pages = []
    for p_num in range(1, 4):
        block = ContentBlock(
            component_family=ComponentFamily.TEXT_BLOCK,
            source_unit_ids=[f"u_{p_num}"],
            raw_content=dup_span,
        )
        page = PageComposition(
            page_number=p_num,
            page_type="content",
            composition_type="single_region",
            regions={RegionRole.PRIMARY: PageRegion(role=RegionRole.PRIMARY, blocks=[block])},
        )
        pages.append(page)

    comp = DocumentComposition(
        document_id="doc_triple_dup",
        title="Triple Duplicate Test",
        mode=DocumentMode.A4_PORTRAIT,
        theme_reference="default",
        source_blueprint_id="bp_dup",
        pages=pages,
    )

    metrics, findings = RedundancyEvaluator.evaluate(comp)

    # 2 duplicate findings (on page 2 and page 3)
    assert len(findings) == 2
    assert all(f.dimension == QualityDimension.REDUNDANCY for f in findings)
    assert metrics[0].score <= 0.50
