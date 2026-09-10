"""
Universal Document Intelligence System V5 — Failure Correlation Engine.

Phase 3A.1: Clusters co-occurring failures on shared pages into unified FailureClusters
to prevent redundant, overlapping, or conflicting repair actions.
"""

from __future__ import annotations

from typing import Dict, List, Set, Tuple
from collections import defaultdict

from app.quality.causal.contracts import CanonicalFailure, FailureCluster, RootCauseHypothesis
from app.quality.causal.evidence_collector import MultiLayerEvidence
from app.quality.causal.taxonomy import (
    ArchitectureLayer,
    CanonicalFailureCode,
    CanonicalRepairClass,
    CausalConfidenceLevel,
    FailureScope,
)


class FailureCorrelationEngine:
    """Detects co-occurring failure patterns and groups them into unified clusters."""

    # Symptoms that frequently co-occur due to blueprint/layout capacity overload
    CAPACITY_SYMPTOMS = {
        CanonicalFailureCode.TEXT_TOO_SMALL,
        CanonicalFailureCode.ELEMENT_COLLISION,
        CanonicalFailureCode.DENSITY_OVERLOAD,
        CanonicalFailureCode.CARD_OVERLOAD,
    }

    @classmethod
    def cluster_failures(
        cls,
        failures: List[CanonicalFailure],
        evidence: MultiLayerEvidence,
    ) -> List[FailureCluster]:
        if not failures:
            return []

        # 1. Map failures by affected pages
        page_to_failures: Dict[int, List[CanonicalFailure]] = defaultdict(list)
        global_failures: List[CanonicalFailure] = []

        for f in failures:
            if not f.affected_pages or f.scope == FailureScope.ARTIFACT_WIDE:
                global_failures.append(f)
            else:
                for p in f.affected_pages:
                    page_to_failures[p].append(f)

        # 2. Build connected page components
        clusters: List[FailureCluster] = []
        visited_pages: Set[int] = set()

        for p, p_fails in page_to_failures.items():
            if p in visited_pages:
                continue

            # Find all connected pages that share any failure with page p
            cluster_pages: Set[int] = {p}
            cluster_failures_set: Set[CanonicalFailure] = set(p_fails)

            to_expand = list(p_fails)
            while to_expand:
                curr_f = to_expand.pop()
                for other_p in curr_f.affected_pages:
                    if other_p not in cluster_pages:
                        cluster_pages.add(other_p)
                        for other_f in page_to_failures[other_p]:
                            if other_f not in cluster_failures_set:
                                cluster_failures_set.add(other_f)
                                to_expand.append(other_f)

            visited_pages.update(cluster_pages)

            # Synthesize root cause for this page cluster
            c_fails = list(cluster_failures_set)
            sorted_pages = tuple(sorted(cluster_pages))
            symptoms = tuple(sorted(set(f.failure_code for f in c_fails), key=lambda x: x.value))

            primary_cause = cls._synthesize_cluster_cause(symptoms, sorted_pages, evidence)

            clusters.append(
                FailureCluster(
                    affected_pages=sorted_pages,
                    symptoms=symptoms,
                    failures=tuple(c_fails),
                    primary_root_cause=primary_cause,
                    is_ambiguous=primary_cause.confidence_level == CausalConfidenceLevel.AMBIGUOUS if primary_cause else False,
                    recommended_repair_class=(
                        primary_cause.allowed_repair_classes[0]
                        if primary_cause and primary_cause.allowed_repair_classes
                        else CanonicalRepairClass.NONE
                    ),
                    rationale=(
                        f"Co-occurring symptoms {list(s.value for s in symptoms)} on pages {sorted_pages} "
                        f"correlated to {primary_cause.cause_code if primary_cause else 'UNKNOWN'}."
                    ),
                )
            )

        # 3. Add global / artifact-wide failures as separate standalone clusters
        for gf in global_failures:
            single_cause = cls._synthesize_cluster_cause((gf.failure_code,), gf.affected_pages, evidence)
            clusters.append(
                FailureCluster(
                    affected_pages=gf.affected_pages,
                    symptoms=(gf.failure_code,),
                    failures=(gf,),
                    primary_root_cause=single_cause,
                    is_ambiguous=single_cause.confidence_level == CausalConfidenceLevel.AMBIGUOUS if single_cause else False,
                    recommended_repair_class=(
                        single_cause.allowed_repair_classes[0]
                        if single_cause and single_cause.allowed_repair_classes
                        else CanonicalRepairClass.NONE
                    ),
                    rationale=f"Artifact-wide defect: {gf.failure_code.value} - {gf.symptom}",
                )
            )

        return clusters

    @classmethod
    def _synthesize_cluster_cause(
        cls,
        symptoms: Tuple[CanonicalFailureCode, ...],
        affected_pages: Tuple[int, ...],
        evidence: MultiLayerEvidence,
    ) -> RootCauseHypothesis:
        # Check if symptoms contain capacity triad (tiny text + collision / overload)
        has_capacity_symptoms = any(s in cls.CAPACITY_SYMPTOMS for s in symptoms)

        if has_capacity_symptoms:
            # Check evidence: blueprint overload vs typography scale
            if evidence.blueprint_capacity_exceeded or evidence.is_font_isolated_to_dense_pages:
                return RootCauseHypothesis(
                    cause_code="BLUEPRINT_CAPACITY_MISMATCH",
                    cause_layer=ArchitectureLayer.BLUEPRINT,
                    confidence_score=0.86,
                    confidence_level=CausalConfidenceLevel.HIGH,
                    supporting_evidence=(
                        f"Planned blocks exceed capacity limit ({evidence.max_blocks_per_page} > {evidence.layout_slot_capacity})",
                        "Font reduction isolated only to dense/overloaded pages",
                        f"Element collisions present on pages {affected_pages}",
                    ),
                    contradicting_evidence=(),
                    affected_scope=FailureScope.CLUSTER if len(affected_pages) >= 3 else FailureScope.LOCAL,
                    repair_authority=ArchitectureLayer.BLUEPRINT,
                    allowed_repair_classes=(
                        CanonicalRepairClass.CLASS_D_BLUEPRINT_REGROUPING,
                        CanonicalRepairClass.CLASS_C_LAYOUT_REMAPPING,
                    ),
                    forbidden_repairs=("GLOBAL_FONT_SHRINK", "TEXT_CLIPPING_SUPPRESSION"),
                )
            elif evidence.is_font_globally_small:
                return RootCauseHypothesis(
                    cause_code="TYPOGRAPHY_CONFIGURATION_FAILURE",
                    cause_layer=ArchitectureLayer.TYPOGRAPHY,
                    confidence_score=0.84,
                    confidence_level=CausalConfidenceLevel.HIGH,
                    supporting_evidence=(
                        "Font size is unreadable across >70% of pages regardless of content",
                        "Blueprint block count is within normal bounds",
                    ),
                    contradicting_evidence=(),
                    affected_scope=FailureScope.SYSTEMIC,
                    repair_authority=ArchitectureLayer.TYPOGRAPHY,
                    allowed_repair_classes=(CanonicalRepairClass.CLASS_B_TYPOGRAPHY,),
                    forbidden_repairs=("SPLIT_CONTENT_GROUP",),
                )

        # Anti-spoiling leak
        if CanonicalFailureCode.WORKSHEET_SPOILING_FAILURE in symptoms:
            return RootCauseHypothesis(
                cause_code="ANTI_SPOILING_POLICY_BREACH",
                cause_layer=ArchitectureLayer.ARTIFACT_POLICY,
                confidence_score=0.95,
                confidence_level=CausalConfidenceLevel.HIGH,
                supporting_evidence=("Answer keywords exposed in student activity area",),
                contradicting_evidence=(),
                affected_scope=FailureScope.LOCAL,
                repair_authority=ArchitectureLayer.ARTIFACT_POLICY,
                allowed_repair_classes=(CanonicalRepairClass.CLASS_F_ARTIFACT_POLICY,),
                forbidden_repairs=("CSS_OPACITY_ZERO",),
            )

        # Scientific citation invisible
        if CanonicalFailureCode.SCIENTIFIC_CITATION_INVISIBLE in symptoms:
            return RootCauseHypothesis(
                cause_code="CITATION_RENDER_SUPPRESSION",
                cause_layer=ArchitectureLayer.COMPOSITION,
                confidence_score=0.85,
                confidence_level=CausalConfidenceLevel.HIGH,
                supporting_evidence=("Multi-page scientific paper with 0 visible citations in body text",),
                contradicting_evidence=(),
                affected_scope=FailureScope.ARTIFACT_WIDE,
                repair_authority=ArchitectureLayer.COMPOSITION,
                allowed_repair_classes=(CanonicalRepairClass.CLASS_F_ARTIFACT_POLICY,),
                forbidden_repairs=("SOURCE_REWRITE",),
            )

        # Worksheet quiz collapse
        if CanonicalFailureCode.WORKSHEET_QUIZ_COLLAPSE in symptoms:
            return RootCauseHypothesis(
                cause_code="TRANSFORMATION_SELECTION_FAILURE",
                cause_layer=ArchitectureLayer.TRANSFORMATION,
                confidence_score=0.88,
                confidence_level=CausalConfidenceLevel.HIGH,
                supporting_evidence=("Repetitive quiz questions without scaffolded inquiry progression",),
                contradicting_evidence=(),
                affected_scope=FailureScope.ARTIFACT_WIDE,
                repair_authority=ArchitectureLayer.TRANSFORMATION,
                allowed_repair_classes=(CanonicalRepairClass.CLASS_E_TRANSFORMATION_STRATEGY,),
                forbidden_repairs=("LAYOUT_CSS_PATCH",),
            )

        # Default fallback
        return RootCauseHypothesis(
            cause_code="GENERAL_RENDER_DEFECT",
            cause_layer=ArchitectureLayer.RENDER,
            confidence_score=0.55,
            confidence_level=CausalConfidenceLevel.MEDIUM,
            supporting_evidence=(f"Observed symptoms: {[s.value for s in symptoms]}",),
            contradicting_evidence=(),
            affected_scope=FailureScope.LOCAL,
            repair_authority=ArchitectureLayer.RENDER,
            allowed_repair_classes=(CanonicalRepairClass.CLASS_A_GEOMETRY,),
            forbidden_repairs=(),
        )
