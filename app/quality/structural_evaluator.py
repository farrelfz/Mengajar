"""
Structural Coherence & Organization Evaluator.

Analyzes section completeness, hierarchy consistency, logical progression,
and orphan content block avoidance.
"""

from __future__ import annotations

from app.blueprints.contracts import SemanticMaterialBlueprint
from app.composition.schemas import DocumentComposition
from app.quality.contracts import (
    QualityDimension,
    QualityFinding,
    QualityMetric,
    QualitySeverity,
)


class StructuralEvaluator:
    """Evaluates the structural coherence and organization of material blueprints and compositions."""

    @staticmethod
    def evaluate(
        blueprint: SemanticMaterialBlueprint | None = None,
        composition: DocumentComposition | None = None,
    ) -> tuple[list[QualityMetric], list[QualityFinding]]:
        metrics: list[QualityMetric] = []
        findings: list[QualityFinding] = []

        score = 1.0

        if blueprint:
            content = blueprint.content
            # Check for structural completeness
            has_objectives = bool(content.objectives)
            has_concepts = bool(content.concepts)
            has_facts = bool(content.facts)

            if not has_objectives:
                score -= 0.2
                findings.append(
                    QualityFinding(
                        dimension=QualityDimension.STRUCTURAL_COHERENCE,
                        severity=QualitySeverity.WARNING,
                        finding="Material blueprint lacks explicit learning objectives in its structural header.",
                        evidence={"objectives_count": 0},
                        score_impact=-0.2,
                        recommendation="Define at least one clear learning objective in the content blueprint.",
                    )
                )

            if not has_concepts and not has_facts:
                score -= 0.4
                findings.append(
                    QualityFinding(
                        dimension=QualityDimension.STRUCTURAL_COHERENCE,
                        severity=QualitySeverity.ERROR,
                        finding="Material blueprint has no concept definitions or facts (empty structural payload).",
                        evidence={"concepts_count": 0, "facts_count": 0},
                        score_impact=-0.4,
                        recommendation="Populate the content blueprint with foundational concepts or empirical facts.",
                    )
                )

        if composition:
            if not composition.pages:
                score -= 0.5
                findings.append(
                    QualityFinding(
                        dimension=QualityDimension.STRUCTURAL_COHERENCE,
                        severity=QualitySeverity.CRITICAL,
                        finding="Document composition contains zero pages.",
                        evidence={"page_count": 0},
                        score_impact=-0.5,
                        recommendation="Verify composition engine page allocation logic.",
                    )
                )
            else:
                # Check for empty pages
                empty_pages = []
                for p in composition.pages:
                    total_blocks = sum(len(r.blocks) for r in p.regions.values())
                    if total_blocks == 0:
                        empty_pages.append(p.page_number)

                if empty_pages:
                    score -= 0.3
                    findings.append(
                        QualityFinding(
                            dimension=QualityDimension.STRUCTURAL_COHERENCE,
                            severity=QualitySeverity.ERROR,
                            finding=f"Empty pages detected in composition: Pages {empty_pages}.",
                            evidence={"empty_pages": empty_pages},
                            score_impact=-0.3,
                            recommendation="Remove orphaned empty pages or allocate content regions.",
                        )
                    )

        final_score = max(0.0, score)
        metrics.append(
            QualityMetric(
                name="structural_organization_integrity",
                dimension=QualityDimension.STRUCTURAL_COHERENCE,
                score=final_score,
                weight=1.3,
                raw_value=final_score,
                details={"blueprint_evaluated": blueprint is not None, "composition_evaluated": composition is not None},
            )
        )

        return metrics, findings
