"""
Concept Prerequisite Graph & Remediation Engine.

Models concept dependencies and identifies prerequisite knowledge deficits for learners.
"""

from __future__ import annotations

from app.adaptation.contracts import LearnerProfile


PREREQUISITE_DEPENDENCIES: dict[str, list[str]] = {
    "torque": ["scalar_force", "lever_distance", "vector_components", "rotational_pivot"],
    "newton_third_law": ["vector_force", "interaction_pairs", "isolated_bodies"],
    "research_problem": ["empirical_observation", "literature_gap", "variable_definition"],
    "controlled_experiment": ["independent_variable", "dependent_variable", "confounding_factors"],
    "argumentative_paragraph": ["claim_statement", "evidence_citation", "warrant_reasoning"],
}


class ConceptPrerequisiteGraph:
    """Manages prerequisite dependency graphs for domain concepts."""

    @staticmethod
    def get_prerequisites(concept_key: str) -> list[str]:
        key = concept_key.lower().strip()
        for k, prereqs in PREREQUISITE_DEPENDENCIES.items():
            if k in key:
                return prereqs
        return []

    @staticmethod
    def check_missing_prerequisites(
        concept_key: str,
        learner: LearnerProfile,
    ) -> list[str]:
        """Compare required prerequisites against learner profile mastery."""
        required = ConceptPrerequisiteGraph.get_prerequisites(concept_key)
        missing = []
        for req in required:
            # If not explicitly marked True in learner prerequisite_mastery, mark missing
            if not learner.prerequisite_mastery.get(req, False):
                missing.append(req)
        return missing
