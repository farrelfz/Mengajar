"""
Unit tests for CapabilitySelectionCritic and RedundancyCritic.
"""

import pytest

from app.composition.schemas import (
    ContentBlock,
    DocumentComposition,
    PageComposition,
    PageRegion,
    RegionRole,
)
from app.critic.capability_selection import CapabilitySelectionCritic
from app.critic.context import CritiqueContextBuilder
from app.critic.contracts import CritiquePerspective
from app.critic.redundancy import RedundancyCritic
from app.design.schemas import ComponentFamily
from app.intelligence.schemas import DocumentMode


def test_capability_selection_critic_flags_grid_for_sequential_process():
    # Comparison block containing linear temporal steps
    page = PageComposition(
        page_number=1,
        page_type="content",
        composition_type="single_region",
        regions={
            RegionRole.PRIMARY: PageRegion(
                role=RegionRole.PRIMARY,
                blocks=[
                    ContentBlock(
                        component_family=ComponentFamily.COMPARISON_BLOCK,
                        source_unit_ids=["u1"],
                        raw_content="Step 1: Initialize experiment. Step 2: Measure resistance. Step 3: Compute current.",
                    )
                ],
            )
        },
    )
    comp = DocumentComposition(
        document_id="doc_cap_test",
        title="Cap Test",
        mode=DocumentMode.A4_PORTRAIT,
        theme_reference="default",
        source_blueprint_id="bp",
        pages=[page],
    )
    ctx = CritiqueContextBuilder("job_cap").with_composition(comp).build()
    critic = CapabilitySelectionCritic()
    findings = critic.critique(ctx)

    assert len(findings) == 1
    assert "Parallel Component" in findings[0].title or "Sequential Process" in findings[0].title
    assert findings[0].perspective == CritiquePerspective.CAPABILITY_SELECTION


def test_redundancy_critic_detects_substantive_cross_page_duplicate_content():
    dup_span = "Detailed paragraph explaining the conservation of angular momentum and torque tensors."
    p1 = PageComposition(page_number=1, page_type="content", composition_type="single_region", regions={RegionRole.PRIMARY: PageRegion(role=RegionRole.PRIMARY, blocks=[ContentBlock(component_family=ComponentFamily.TEXT_BLOCK, source_unit_ids=["u1"], raw_content=dup_span)])})
    p2 = PageComposition(page_number=2, page_type="content", composition_type="single_region", regions={RegionRole.PRIMARY: PageRegion(role=RegionRole.PRIMARY, blocks=[ContentBlock(component_family=ComponentFamily.TEXT_BLOCK, source_unit_ids=["u2"], raw_content=dup_span)])})
    comp = DocumentComposition(document_id="doc_red_test", title="Red Test", mode=DocumentMode.A4_PORTRAIT, theme_reference="default", source_blueprint_id="bp", pages=[p1, p2])

    ctx = CritiqueContextBuilder("job_red").with_composition(comp).build()
    critic = RedundancyCritic()
    findings = critic.critique(ctx)

    assert len(findings) == 1
    assert "Substantial Conceptual Repetition" in findings[0].title
    assert findings[0].perspective == CritiquePerspective.REDUNDANCY
