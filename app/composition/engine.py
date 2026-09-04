"""
KIR AI Document Intelligence — Core Composition Engine.
"""
from app.intelligence.schemas import BlueprintProposal
from app.design.schemas import VisualBlueprint
from app.composition.schemas import DocumentComposition, ContentBlock
from app.composition.composition_resolver import CompositionResolver
from app.composition.quality_evaluator import evaluate_composition_quality
from app.composition.kti_integrator import validate_kti_progression

class DocumentComposer:
    def compose(self, proposal: BlueprintProposal, visual: VisualBlueprint) -> DocumentComposition:
        resolver = CompositionResolver(mode=visual.document_mode)
        
        doc = DocumentComposition(
            mode=visual.document_mode,
            theme_reference=visual.theme_name,
            source_blueprint_id=visual.blueprint_id
        )
        
        page_num = 1
        all_source_units = []
        for group in proposal.content_groups:
            all_source_units.extend(group.unit_ids)
            
            blocks = []
            for vpage in visual.pages:
                if vpage.source_group_id == group.group_id:
                    for comp in vpage.components:
                        blocks.append(ContentBlock(
                            component_family=comp.component_family,
                            source_unit_ids=comp.source_unit_ids,
                            typography=comp.typography,
                            color_role=comp.color_role
                        ))
                        
            if not blocks:
                # If no components assigned, skip or mock
                continue
                
            pages = resolver.resolve_group_to_pages(group, blocks, page_num)
            
            for p in pages:
                p.metadata["kti_bab"] = group.kti_bab
                
            doc.pages.extend(pages)
            page_num += len(pages)
            
        doc.composition_summary = evaluate_composition_quality(all_source_units, doc)
        
        if proposal.document_genre.value == "research_report":
            kti_warnings = validate_kti_progression(doc)
            doc.warnings.extend(kti_warnings)
            
        return doc
