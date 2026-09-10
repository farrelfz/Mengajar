"""
Universal Document Intelligence System V5 — Root Cause Analysis.

Phase 3B: Deterministic, explainable root cause inference from finding clusters
and multi-layer quality evidence.
"""

from __future__ import annotations

import uuid
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.quality.contracts.findings import FindingCluster, QualityFinding
from app.quality.repair.contracts import RepairMutationClass, RepairTarget


class RootCauseType(str, Enum):
    """Canonical taxonomy of underlying failure origins."""
    CONTENT_DENSITY = "CONTENT_DENSITY"
    CONTENT_GROUPING = "CONTENT_GROUPING"
    TYPOGRAPHY = "TYPOGRAPHY"
    GRID_GEOMETRY = "GRID_GEOMETRY"
    PADDING_SPACING = "PADDING_SPACING"
    ASSET_ALLOCATION = "ASSET_ALLOCATION"
    PAGE_BREAK = "PAGE_BREAK"
    LAYOUT_SELECTION = "LAYOUT_SELECTION"
    SEMANTIC_LAYOUT_MAPPING = "SEMANTIC_LAYOUT_MAPPING"
    NARRATIVE_ORDER = "NARRATIVE_ORDER"
    INQUIRY_STRUCTURE = "INQUIRY_STRUCTURE"
    TRACEABILITY_MAPPING = "TRACEABILITY_MAPPING"
    EVIDENCE_MAPPING = "EVIDENCE_MAPPING"
    SOURCE_INSUFFICIENCY = "SOURCE_INSUFFICIENCY"
    RENDERER_NONDETERMINISM = "RENDERER_NONDETERMINISM"
    UNKNOWN = "UNKNOWN"


class RootCauseHypothesis(BaseModel):
    """Attributed root cause hypothesis backed by correlated evidence."""
    model_config = ConfigDict(frozen=True)

    root_cause_id: str = Field(default_factory=lambda: f"rc_{uuid.uuid4().hex[:8]}")
    cause_type: RootCauseType
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    supporting_findings: Tuple[QualityFinding, ...] = Field(default_factory=tuple)
    affected_targets: Tuple[RepairTarget, ...] = Field(default_factory=tuple)
    competing_hypotheses: Tuple[Tuple[RootCauseType, float], ...] = Field(default_factory=tuple)
    repairability: bool = True
    suggested_mutation_class: RepairMutationClass = RepairMutationClass.CLASS_A_GEOMETRY
    rationale: str = ""


