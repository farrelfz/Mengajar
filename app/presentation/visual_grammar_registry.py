"""
Canonical Visual Grammar Registry.

Single authoritative source of truth for presentation layouts, visual intents,
and narrative-to-layout compatibility rules. Shared across SlideArchitect,
VisualDirector, SemanticLayoutValidator, and DeterministicRepairEngine.
"""

from __future__ import annotations
from typing import Any
from pydantic import BaseModel


class LayoutRule(BaseModel):
    layout_name: str
    component_type: str
    preferred_css_class: str
    description: str


# Canonical Layout Definitions
CANONICAL_LAYOUTS: dict[str, LayoutRule] = {
    "hero_composition": LayoutRule(
        layout_name="hero_composition",
        component_type="hero_visual",
        preferred_css_class="layout-hero",
        description="Large dramatic headline with centered visual metaphor",
    ),
    "concept_card": LayoutRule(
        layout_name="concept_card",
        component_type="concept_panel",
        preferred_css_class="layout-concept",
        description="Core concept title, structured definition, and key properties",
    ),
    "formula_explainer": LayoutRule(
        layout_name="formula_explainer",
        component_type="formula_card",
        preferred_css_class="layout-formula",
        description="Mathematical equation with variable breakdown and physical intuition",
    ),
    "three_column_comparison": LayoutRule(
        layout_name="three_column_comparison",
        component_type="comparison_grid",
        preferred_css_class="layout-comparison-3",
        description="Three distinct parallel mechanisms compared side-by-side",
    ),
    "comparison_split": LayoutRule(
        layout_name="comparison_split",
        component_type="split_card",
        preferred_css_class="layout-comparison-2",
        description="Two-column contrasting perspectives or variables",
    ),
    "triangle_relationship": LayoutRule(
        layout_name="triangle_relationship",
        component_type="triangular_model",
        preferred_css_class="layout-triangle",
        description="Three-way interdependent system (e.g., Heat, Fuel, Oxygen)",
    ),
    "timeline_horizontal": LayoutRule(
        layout_name="timeline_horizontal",
        component_type="timeline_sequence",
        preferred_css_class="layout-timeline",
        description="Chronological milestones or multi-step experimental procedure",
    ),
    "data_table": LayoutRule(
        layout_name="data_table",
        component_type="structured_table",
        preferred_css_class="layout-table",
        description="Dense tabular observation records or experimental parameters",
    ),
    "risk_matrix": LayoutRule(
        layout_name="risk_matrix",
        component_type="safety_matrix",
        preferred_css_class="layout-safety",
        description="Laboratory hazard level assessment and protective controls",
    ),
    "minimal_question": LayoutRule(
        layout_name="minimal_question",
        component_type="inquiry_prompt",
        preferred_css_class="layout-question",
        description="High-contrast question prompt for critical thinking and inquiry",
    ),
    "synthesis": LayoutRule(
        layout_name="synthesis",
        component_type="concept_network",
        preferred_css_class="layout-synthesis",
        description="Final concept integration and concluding takeaways",
    ),
    "two_column": LayoutRule(
        layout_name="two_column",
        component_type="narrative_visual",
        preferred_css_class="layout-two-col",
        description="Balanced 50/50 narrative and visual accompaniment",
    ),
}

# Canonical Visual Grammar Matrix
# Maps Narrative Role -> Preferred & Avoided Layouts
VISUAL_GRAMMAR_MATRIX: dict[str, dict[str, Any]] = {
    "PROCESS": {
        "preferred": ["timeline_horizontal", "two_column", "data_table"],
        "avoid": ["concept_card", "three_column_comparison", "risk_matrix", "hero_composition"],
        "reason": "Sequential procedural workflows require directional step or timeline layouts rather than cards",
    },
    "QUESTION": {
        "preferred": ["minimal_question", "hero_composition", "two_column"],
        "avoid": ["data_table", "three_column_comparison", "risk_matrix"],
        "reason": "Inquiry and reflection require high-contrast minimal prompt layouts",
    },
    "FORMULA": {
        "preferred": ["formula_explainer", "two_column"],
        "avoid": ["data_table", "three_column_comparison", "risk_matrix", "timeline_horizontal"],
        "reason": "Mathematical models require centered formula display with variable breakdowns",
    },
    "COMPARISON": {
        "preferred": ["three_column_comparison", "comparison_split", "two_column"],
        "avoid": ["timeline_horizontal", "minimal_question", "risk_matrix"],
        "reason": "Comparative mechanisms require parallel multi-column contrasting grids",
    },
    "SAFETY": {
        "preferred": ["risk_matrix", "two_column"],
        "avoid": ["minimal_question", "timeline_horizontal", "formula_explainer"],
        "reason": "Laboratory safety protocols require prominent hazard matrices and control callouts",
    },
    "OBSERVATION": {
        "preferred": ["data_table", "two_column"],
        "avoid": ["hero_composition", "minimal_question", "formula_explainer", "timeline_horizontal"],
        "reason": "Empirical observation records require structured tabular data presentation",
    },
    "SYNTHESIS": {
        "preferred": ["synthesis", "two_column", "concept_card"],
        "avoid": ["risk_matrix", "formula_explainer", "data_table"],
        "reason": "Conclusion and synthesis require holistic conceptual network or takeaway layouts",
    },
    "HOOK": {
        "preferred": ["hero_composition", "minimal_question", "two_column"],
        "avoid": ["data_table", "risk_matrix", "formula_explainer"],
        "reason": "Engagement hooks require visual-first hero compositions",
    },
    "MECHANISM": {
        "preferred": ["formula_explainer", "triangle_relationship", "two_column", "concept_card", "timeline_horizontal"],
        "avoid": ["minimal_question", "data_table"],
        "reason": "Scientific mechanisms require causal flow or relationship diagrams",
    },
    "CONCEPT_INTRODUCTION": {
        "preferred": ["concept_card", "two_column"],
        "avoid": ["risk_matrix", "data_table"],
        "reason": "Core conceptual introductions require focused card or balanced two-column presentation",
    },
    "CONTEXT": {
        "preferred": ["two_column", "concept_card", "risk_matrix"],
        "avoid": ["formula_explainer"],
        "reason": "Contextual background information requires balanced narrative layout",
    },
}
