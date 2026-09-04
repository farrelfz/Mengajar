"""
KIR AI Document Intelligence — Composition Tests.
"""
from app.composition.engine import DocumentComposer
from app.intelligence.schemas import BlueprintProposal, ContentGroup, BlueprintCandidateType, DocumentMode, DocumentGenre
from app.design.schemas import VisualBlueprint, PageComposition as VisualPage, ComponentAssignment, ComponentFamily

def test_document_composer_basic():
    composer = DocumentComposer()
    
    group = ContentGroup(
        unit_ids=["u1", "u2"],
        blueprint_candidate=BlueprintCandidateType.GENERIC_CONTENT
    )
    
    proposal = BlueprintProposal(
        source_analysis_id="test",
        document_title="Test Doc",
        document_genre=DocumentGenre.GENERAL,
        recommended_mode=DocumentMode.A4_TUTORIAL,
        content_groups=[group]
    )
    
    vpage = VisualPage(
        page_type="generic",
        composition_pattern="sequential",
        source_group_id=group.group_id,
        source_unit_ids=["u1", "u2"],
        components=[
            ComponentAssignment(
                component_family=ComponentFamily.TEXT_BLOCK,
                source_unit_ids=["u1", "u2"]
            )
        ]
    )
    
    visual = VisualBlueprint(
        source_proposal_id="test",
        document_mode=DocumentMode.A4_TUTORIAL,
        theme_name="default",
        pages=[vpage]
    )
    
    doc = composer.compose(proposal, visual)
    
    assert doc is not None
    assert len(doc.pages) > 0
    assert doc.composition_summary is not None
    assert doc.composition_summary.score >= 0.0
