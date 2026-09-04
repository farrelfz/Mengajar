"""
Unit tests for VisualCommunicationCritic and NarrativeCritic.
"""

import pytest

from app.composition.schemas import (
    ContentBlock,
    DocumentComposition,
    PageComposition,
    PageRegion,
    RegionRole,
)
from app.critic.context import CritiqueContextBuilder
from app.critic.contracts import CritiquePerspective
from app.critic.narrative import NarrativeCritic
from app.critic.visual import VisualCommunicationCritic
from app.design.schemas import ComponentFamily
from app.intelligence.schemas import DocumentMode


def test_visual_critic_flags_uniform_layout_monotony():
    # 5 pages all using identical single_region
    pages = [
        PageComposition(
            page_number=i,
            page_type="content",
            composition_type="single_region",
            regions={RegionRole.PRIMARY: PageRegion(role=RegionRole.PRIMARY, blocks=[ContentBlock(component_family=ComponentFamily.TEXT_BLOCK, source_unit_ids=[f"u{i}"], raw_content="Text")])},
        )
        for i in range(1, 6)
    ]
    comp = DocumentComposition(
        document_id="doc_monotony",
        title="Monotony",
        mode=DocumentMode.A4_PORTRAIT,
        theme_reference="default",
        source_blueprint_id="bp",
        pages=pages,
    )
    ctx = CritiqueContextBuilder("job_vis").with_composition(comp).build()
    critic = VisualCommunicationCritic()
    findings = critic.critique(ctx)

    assert len(findings) == 1
    assert findings[0].id == "vis_layout_monotony"
    assert findings[0].perspective == CritiquePerspective.VISUAL_COMMUNICATION


def test_narrative_critic_flags_abrupt_termination_in_long_document():
    # 5 pages with no conclusion
    pages = [
        PageComposition(
            page_number=i,
            page_type="exercise" if i == 5 else "content",
            composition_type="single_region",
            regions={RegionRole.PRIMARY: PageRegion(role=RegionRole.PRIMARY, blocks=[ContentBlock(component_family=ComponentFamily.TEXT_BLOCK, source_unit_ids=[f"u{i}"], raw_content="Text")])},
        )
        for i in range(1, 6)
    ]
    comp = DocumentComposition(
        document_id="doc_narrative",
        title="Narrative Test",
        mode=DocumentMode.A4_PORTRAIT,
        theme_reference="default",
        source_blueprint_id="bp",
        pages=pages,
    )
    ctx = CritiqueContextBuilder("job_narr").with_composition(comp).build()
    critic = NarrativeCritic()
    findings = critic.critique(ctx)

    assert len(findings) == 1
    assert findings[0].id == "narrative_abrupt_closure"
    assert findings[0].perspective == CritiquePerspective.NARRATIVE
