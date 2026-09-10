"""
Stage 8 — ImportanceAnalyzer.

Assigns domain-intrinsic importance scores (0.0 - 1.0) and IntrinsicImportance levels
(FOUNDATIONAL, CENTRAL, SUPPORTING, CONTEXTUAL) based on structural centrality, degree centrality,
and content type without format coverage assumptions. 100% offline compatible.
"""

from __future__ import annotations

from typing import List
from app.intelligence.schemas import (
    ContentType,
    IntrinsicImportance,
    KnowledgeRelationship,
    KnowledgeUnit,
)


class ImportanceAnalyzer:
    """Stage 8: Analyzes domain-intrinsic importance independent of artifact formats."""

    def analyze(
        self,
        units: List[KnowledgeUnit],
        relationships: List[KnowledgeRelationship],
    ) -> List[KnowledgeUnit]:
        if not units:
            return units

        # Compute degree centrality per node
        degree_map: dict[str, int] = {u.id: 0 for u in units}
        for rel in relationships:
            if rel.source_unit_id in degree_map:
                degree_map[rel.source_unit_id] += 1
            if rel.target_unit_id in degree_map:
                degree_map[rel.target_unit_id] += 1

        max_degree = max(degree_map.values()) if degree_map and max(degree_map.values()) > 0 else 1
        has_edges = any(deg > 0 for deg in degree_map.values())

        updated_units: List[KnowledgeUnit] = []
        for u in units:
            deg = degree_map.get(u.id, 0)
            norm_deg = (deg / max_degree) if has_edges else 0.0

            # Type weight
            type_weight = 0.50
            if u.content_type in (ContentType.DEFINITION, ContentType.CONCEPT, ContentType.THEORY):
                type_weight = 0.90
            elif u.content_type in (ContentType.FORMULA, ContentType.HYPOTHESIS, ContentType.CONCLUSION):
                type_weight = 0.85
            elif u.content_type in (ContentType.PROCEDURE, ContentType.METHOD, ContentType.PROBLEM, ContentType.OBJECTIVE, ContentType.ARGUMENT):
                type_weight = 0.75
            elif u.content_type in (ContentType.BACKGROUND, ContentType.CONTEXT, ContentType.TIP):
                type_weight = 0.30

            # Composite score:
            # If the graph has edges, degree centrality modulates type weight.
            # If no edges exist, type_weight defines intrinsic importance.
            if has_edges:
                score = round(min(1.0, 0.6 * type_weight + 0.4 * norm_deg), 2)
            else:
                score = type_weight

            # Assign level
            if score >= 0.80:
                importance = IntrinsicImportance.FOUNDATIONAL
            elif score >= 0.60:
                importance = IntrinsicImportance.CENTRAL
            elif score >= 0.35:
                importance = IntrinsicImportance.SUPPORTING
            else:
                importance = IntrinsicImportance.CONTEXTUAL

            # Create copy with updated importance
            u_dict = u.model_dump()
            u_dict["intrinsic_importance"] = importance
            updated_units.append(KnowledgeUnit(**u_dict))

        return updated_units
