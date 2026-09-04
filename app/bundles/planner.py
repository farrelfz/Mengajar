"""
Multi-Artifact Curriculum Bundle Planner.

Decomposes target concept into shared objectives and plans coordinated artifact pipelines.
"""

from __future__ import annotations

from app.adaptation.contracts import SharedLearningObjective
from app.bundles.allocation import ContentAllocationPolicy, ObjectiveCoverageMatrix
from app.bundles.contracts import ArtifactBundleRequest, ArtifactRole
from app.director.contracts import CognitiveLevel


class BundlePlanner:
    """Plans multi-artifact curriculum bundles from a single concept."""

    def plan_objectives(self, concept: str) -> list[SharedLearningObjective]:
        """Decompose concept into 3 canonical shared learning objectives."""
        return [
            SharedLearningObjective(
                objective_id="LO1",
                statement=f"Define and explain the physical principles of {concept}",
                cognitive_level=CognitiveLevel.UNDERSTAND,
                target_concept=concept,
                mastery_criteria="Qualitative conceptual explanation",
            ),
            SharedLearningObjective(
                objective_id="LO2",
                statement=f"Apply formal mathematical models to solve quantitative {concept} problems",
                cognitive_level=CognitiveLevel.APPLY,
                target_concept=concept,
                mastery_criteria="Quantitative problem derivation",
            ),
            SharedLearningObjective(
                objective_id="LO3",
                statement=f"Analyze multi-variable systems and evaluate equilibrium under {concept}",
                cognitive_level=CognitiveLevel.ANALYZE,
                target_concept=concept,
                mastery_criteria="Multi-variable system analysis",
            ),
        ]

    def plan_bundle(self, request: ArtifactBundleRequest) -> tuple[list[SharedLearningObjective], dict[str, dict[str, bool]]]:
        """Generate objectives and coverage matrix for bundle request."""
        objectives = self.plan_objectives(request.concept)
        matrix = ObjectiveCoverageMatrix.build_matrix(objectives, request.artifacts)
        return objectives, matrix
