"""
KIR AI Document Intelligence — Composition Engine.

Maps semantic visual intent to abstract composition patterns.
"""

from app.intelligence.schemas import VisualIntent
from app.design.schemas import CompositionPattern


def map_intent_to_composition(intent: VisualIntent) -> CompositionPattern:
    """
    Translates a semantic visual intent into a concrete compositional layout pattern.
    """
    mapping = {
        VisualIntent.TEXT_FOCUSED: CompositionPattern.SEQUENTIAL,
        VisualIntent.HIERARCHICAL: CompositionPattern.LAYERED,
        VisualIntent.SEQUENTIAL: CompositionPattern.SEQUENTIAL,
        VisualIntent.COMPARATIVE: CompositionPattern.COMPARISON,
        VisualIntent.PROCESS_FLOW: CompositionPattern.DIRECTIONAL,
        VisualIntent.DATA_TREND: CompositionPattern.DATA_DOMINANT,
        VisualIntent.DATA_COMPARISON: CompositionPattern.COMPARISON,
        VisualIntent.DATA_DISTRIBUTION: CompositionPattern.DATA_DOMINANT,
        VisualIntent.RELATIONSHIP: CompositionPattern.DIRECTIONAL,
        VisualIntent.CAUSE_EFFECT: CompositionPattern.DIRECTIONAL,
        VisualIntent.TIMELINE: CompositionPattern.SEQUENTIAL,
        VisualIntent.CHECKLIST: CompositionPattern.ACTION,
        VisualIntent.STEP_BY_STEP: CompositionPattern.SEQUENTIAL,
        VisualIntent.EVIDENCE_GALLERY: CompositionPattern.GRID,
        VisualIntent.QUOTE_HIGHLIGHT: CompositionPattern.EMPHASIS,
        VisualIntent.KEY_MESSAGE: CompositionPattern.SINGLE_FOCUS,
        VisualIntent.SUMMARY: CompositionPattern.DISTILLED,
        VisualIntent.DECISION: CompositionPattern.ACTION,
        VisualIntent.REFERENCE: CompositionPattern.SEQUENTIAL,
    }
    
    return mapping.get(intent, CompositionPattern.SEQUENTIAL)
