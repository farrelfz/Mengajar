"""
Universal Knowledge Core — Knowledge Selection Engine.

Phase 1C.1 Adversarial Hardening:
Combines Global Knowledge Properties (importance, relationship topology)
with Artifact Specific Relevance (payload types, category metadata, edge types, intent weighting).

100% offline, deterministic, zero keyword matching, zero AI calls.
"""

from __future__ import annotations

from typing import Dict, List, Set, Tuple, Any, Optional
from pydantic import BaseModel, Field

from app.intelligence.schemas import (
    ContentType,
    IntrinsicImportance,
    KnowledgeCategory,
    KnowledgeUnit,
    ResolutionStatus,
    UniversalKnowledgeManifest,
)
from app.intelligence.schemas.relationships import RelationshipType
from app.intelligence.transformation.intent import (
    ArtifactType,
    ResolvedArtifactIntent,
    UncertaintyHandlingPolicy,
)


class SelectedKnowledgeSet(BaseModel):
    """Container for knowledge units selected for blueprint transformation."""
    source_manifest_id: str
    artifact_type: ArtifactType
    selected_units: Dict[str, KnowledgeUnit] = Field(default_factory=dict)
    selected_unit_ids: Tuple[str, ...] = Field(default_factory=tuple)
    filtered_unit_reasons: Dict[str, str] = Field(default_factory=dict)
    selection_rationale: str = ""
    traceability_metadata: Dict[str, Any] = Field(default_factory=dict)


class SelectionFallbackEligibility:
    """Evaluates whether a KnowledgeUnit is safe and eligible for selection fallback."""

    @staticmethod
    def is_eligible(unit: KnowledgeUnit, artifact_type: ArtifactType) -> bool:
        # 1. Structural validity & minimum confidence
        if not unit.id or unit.classification_confidence < 0.20:
            return False

        # 2. Safety & Forbidden exclusions
        tags_lower = {t.lower() for t in (unit.tags or ())}
        if any(f in tags_lower for f in ("forbidden", "unsafe", "safety_exclusion", "toxic")):
            return False

        # 3. Anti-spoiling exclusion (Worksheet activities cannot reveal answers in fallback)
        if artifact_type == ArtifactType.WORKSHEET:
            if "answer_key" in tags_lower or "spoiler" in tags_lower:
                return False

        # 4. Unsupported claim exclusion
        if unit.content_type == ContentType.CLAIM and "unsupported" in tags_lower:
            return False

        return True


