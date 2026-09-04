"""
KIR AI Document Intelligence — Integration Tests for Blueprint to VisualBlueprint.
"""
from app.intelligence.schemas import BlueprintProposal, ContentGroup, DocumentMode, VisualIntent, ContentDensity, ContentType, BlueprintCandidateType
from app.design.visual_mapper import map_to_visual_blueprint
from app.design.schemas import ComponentFamily

def test_blueprint_to_visual_blueprint_traceability():
    group = ContentGroup(
        group_id="group-1",
        title="Test Group",
        unit_ids=["unit-1", "unit-2"],
        primary_visual_intent=VisualIntent.COMPARATIVE,
        density=ContentDensity.MEDIUM,
        blueprint_candidate=BlueprintCandidateType.GENERIC_CONTENT
    )
    proposal = BlueprintProposal(
        source_analysis_id="job-1",
        document_title="Test",
        recommended_mode=DocumentMode.A4_TUTORIAL,
        content_groups=[group]
    )
    
    visual_bp = map_to_visual_blueprint(proposal)
    
    assert visual_bp.document_mode == DocumentMode.A4_TUTORIAL
    assert visual_bp.theme_name == "editorial_hybrid"
    assert len(visual_bp.pages) == 1
    
    page = visual_bp.pages[0]
    assert page.page_type == "COMPARISON"
    
    # Traceability
    assert page.source_group_id == "group-1"
    assert "unit-1" in page.source_unit_ids
