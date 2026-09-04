"""
KIR AI Document Intelligence — Research Education Domain Pack.

Houses capabilities specifically developed for Research Education:
- Scientific Thinking (Reasoning pathway, Hypothesis testing)
- Research Problem Formulation (Problem funnel, Literature gap)
- Research Methodology (Methodology design matrix)
"""

from app.libraries.research_education.scientific_thinking import (
    scientific_reasoning_pathway_capability,
    hypothesis_test_capability,
)
from app.libraries.research_education.research_problem import (
    problem_funnel_capability,
    research_gap_capability,
)
from app.libraries.research_education.methodology import (
    methodology_design_capability,
)

__all__ = [
    "scientific_reasoning_pathway_capability",
    "hypothesis_test_capability",
    "problem_funnel_capability",
    "research_gap_capability",
    "methodology_design_capability",
]
