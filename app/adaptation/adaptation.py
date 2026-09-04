"""
Adaptive Content Transformation Engine.

Applies multi-dimensional complexity profiles, vocabulary scaling,
and mathematical formalism tiering to transform blueprints into target learner levels.
"""

from __future__ import annotations

import copy
from app.adaptation.contracts import (
    AdaptationTrace,
    ComplexityLevel,
    ContentComplexityProfile,
    LearnerProfile,
)
from app.adaptation.vocabulary import VocabularyTransformer
from app.blueprints.contracts import SemanticMaterialBlueprint


class AdaptiveContentTransformer:
    """Transforms semantic material blueprints according to target learner and complexity profiles."""

    def transform(
        self,
        blueprint: SemanticMaterialBlueprint,
        learner: LearnerProfile,
        complexity: ContentComplexityProfile,
    ) -> tuple[SemanticMaterialBlueprint, AdaptationTrace]:
        """Apply comprehensive semantic, vocabulary, and formula adaptations."""
        adapted_bp = copy.deepcopy(blueprint)
        trace = AdaptationTrace(
            learner_profile={
                "educational_level": learner.educational_level.value,
                "knowledge_state": learner.knowledge_state.value,
                "mathematical_readiness": learner.mathematical_readiness.value,
            }
        )

        # 1. Adapt Metadata & Titles
        title_lower = adapted_bp.content.metadata.title.lower()
        if "torque" in title_lower or "torsi" in title_lower:
            new_title = VocabularyTransformer.transform_term("torque", complexity.vocabulary_complexity)
            adapted_bp.content.metadata.title = new_title
            trace.vocabulary_transformations.append({
                "original": "torque",
                "adapted": new_title,
                "level": complexity.vocabulary_complexity.value,
            })

        # 2. Adapt Level A Concepts
        for concept in adapted_bp.content.concepts:
            concept_text = f"{concept.name} {concept.formal_definition}".lower()
            if "torque" in concept_text or "torsi" in concept_text:
                adapted_formula = VocabularyTransformer.transform_formula("torque_formula", complexity.mathematical_formalism)
                concept.formal_definition = f"{concept.formal_definition} [Model: {adapted_formula}]"
                trace.formula_transformations.append({
                    "concept": "torque_formula",
                    "formula": adapted_formula,
                    "formalism_level": complexity.mathematical_formalism.value,
                })

        # 3. Adapt Pedagogical Steps
        for step in adapted_bp.pedagogy.sequence:
            step_text = f"{step.purpose} {step.notes or ''}".lower()
            if "torque" in step_text or "torsi" in step_text:
                adapted_formula = VocabularyTransformer.transform_formula("torque_formula", complexity.mathematical_formalism)
                step.notes = f"Adapted Model ({complexity.mathematical_formalism.value}): {adapted_formula}"
                step.purpose = f"{step.purpose} ({complexity.mathematical_formalism.value})"

        trace.complexity_adjustments.append({
            "dimension": "abstraction_level",
            "level": complexity.abstraction_level.value,
        })
        trace.complexity_adjustments.append({
            "dimension": "mathematical_formalism",
            "level": complexity.mathematical_formalism.value,
        })

        return adapted_bp, trace
