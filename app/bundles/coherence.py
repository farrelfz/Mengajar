"""
Cross-Artifact Coherence & Redundancy Validator.

Ensures bundle items are conceptually unified, role-differentiated, and non-redundant.
"""

from __future__ import annotations

from typing import Any
from app.adaptation.contracts import SharedLearningObjective
from app.bundles.contracts import ArtifactRole, BundleItemResult


class BundleCoherenceValidator:
    """Validates cross-artifact consistency, objective coverage, and non-redundancy."""

    @staticmethod
    def validate_bundle(
        items: list[BundleItemResult],
        shared_objectives: list[SharedLearningObjective],
        coverage_matrix: dict[str, dict[str, bool]],
    ) -> tuple[bool, float, float, list[str]]:
        """
        Validates bundle coherence.
        Returns (is_valid, redundancy_score, complementarity_score, list_of_warnings).
        """
        warnings: list[str] = []

        if not items:
            return False, 0.0, 0.0, ["Bundle contains 0 generated artifacts."]

        # 1. Objective Coverage Check: Ensure every objective is covered by at least 1 artifact
        for obj in shared_objectives:
            covered = any(
                coverage_matrix.get(item.role.value, {}).get(obj.objective_id, False)
                for item in items
            )
            if not covered:
                warnings.append(f"Uncovered learning objective: '{obj.objective_id}' has no assigned artifact.")

        # 2. Redundancy & Complementarity Metrics
        roles = [item.role for item in items]
        unique_roles = len(set(roles))
        total_items = len(items)

        # Redundancy: fraction of identical roles (should be 0 if each artifact is distinct)
        redundancy_score = round(max(0.0, (total_items - unique_roles) / max(1, total_items)), 2)

        # Complementarity: diversity of distinct pedagogical functions fulfilled
        complementarity_score = round(min(1.0, unique_roles / max(1, total_items)), 2)

        # 3. Check for exact duplicate stage sequences across distinct roles
        stage_sequences = {item.role: item.journey_stages for item in items}
        if ArtifactRole.PRESENTATION in stage_sequences and ArtifactRole.HANDOUT in stage_sequences:
            if stage_sequences[ArtifactRole.PRESENTATION] == stage_sequences[ArtifactRole.HANDOUT]:
                warnings.append("High redundancy: Presentation has identical stage sequence to Handout.")

        is_valid = len([w for w in warnings if not w.startswith("Warning")]) == 0
        return is_valid, redundancy_score, complementarity_score, warnings
