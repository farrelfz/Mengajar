"""
KIR AI Document Intelligence — Visual Mapper.

The primary entry point for Batch 3.
Transforms a BlueprintProposal (semantic) into a VisualBlueprint (design).
"""

from app.intelligence.schemas import BlueprintProposal
from app.design.schemas import (
    VisualBlueprint, PageComposition, ComponentAssignment, 
    ComponentFamily, ColorRole, VisualWeight
)
from app.design.theme_manager import theme_registry
from app.design.visual_hierarchy import determine_hierarchy, map_hierarchy_to_typography, map_hierarchy_to_weight
from app.design.kti_visual_mapping import get_kti_component_family
from app.design.density_engine import evaluate_density
from app.page_types.registry import page_registry
from app.design.composition_engine import map_intent_to_composition
from app.design.grid_system import get_default_grid
from app.design.balance_evaluator import evaluate_balance
from app.design.visual_rules import evaluate_sequence


def map_to_visual_blueprint(proposal: BlueprintProposal) -> VisualBlueprint:
    """
    Converts a BlueprintProposal into a fully specified VisualBlueprint.
    This maintains traceability but adds styling decisions.
    """
    # 1. Resolve Theme
    theme = theme_registry.get_default_theme()
    
    blueprint = VisualBlueprint(
        source_proposal_id=proposal.proposal_id,
        document_mode=proposal.recommended_mode,
        theme_name=theme.name,
        color_tokens={k.value: v for k, v in theme.colors.items()}
    )
    
    pages = []
    
    # 2. Iterate Content Groups -> Map to Pages
    # For now, we do a simplified 1 group = 1 page mapping (or split if too large)
    for group in proposal.content_groups:
        
        # Determine intent -> composition
        composition = map_intent_to_composition(group.primary_visual_intent)
        
        # Determine page type
        page_type = page_registry.select_page_type(
            role=group.kti_bab or group.blueprint_candidate,  # simplification for role fallback
            intent=group.primary_visual_intent,
            density=group.density,
            mode=proposal.recommended_mode
        )
        
        # Map units to components
        components = []
        
        # Simulate resolving units to components
        # In full implementation, we'd look up the actual ContentUnit.
        # But we don't have the units in the proposal (only unit_ids).
        # We will create generic assignments for traceability.
        if group.title:
            components.append(ComponentAssignment(
                component_family=ComponentFamily.TITLE_BLOCK,
                source_unit_ids=[],  # Title is often a synthesized group property
                typography=map_hierarchy_to_typography(1, proposal.recommended_mode)
            ))
            
        for uid in group.unit_ids:
            # In a full implementation, we look up the actual ContentUnit.
            # Here we provide a structural fallback for the components.
            comp_family = ComponentFamily.TEXT_BLOCK
            comp_weight = VisualWeight.NORMAL
            
            if group.blueprint_candidate.value == "data_evidence_block":
                comp_family = ComponentFamily.DATA_BLOCK
            elif group.blueprint_candidate.value == "key_finding_block":
                comp_family = ComponentFamily.KEY_STATEMENT
                comp_weight = VisualWeight.DOMINANT
            elif group.blueprint_candidate.value == "conclusion_block":
                comp_family = ComponentFamily.SUMMARY_BLOCK
                comp_weight = VisualWeight.DOMINANT
            elif group.blueprint_candidate.value == "warning_block":
                comp_family = ComponentFamily.WARNING_BLOCK
            
            components.append(ComponentAssignment(
                component_family=comp_family,
                visual_weight=comp_weight,
                source_unit_ids=[uid],
                typography=map_hierarchy_to_typography(3, proposal.recommended_mode)
            ))
            
        page = PageComposition(
            page_type=page_type,
            composition_pattern=composition,
            source_group_id=group.group_id,
            source_unit_ids=group.unit_ids,
            components=components,
            grid_specification=get_default_grid(proposal.recommended_mode)
        )
        
        # Evaluate Balance
        page.balance_report = evaluate_balance(page)
        
        pages.append(page)
        
    blueprint.pages = pages
    
    # 3. Evaluate Sequence (Monotony check)
    sequence_warnings = evaluate_sequence(pages)
    blueprint.global_warnings.extend(sequence_warnings)
    
    return blueprint