class DeterministicRootCauseAnalyzer:
    """Infers the root cause of quality defects deterministically."""

    @classmethod
    def analyze(
        cls,
        findings: Sequence[QualityFinding],
        clusters: Sequence[FindingCluster] = (),
        metrics: Optional[Dict[str, Any]] = None,
        artifact_type: str = "main",
    ) -> List[RootCauseHypothesis]:
        metrics = metrics or {}
        hypotheses: List[RootCauseHypothesis] = []

        # Process correlated clusters first
        clustered_finding_ids = set()
        for cluster in clusters:
            all_cluster_findings = [cluster.canonical_finding] + list(cluster.correlated_findings)
            for f in all_cluster_findings:
                clustered_finding_ids.add(f.finding_id)

            hyp = cls._infer_cluster_cause(cluster, all_cluster_findings, metrics, artifact_type)
            if hyp:
                hypotheses.append(hyp)

        # Process unclustered individual findings
        for f in findings:
            if f.finding_id in clustered_finding_ids:
                continue
            hyp = cls._infer_single_finding_cause(f, metrics, artifact_type)
            if hyp:
                hypotheses.append(hyp)

        # Sort by confidence descending, non-repairable/blocking first
        hypotheses.sort(key=lambda h: (not h.repairability, h.confidence), reverse=True)
        return hypotheses

    @classmethod
    def _infer_cluster_cause(
        cls,
        cluster: FindingCluster,
        findings: List[QualityFinding],
        metrics: Dict[str, Any],
        artifact_type: str,
    ) -> RootCauseHypothesis:
        codes = {f.failure_code for f in findings}
        targets = cls._extract_targets(findings, artifact_type)

        # Pattern 1: Overflow + Small Font or High Occupancy -> Content Density
        if ("TEXT_OVERFLOW" in codes or "TEXT_CLIPPING" in codes) and (
            "FONT_TOO_SMALL" in codes or metrics.get("occupancy", 0.0) > 0.85
        ):
            return RootCauseHypothesis(
                cause_type=RootCauseType.CONTENT_DENSITY,
                confidence=0.94,
                supporting_findings=tuple(findings),
                affected_targets=tuple(targets),
                competing_hypotheses=(
                    (RootCauseType.GRID_GEOMETRY, 0.60),
                    (RootCauseType.TYPOGRAPHY, 0.45),
                ),
                repairability=True,
                suggested_mutation_class=RepairMutationClass.CLASS_B_COMPOSITION,
                rationale="Text overflow co-occurring with reduced font size or high occupancy indicates content overload.",
            )

        # Pattern 2: Multiple collision/margin errors -> Grid Geometry
        if "ELEMENT_COLLISION" in codes or "MARGIN_VIOLATION" in codes:
            return RootCauseHypothesis(
                cause_type=RootCauseType.GRID_GEOMETRY,
                confidence=0.88,
                supporting_findings=tuple(findings),
                affected_targets=tuple(targets),
                competing_hypotheses=(
                    (RootCauseType.PADDING_SPACING, 0.65),
                ),
                repairability=True,
                suggested_mutation_class=RepairMutationClass.CLASS_A_GEOMETRY,
                rationale="Element collisions or margin breaches indicate grid geometry constraint failure.",
            )

        # Pattern 3: Broken inquiry arc / Answer spoiling -> Inquiry Structure
        if "INQUIRY_ARC_BROKEN" in codes or "ANTI_SPOILING_BREACH" in codes:
            return RootCauseHypothesis(
                cause_type=RootCauseType.INQUIRY_STRUCTURE,
                confidence=0.96,
                supporting_findings=tuple(findings),
                affected_targets=tuple(targets),
                repairability=True,
                suggested_mutation_class=RepairMutationClass.CLASS_D_PEDAGOGICAL_STRUCTURE,
                rationale="Pedagogical inquiry sequence violation or anti-spoiling leak requires inquiry structure repair.",
            )

        # Fallback to canonical finding cause
        return cls._infer_single_finding_cause(cluster.canonical_finding, metrics, artifact_type)

    @classmethod
    def _infer_single_finding_cause(
        cls,
        f: QualityFinding,
        metrics: Dict[str, Any],
        artifact_type: str,
    ) -> RootCauseHypothesis:
        code = f.failure_code
        targets = cls._extract_targets([f], artifact_type)

        # 1. Physical Render Failures
        if code in ("TEXT_CLIPPING", "TEXT_OVERFLOW"):
            occupancy = metrics.get("occupancy", metrics.get("page_occupancy", 0.0))
            is_dense = occupancy > 0.88 or metrics.get("card_count", 0) >= 5 or metrics.get("text_length", 0) > 600
            if is_dense:
                return RootCauseHypothesis(
                    cause_type=RootCauseType.CONTENT_DENSITY,
                    confidence=0.92,
                    supporting_findings=(f,),
                    affected_targets=tuple(targets),
                    competing_hypotheses=(
                        (RootCauseType.PADDING_SPACING, 0.60),
                        (RootCauseType.TYPOGRAPHY, 0.40),
                    ),
                    repairability=True,
                    suggested_mutation_class=RepairMutationClass.CLASS_B_COMPOSITION,
                    rationale=f"Overflow on {code} under high density/occupancy ({occupancy:.2f}) indicates excessive content volume.",
                )
            else:
                return RootCauseHypothesis(
                    cause_type=RootCauseType.PADDING_SPACING,
                    confidence=0.82,
                    supporting_findings=(f,),
                    affected_targets=tuple(targets),
                    competing_hypotheses=(
                        (RootCauseType.GRID_GEOMETRY, 0.70),
                        (RootCauseType.TYPOGRAPHY, 0.50),
                    ),
                    repairability=True,
                    suggested_mutation_class=RepairMutationClass.CLASS_A_GEOMETRY,
                    rationale=f"Overflow on {code} under moderate density indicates padding/spacing constraint mismatch.",
                )

        elif code in ("FONT_TOO_SMALL", "TINY_TEXT", "TEXT_TOO_SMALL"):
            return RootCauseHypothesis(
                cause_type=RootCauseType.TYPOGRAPHY,
                confidence=0.88,
                supporting_findings=(f,),
                affected_targets=tuple(targets),
                competing_hypotheses=(
                    (RootCauseType.SEMANTIC_LAYOUT_MAPPING, 0.80),
                    (RootCauseType.GRID_GEOMETRY, 0.65),
                ),
                repairability=True,
                suggested_mutation_class=RepairMutationClass.CLASS_A_GEOMETRY,
                rationale="Font size below format legibility threshold; requires typography scaling or layout remap.",
            )

        elif code in ("MARGIN_VIOLATION", "VIEWPORT_BREACH"):
            return RootCauseHypothesis(
                cause_type=RootCauseType.PADDING_SPACING,
                confidence=0.88,
                supporting_findings=(f,),
                affected_targets=tuple(targets),
                competing_hypotheses=(
                    (RootCauseType.GRID_GEOMETRY, 0.70),
                ),
                repairability=True,
                suggested_mutation_class=RepairMutationClass.CLASS_A_GEOMETRY,
                rationale="Element breaches safe margins; container padding or spacing needs adjustment.",
            )

        elif code in ("ELEMENT_COLLISION", "OVERLAPPING_CONTENT"):
            return RootCauseHypothesis(
                cause_type=RootCauseType.GRID_GEOMETRY,
                confidence=0.92,
                supporting_findings=(f,),
                affected_targets=tuple(targets),
                competing_hypotheses=(
                    (RootCauseType.SEMANTIC_LAYOUT_MAPPING, 0.85),
                    (RootCauseType.CONTENT_DENSITY, 0.70),
                ),
                repairability=True,
                suggested_mutation_class=RepairMutationClass.CLASS_A_GEOMETRY,
                rationale="Visual elements overlap due to conflicting grid positioning; requires component reflow or layout remap.",
            )

        elif code in ("ACCIDENTAL_PAGE", "ORPHAN_PAGE"):
            return RootCauseHypothesis(
                cause_type=RootCauseType.PAGE_BREAK,
                confidence=0.91,
                supporting_findings=(f,),
                affected_targets=tuple(targets),
                repairability=True,
                suggested_mutation_class=RepairMutationClass.CLASS_B_COMPOSITION,
                rationale="Trailing accidental page with minimal content caused by overflow page break.",
            )

        # 2. Compositional & Layout Failures
        elif code in ("LAYOUT_MONOTONY", "LAYOUT_TAXONOMY_MISMATCH", "REPETITION_STREAK", "FIVE_CONSECUTIVE_IDENTICAL_LAYOUT"):
            return RootCauseHypothesis(
                cause_type=RootCauseType.SEMANTIC_LAYOUT_MAPPING,
                confidence=0.95,
                supporting_findings=(f,),
                affected_targets=tuple(targets),
                competing_hypotheses=(
                    (RootCauseType.CONTENT_DENSITY, 0.75),
                ),
                repairability=True,
                suggested_mutation_class=RepairMutationClass.CLASS_C_LAYOUT_REMAPPING,
                rationale="Slide or worksheet layout repeats monotonously; requires layout alternation or remap.",
            )

        elif code in ("COGNITIVE_OVERLOAD", "EXTREME_DENSE_PAGE"):
            return RootCauseHypothesis(
                cause_type=RootCauseType.CONTENT_DENSITY,
                confidence=0.93,
                supporting_findings=(f,),
                affected_targets=tuple(targets),
                repairability=True,
                suggested_mutation_class=RepairMutationClass.CLASS_B_COMPOSITION,
                rationale="Unit exceeds cognitive load limits or maximum card thresholds.",
            )

        # 3. Pedagogical & Inquiry Failures
        elif code in ("INQUIRY_ARC_BROKEN", "REFLECTION_BEFORE_OBSERVATION", "PREDICTION_AFTER_EXPLANATION"):
            return RootCauseHypothesis(
                cause_type=RootCauseType.INQUIRY_STRUCTURE,
                confidence=0.96,
                supporting_findings=(f,),
                affected_targets=tuple(targets),
                repairability=True,
                suggested_mutation_class=RepairMutationClass.CLASS_D_PEDAGOGICAL_STRUCTURE,
                rationale="Worksheet activities deviate from canonical inquiry learning arc.",
            )

        elif code in ("ANTI_SPOILING_BREACH", "EXPLANATION_LEAKED_BEFORE_PREDICTION", "ANSWER_LEAKED_INSIDE_QUESTION"):
            return RootCauseHypothesis(
                cause_type=RootCauseType.INQUIRY_STRUCTURE,
                confidence=0.98,
                supporting_findings=(f,),
                affected_targets=tuple(targets),
                repairability=True,
                suggested_mutation_class=RepairMutationClass.CLASS_D_PEDAGOGICAL_STRUCTURE,
                rationale="Explanatory answer leaked before student observation/prediction.",
            )

        elif code in ("INSUFFICIENT_WORKSPACE", "WORKSPACE_DETACHED"):
            return RootCauseHypothesis(
                cause_type=RootCauseType.GRID_GEOMETRY,
                confidence=0.88,
                supporting_findings=(f,),
                affected_targets=tuple(targets),
                repairability=True,
                suggested_mutation_class=RepairMutationClass.CLASS_A_GEOMETRY,
                rationale="Student response area missing or smaller than required pedagogical minimum.",
            )

        # 4. Scientific Integrity & Narrative Failures
        elif code in ("UNSUPPORTED_SCIENTIFIC_CLAIM", "CLAIM_WITHOUT_EVIDENCE"):
            return RootCauseHypothesis(
                cause_type=RootCauseType.EVIDENCE_MAPPING,
                confidence=0.91,
                supporting_findings=(f,),
                affected_targets=tuple(targets),
                repairability=True,
                suggested_mutation_class=RepairMutationClass.CLASS_E_SEMANTIC_INTEGRITY,
                rationale="Scientific claim lacks verified citation/evidence linkage in knowledge base.",
            )

        elif code in ("SCIENTIFIC_CITATION_INVISIBLE", "MISSING_CITATIONS", "CITATION_MARKER_MISSING"):
            from app.quality.repair.effectiveness.coverage_matrix import RootCauseCoverageMatrix
            ev = getattr(f, "evidence", {}) or {}
            subtype = RootCauseCoverageMatrix.classify_citation_invisible_subtype(ev)
            sub_cause, owning_layer, _ = RootCauseCoverageMatrix.resolve_citation_subtype_strategy(subtype)
            return RootCauseHypothesis(
                cause_type=sub_cause,
                confidence=0.95,
                supporting_findings=(f,),
                affected_targets=tuple(targets),
                competing_hypotheses=(
                    (RootCauseType.SOURCE_INSUFFICIENCY, 0.70),
                ),
                repairability=True,
                suggested_mutation_class=RepairMutationClass.CLASS_E_SEMANTIC_INTEGRITY,
                rationale=f"Scientific citation finding decomposed to subtype '{subtype.value}' (Owning Layer: {owning_layer}).",
            )

        elif code in ("MISATTRIBUTED_EVIDENCE", "EVIDENCE_ATTACHED_TO_WRONG_CLAIM"):
            return RootCauseHypothesis(
                cause_type=RootCauseType.EVIDENCE_MAPPING,
                confidence=0.92,
                supporting_findings=(f,),
                affected_targets=tuple(targets),
                repairability=True,
                suggested_mutation_class=RepairMutationClass.CLASS_E_SEMANTIC_INTEGRITY,
                rationale="Evidence unit linked to incorrect claim statement.",
            )

        elif code in ("SOURCE_CONTRADICTION", "CLAIM_CONTRADICTION"):
            return RootCauseHypothesis(
                cause_type=RootCauseType.SOURCE_INSUFFICIENCY,
                confidence=0.99,
                supporting_findings=(f,),
                affected_targets=tuple(targets),
                repairability=False,  # Unrepairable automatically! Must escalate
                suggested_mutation_class=RepairMutationClass.CLASS_F_NON_REPAIRABLE,
                rationale="Contradictory factual statements in source material cannot be resolved automatically.",
            )

        elif code in ("STRUCTURAL_HIERARCHY_INVERSION", "BAB_HIERARCHY_INVERSION", "SCIENTIFIC_METHODOLOGY_ORDER_INVERSION"):
            return RootCauseHypothesis(
                cause_type=RootCauseType.NARRATIVE_ORDER,
                confidence=0.92,
                supporting_findings=(f,),
                affected_targets=tuple(targets),
                repairability=True,
                suggested_mutation_class=RepairMutationClass.CLASS_D_PEDAGOGICAL_STRUCTURE,
                rationale="Document section or chapter ordering violates canonical structural rules.",
            )

        # Non-automatable coverage check: unknown finding code has zero generic fallback
        from app.quality.repair.effectiveness.coverage_matrix import RootCauseCoverageMatrix
        coverage = RootCauseCoverageMatrix.lookup(code, artifact_type)
        if coverage and coverage.is_automatable:
            return RootCauseHypothesis(
                cause_type=coverage.root_cause,
                confidence=0.85,
                supporting_findings=(f,),
                affected_targets=tuple(targets),
                repairability=True,
                suggested_mutation_class=coverage.mutation_class,
                rationale=coverage.rationale,
            )

        # Unclassified finding: strictly NON_AUTOMATABLE, no generic padding fallback
        return RootCauseHypothesis(
            cause_type=RootCauseType.UNKNOWN,
            confidence=0.50,
            supporting_findings=(f,),
            affected_targets=tuple(targets),
            repairability=False,  # Explicitly non-repairable
            suggested_mutation_class=RepairMutationClass.CLASS_F_NON_REPAIRABLE,
            rationale=f"Unclassified finding code '{code}' has no verified automated repair; routing to manual review.",
        )

    @classmethod
    def _extract_targets(cls, findings: List[QualityFinding], artifact_type: str) -> List[RepairTarget]:
        targets: List[RepairTarget] = []
        for f in findings:
            if f.affected_pages:
                for p in f.affected_pages:
                    targets.append(
                        RepairTarget(
                            artifact_type=artifact_type,
                            page_index=p,
                            slide_index=p if artifact_type.lower() == "presentation" else None,
                            source_knowledge_ids=tuple(f.evidence_refs),
                        )
                    )
            elif f.affected_elements:
                for el in f.affected_elements:
                    targets.append(
                        RepairTarget(
                            artifact_type=artifact_type,
                            element_id=el,
                            source_knowledge_ids=tuple(f.evidence_refs),
                        )
                    )
            else:
                targets.append(
                    RepairTarget(
                        artifact_type=artifact_type,
                        source_knowledge_ids=tuple(f.evidence_refs),
                    )
                )
        return targets
