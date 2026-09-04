"""
Semantic Correctness & Objective Coverage Evaluator.

Checks whether all declared learning objectives have corresponding content,
ensures core concept definitions are fully articulated, and detects undefined concepts.
"""

from __future__ import annotations

from app.blueprints.contracts import SemanticMaterialBlueprint
from app.quality.contracts import (
    QualityDimension,
    QualityFinding,
    QualityMetric,
    QualitySeverity,
)


class SemanticEvaluator:
    """Evaluates semantic integrity and learning objective coverage."""

    @staticmethod
    def evaluate(
        blueprint: SemanticMaterialBlueprint | None,
    ) -> tuple[list[QualityMetric], list[QualityFinding]]:
        metrics: list[QualityMetric] = []
        findings: list[QualityFinding] = []

        if not blueprint or not blueprint.content:
            return metrics, findings

        score = 1.0
        content = blueprint.content
        objectives = content.objectives
        concepts = content.concepts

        if not objectives:
            score -= 0.3
            findings.append(
                QualityFinding(
                    dimension=QualityDimension.SEMANTIC_CORRECTNESS,
                    severity=QualitySeverity.WARNING,
                    finding="Material blueprint has no explicit learning objectives defined.",
                    score_impact=-0.3,
                    recommendation="Define explicit measurable learning objectives in Level A content blueprint.",
                )
            )

        if not concepts:
            score -= 0.5
            findings.append(
                QualityFinding(
                    dimension=QualityDimension.SEMANTIC_CORRECTNESS,
                    severity=QualitySeverity.ERROR,
                    finding="Material blueprint has no core concept definitions.",
                    score_impact=-0.5,
                    recommendation="Ensure content intelligence extracts primary concept definitions.",
                )
            )
        else:
            # Check for empty or trivial concept definitions
            concept_names = {c.name.lower().strip() for c in concepts if c.name}
            trivial_concepts = []
            for c in concepts:
                defn = str(c.formal_definition or "").strip()
                if len(defn) < 5:
                    trivial_concepts.append(c.name)

            if trivial_concepts:
                score -= 0.25
                findings.append(
                    QualityFinding(
                        dimension=QualityDimension.SEMANTIC_CORRECTNESS,
                        severity=QualitySeverity.ERROR,
                        finding=f"Incompletely articulated concepts detected: {trivial_concepts}.",
                        evidence={"trivial_concepts": trivial_concepts},
                        score_impact=-0.25,
                        recommendation="Provide formal definitions and intuitive explanations for all core concepts.",
                    )
                )

            # Check objective coverage: objectives targeting concepts that have no definition
            uncovered_objectives = []
            for obj in objectives:
                if obj.target_concept and obj.target_concept.lower().strip() not in concept_names:
                    uncovered_objectives.append(obj.objective)

            if uncovered_objectives:
                score -= 0.3
                findings.append(
                    QualityFinding(
                        dimension=QualityDimension.SEMANTIC_CORRECTNESS,
                        severity=QualitySeverity.WARNING,
                        finding=f"Learning objectives target concepts with no formal definitions: {uncovered_objectives}.",
                        evidence={"uncovered_objectives": uncovered_objectives},
                        score_impact=-0.3,
                        recommendation="Add corresponding concept definitions for all targeted learning objectives.",
                    )
                )

        metrics.append(
            QualityMetric(
                name="objective_and_concept_grounding",
                dimension=QualityDimension.SEMANTIC_CORRECTNESS,
                score=max(0.0, round(score, 3)),
                weight=1.5,
                raw_value={"objectives_count": len(objectives), "concepts_count": len(concepts)},
            )
        )

        return metrics, findings