class KnowledgeSelectionEngine:
    """Deterministic selection engine applying artifact intent, topological relevance, and uncertainty policies."""

    _IMPORTANCE_RANK: Dict[IntrinsicImportance, int] = {
        IntrinsicImportance.FOUNDATIONAL: 4,
        IntrinsicImportance.CENTRAL: 3,
        IntrinsicImportance.SUPPORTING: 2,
        IntrinsicImportance.CONTEXTUAL: 1,
    }

    _EVIDENCE_RELATIONSHIP_TYPES: Set[RelationshipType] = {
        RelationshipType.SUPPORTED_BY,
        RelationshipType.REFUTES,
        RelationshipType.DEMONSTRATED_BY,
        RelationshipType.MEASURED_BY,
    }

    def _compute_relevance_multiplier(
        self,
        unit: KnowledgeUnit,
        artifact_type: ArtifactType,
        evidence_unit_ids: Set[str],
    ) -> float:
        """Calculates artifact-specific relevance weighting from semantic metadata and topology."""
        multiplier = 1.0

        if artifact_type == ArtifactType.PRESENTATION:
            # Presentation favors high-level concepts, formulas, and core principles
            if unit.content_type in (ContentType.CONCEPT, ContentType.FORMULA, ContentType.DEFINITION):
                multiplier *= 1.5
            if unit.category in (KnowledgeCategory.CORE_CONCEPT, KnowledgeCategory.FORMAL):
                multiplier *= 1.3
            if unit.content_type == ContentType.PROCEDURE:
                multiplier *= 0.8  # Procedures compressed or demoted in presentations

        elif artifact_type == ArtifactType.HANDOUT:
            # Handout favors balanced explanatory context, definitions, examples, procedures
            if unit.content_type in (ContentType.DEFINITION, ContentType.CONCEPT, ContentType.PROCEDURE, ContentType.EXPLANATION, ContentType.EXAMPLE):
                multiplier *= 1.4
            if unit.category in (KnowledgeCategory.CORE_CONCEPT, KnowledgeCategory.PROCEDURAL):
                multiplier *= 1.2

        elif artifact_type == ArtifactType.WORKSHEET:
            # Worksheet favors procedures, empirical data, formulas, questions, facts for active inquiry
            if unit.content_type in (ContentType.PROCEDURE, ContentType.FORMULA, ContentType.QUESTION, ContentType.DATA):
                multiplier *= 1.5
            if unit.category in (KnowledgeCategory.PROCEDURAL, KnowledgeCategory.EMPIRICAL):
                multiplier *= 1.4
            if unit.content_type == ContentType.DEFINITION:
                multiplier *= 0.9  # Plain definitions de-emphasized in active inquiry

        elif artifact_type == ArtifactType.SCIENTIFIC_DOCUMENT:
            # Scientific document favors claims, evidence topology, formulas, formal methodologies
            if unit.content_type in (ContentType.CLAIM, ContentType.EVIDENCE, ContentType.FORMULA, ContentType.PROCEDURE, ContentType.DEFINITION):
                multiplier *= 1.6
            if unit.id in evidence_unit_ids:
                multiplier *= 1.8  # Strong topological boost for units participating in genuine evidence edges

        return multiplier

    def select(
        self,
        manifest: UniversalKnowledgeManifest,
        intent: ResolvedArtifactIntent,
    ) -> SelectedKnowledgeSet:
        selected_units: Dict[str, KnowledgeUnit] = {}
        filtered_reasons: Dict[str, str] = {}

        # 1. Topology Analysis: Centrality & Evidence Edges
        centrality_map: Dict[str, int] = {uid: 0 for uid in manifest.units.keys()}
        evidence_units: Set[str] = set()

        for rel in manifest.relationships:
            if rel.source_unit_id in centrality_map:
                centrality_map[rel.source_unit_id] += 1
            if rel.target_unit_id in centrality_map:
                centrality_map[rel.target_unit_id] += 1
            
            # Check for genuine scientific evidence relationship types
            if rel.relationship in self._EVIDENCE_RELATIONSHIP_TYPES:
                evidence_units.add(rel.source_unit_id)
                evidence_units.add(rel.target_unit_id)

        # 2. Iterate & Filter against Uncertainty Policy & Importance Threshold
        scores: Dict[str, float] = {}

        for unit_id, unit in manifest.units.items():
            # A. Evaluate Uncertainty Policy
            if unit.resolution_status in (ResolutionStatus.UNRESOLVED_OFFLINE, ResolutionStatus.DEFERRED):
                if intent.uncertainty_policy == UncertaintyHandlingPolicy.EXCLUDE_UNRESOLVED:
                    filtered_reasons[unit_id] = f"Excluded by uncertainty policy ({unit.resolution_status.value})"
                    continue
                elif intent.uncertainty_policy == UncertaintyHandlingPolicy.ISOLATE_AS_LIMITATION:
                    if intent.artifact_type not in (ArtifactType.SCIENTIFIC_DOCUMENT, ArtifactType.HANDOUT):
                        filtered_reasons[unit_id] = f"Excluded: unresolved state isolated from core artifact ({unit.resolution_status.value})"
                        continue

            # B. Importance Threshold Check
            rank = self._IMPORTANCE_RANK.get(unit.intrinsic_importance, 1)
            if intent.min_importance_threshold == "HIGH" and rank < 3:
                filtered_reasons[unit_id] = f"Below minimum importance threshold (Rank {rank} < 3)"
                continue
            elif intent.min_importance_threshold == "MEDIUM" and rank < 2:
                filtered_reasons[unit_id] = f"Below minimum importance threshold (Rank {rank} < 2)"
                continue

            # C. Compute Final Selection Score (Global Properties + Topology + Artifact Specific Relevance)
            base_score = float(rank * 10 + centrality_map.get(unit_id, 0) * 2)
            rel_multiplier = self._compute_relevance_multiplier(unit, intent.artifact_type, evidence_units)
            final_score = base_score * rel_multiplier

            scores[unit_id] = round(final_score, 3)
            selected_units[unit_id] = unit

        # Fallback: if all units were filtered out, ensure non-empty artifact generation
        # by preserving only eligible candidate units without violating safety exclusions.
        if not selected_units and manifest.units:
            eligible_candidates = [
                u for u in manifest.units.values()
                if SelectionFallbackEligibility.is_eligible(u, intent.artifact_type)
            ]
            if eligible_candidates:
                cand_scores = {}
                for u in eligible_candidates:
                    rank = self._IMPORTANCE_RANK.get(u.intrinsic_importance, 1)
                    base_score = float(rank * 10 + centrality_map.get(u.id, 0) * 2)
                    rel_mult = self._compute_relevance_multiplier(u, intent.artifact_type, evidence_units)
                    cand_scores[u.id] = round(base_score * rel_mult, 3)

                best_score = max(cand_scores.values())
                for u in eligible_candidates:
                    if cand_scores[u.id] >= best_score * 0.8:
                        scores[u.id] = cand_scores[u.id]
                        selected_units[u.id] = u
                filtered_reasons.clear()

        # 3. Sort selected unit IDs deterministically by (final_score, unit_id)
        sorted_ids = sorted(
            selected_units.keys(),
            key=lambda uid: (scores[uid], uid),
            reverse=True,
        )

        rationale = (
            f"Selected {len(selected_units)} / {len(manifest.units)} units for {intent.artifact_type.value}. "
            f"Uncertainty policy: {intent.uncertainty_policy.value}. "
            f"Filtered out {len(filtered_reasons)} units."
        )

        traceability = {
            "source_manifest_id": manifest.manifest_id,
            "total_source_units": len(manifest.units),
            "selected_count": len(selected_units),
            "filtered_count": len(filtered_reasons),
            "relevance_scores": {uid: scores[uid] for uid in sorted_ids},
        }

        return SelectedKnowledgeSet(
            source_manifest_id=manifest.manifest_id,
            artifact_type=intent.artifact_type,
            selected_units=selected_units,
            selected_unit_ids=tuple(sorted_ids),
            filtered_unit_reasons=filtered_reasons,
            selection_rationale=rationale,
            traceability_metadata=traceability,
        )
