"""
Content Allocation Policy & Objective Coverage Matrix.

Maps artifact roles to pedagogical strategies, formats, and shared learning objectives.
"""

from __future__ import annotations

from app.adaptation.contracts import SharedLearningObjective
from app.bundles.contracts import ArtifactRole
from app.director.contracts import MaterialStrategyType


ROLE_SPECS: dict[ArtifactRole, dict[str, Any]] = {
    ArtifactRole.PRESENTATION: {
        "format_id": "presentation_16_9",
        "strategy": MaterialStrategyType.PRESENTATION_STORY,
        "objectives_focus": ["LO1"],
        "target_artifact": "teaching_presentation",
        "description": "Visual anchor and core intuition",
    },
    ArtifactRole.HANDOUT: {
        "format_id": "a4_portrait",
        "strategy": MaterialStrategyType.CONCRETE_TO_ABSTRACT,
        "objectives_focus": ["LO1", "LO2"],
        "target_artifact": "detailed_handout",
        "description": "Exhaustive conceptual reference and formal derivation",
    },
    ArtifactRole.WORKSHEET: {
        "format_id": "a4_portrait",
        "strategy": MaterialStrategyType.WORKED_EXAMPLE_PROGRESSIVE,
        "objectives_focus": ["LO2", "LO3"],
        "target_artifact": "worksheet",
        "description": "Active problem solving and guided exercises",
    },
    ArtifactRole.ASSESSMENT: {
        "format_id": "a4_portrait",
        "strategy": MaterialStrategyType.EXAM_PREPARATION,
        "objectives_focus": ["LO1", "LO2", "LO3"],
        "target_artifact": "exam_worksheet",
        "description": "Formative evaluation and mastery checks",
    },
    ArtifactRole.TEACHER_GUIDE: {
        "format_id": "a4_landscape",
        "strategy": MaterialStrategyType.RESEARCH_METHOD_TUTORIAL,
        "objectives_focus": ["LO1", "LO2", "LO3"],
        "target_artifact": "detailed_handout",
        "description": "Lesson timeline and misconception intervention",
    },
}


class ContentAllocationPolicy:
    """Allocates formats and strategy configurations per artifact role."""

    @staticmethod
    def get_role_spec(role: ArtifactRole) -> dict[str, Any]:
        return ROLE_SPECS.get(role, ROLE_SPECS[ArtifactRole.HANDOUT])


class ObjectiveCoverageMatrix:
    """Calculates coverage of shared learning objectives across bundle items."""

    @staticmethod
    def build_matrix(
        objectives: list[SharedLearningObjective],
        roles: list[ArtifactRole],
    ) -> dict[str, dict[str, bool]]:
        """Construct a matrix of [Role][Objective_ID] -> bool."""
        matrix: dict[str, dict[str, bool]] = {}

        for role in roles:
            spec = ContentAllocationPolicy.get_role_spec(role)
            target_ids = spec["objectives_focus"]
            role_coverage: dict[str, bool] = {}

            for obj in objectives:
                role_coverage[obj.objective_id] = (
                    obj.objective_id in target_ids or "all" in target_ids
                )

            matrix[role.value] = role_coverage

        return matrix
