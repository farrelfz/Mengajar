"""
Material Invariants & Regression Protection: Guards semantic, pedagogical, structural, and format invariants.
"""

from __future__ import annotations

from typing import Any
from app.blueprints.contracts import SemanticMaterialBlueprint
from app.composition.schemas import DocumentComposition
from app.refinement.contracts import (
    InvariantCategory,
    InvariantViolation,
    RefinedArtifactBundle,
)


class InvariantChecker:
    """Validates that candidate artifacts satisfy non-negotiable preservation invariants."""

    @classmethod
    def check_invariants(
        cls,
        baseline: RefinedArtifactBundle,
        candidate: RefinedArtifactBundle,
    ) -> list[InvariantViolation]:
        violations: list[InvariantViolation] = []

        # 1. SEMANTIC INVARIANT: All baseline Learning Objectives must remain present
        if baseline.blueprint and baseline.blueprint.content:
            base_objs = {o.objective.strip().lower() for o in baseline.blueprint.content.objectives if o.objective}
            cand_objs = set()
            if candidate.blueprint and candidate.blueprint.content:
                cand_objs = {o.objective.strip().lower() for o in candidate.blueprint.content.objectives if o.objective}

            missing_objs = base_objs - cand_objs
            if missing_objs:
                violations.append(
                    InvariantViolation(
                        category=InvariantCategory.SEMANTIC_INVARIANT,
                        invariant_name="learning_objectives_preserved",
                        description=f"Candidate accidentally removed {len(missing_objs)} baseline learning objectives: {list(missing_objs)[:3]}.",
                        violating_data={"missing_objectives": list(missing_objs)},
                    )
                )

            # 2. SEMANTIC INVARIANT: Baseline Core Concepts must remain present
            base_concepts = {c.name.strip().lower() for c in baseline.blueprint.content.concepts if c.name}
            cand_concepts = set()
            if candidate.blueprint and candidate.blueprint.content:
                cand_concepts = {c.name.strip().lower() for c in candidate.blueprint.content.concepts if c.name}

            missing_concepts = base_concepts - cand_concepts
            if missing_concepts:
                violations.append(
                    InvariantViolation(
                        category=InvariantCategory.SEMANTIC_INVARIANT,
                        invariant_name="core_concepts_preserved",
                        description=f"Candidate removed {len(missing_concepts)} core concept definitions: {list(missing_concepts)[:3]}.",
                        violating_data={"missing_concepts": list(missing_concepts)},
                    )
                )

        # 3. STRUCTURAL INVARIANT: DocumentComposition must not be empty
        if not candidate.composition.pages:
            violations.append(
                InvariantViolation(
                    category=InvariantCategory.STRUCTURAL_INVARIANT,
                    invariant_name="non_empty_composition",
                    description="Candidate composition contains 0 pages.",
                    violating_data={"page_count": 0},
                )
            )

        # 4. FORMAT INVARIANT: Target format string must match baseline
        if baseline.target_format != candidate.target_format:
            violations.append(
                InvariantViolation(
                    category=InvariantCategory.FORMAT_INVARIANT,
                    invariant_name="target_format_invariant",
                    description=f"Candidate changed format from '{baseline.target_format}' to '{candidate.target_format}'.",
                    violating_data={"baseline_format": baseline.target_format, "candidate_format": candidate.target_format},
                )
            )

        return violations
