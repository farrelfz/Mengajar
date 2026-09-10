"""
Visual Director & Layout Diversity Engine.

Maps semantic block types to rich presentation layouts and enforces
layout diversity constraints across the presentation deck.
"""

from __future__ import annotations

import math
from typing import Any
from pydantic import BaseModel, Field


class LayoutRule(BaseModel):
    layout_name: str
    component_type: str
    preferred_css_class: str
    description: str


LAYOUT_MAPPING: dict[str, LayoutRule] = {
    "hero_phenomenon": LayoutRule(
        layout_name="hero_composition",
        component_type="hero_visual",
        preferred_css_class="layout-hero",
        description="Large dramatic headline with centered visual metaphor",
    ),
    "concept_explainer": LayoutRule(
        layout_name="concept_card",
        component_type="concept_panel",
        preferred_css_class="layout-concept",
        description="Core concept title, structured definition, and key properties",
    ),
    "formula_visual": LayoutRule(
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
    "triangle_diagram": LayoutRule(
        layout_name="triangle_relationship",
        component_type="triangular_model",
        preferred_css_class="layout-triangle",
        description="Three-way interdependent system (e.g., Heat, Fuel, Oxygen)",
    ),
    "step_process": LayoutRule(
        layout_name="timeline_horizontal",
        component_type="process_steps",
        preferred_css_class="layout-process",
        description="Numbered sequential laboratory workflow or timeline",
    ),
    "data_table": LayoutRule(
        layout_name="data_table",
        component_type="table_view",
        preferred_css_class="layout-table",
        description="Observation results and experimental data matrix",
    ),
    "risk_matrix": LayoutRule(
        layout_name="risk_matrix",
        component_type="hazard_warning",
        preferred_css_class="layout-warning",
        description="Safety protocol, hazards, and prevention controls",
    ),
    "reflection_question": LayoutRule(
        layout_name="minimal_question",
        component_type="discussion_prompt",
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

ALTERNATIVE_LAYOUTS: dict[str, list[str]] = {
    "concept_card": ["two_column", "formula_explainer", "synthesis"],
    "hero_composition": ["concept_card", "minimal_question"],
    "three_column_comparison": ["comparison_split", "data_table"],
    "step_process": ["two_column", "data_table"],
    "data_table": ["step_process", "concept_card"],
    "minimal_question": ["concept_card", "two_column"],
}


class VisualDirector:
    """Selects and balances visual layouts across a planned deck."""

    MAX_IDENTICAL_LAYOUT_STREAK: int = 2

    def resolve_layout(self, visual_type: str) -> LayoutRule:
        return LAYOUT_MAPPING.get(visual_type, LAYOUT_MAPPING["concept_explainer"])

    def balance_deck_layouts(self, planned_visual_types: list[str]) -> list[str]:
        """Enforce MAX_IDENTICAL_LAYOUT_STREAK constraint without breaking semantic intent."""
        balanced: list[str] = []
        current_streak = 0
        last_layout = ""

        for v_type in planned_visual_types:
            layout_rule = self.resolve_layout(v_type)
            layout_name = layout_rule.layout_name

            if layout_name == last_layout:
                current_streak += 1
            else:
                current_streak = 1
                last_layout = layout_name

            if current_streak > self.MAX_IDENTICAL_LAYOUT_STREAK:
                # Pick alternative layout
                alternatives = ALTERNATIVE_LAYOUTS.get(layout_name, ["two_column"])
                chosen_alt = alternatives[0]
                # Find visual_type for this alt
                alt_v_type = next((k for k, v in LAYOUT_MAPPING.items() if v.layout_name == chosen_alt), "concept_explainer")
                balanced.append(alt_v_type)
                last_layout = chosen_alt
                current_streak = 1
            else:
                balanced.append(v_type)

        return balanced

    def calculate_layout_entropy(self, layout_names: list[str]) -> float:
        """Calculate Shannon entropy for layout distribution (higher = more diverse)."""
        if not layout_names:
            return 0.0
        counts: dict[str, int] = {}
        for l in layout_names:
            counts[l] = counts.get(l, 0) + 1
        n = len(layout_names)
        entropy = 0.0
        for cnt in counts.values():
            p = cnt / n
            entropy -= p * math.log2(p)
        # Normalize entropy between 0.0 and 1.0 based on unique classes
        max_entropy = math.log2(len(counts)) if len(counts) > 1 else 1.0
        return round(entropy / max_entropy, 3) if max_entropy > 0 else 0.0
