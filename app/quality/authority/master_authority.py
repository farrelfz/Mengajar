"""
Universal Document Intelligence System V5 — Master Unified Quality Authority.

Phase 3A.1: Master authoritative quality intelligence engine consolidating 4
orthogonal truth layers (Semantic Integrity, Artifact Fidelity, Artifact Quality,
Physical Rendered Quality) into a single canonical UnifiedQualityReport.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional, Sequence, Tuple

from app.quality.adapters.calibration import CalibrationSignalAdapter
from app.quality.adapters.fidelity import FidelitySignalAdapter
from app.quality.adapters.legacy_document import LegacyDocumentQualitySignalAdapter
from app.quality.adapters.presentation import PresentationQualitySignalAdapter
from app.quality.adapters.rendered import RenderedQualitySignalAdapter
from app.quality.authority.correlation import FindingCorrelationEngine
from app.quality.authority.decision_engine import AuthoritativeDecisionEngine
from app.quality.authority.dimension_normalizer import QualityDimensionNormalizer
from app.quality.authority.profiles import get_profile_for_artifact
from app.quality.contracts.authority import UnifiedQualityReport
from app.quality.contracts.decisions import ExportDecision
from app.quality.contracts.provenance import QualityProvenanceGraph
from app.quality.contracts.signals import QualitySignal


class UnifiedQualityAuthority:
    """Master single source of truth for document quality decisions across all artifact types."""

    @classmethod
    def evaluate_artifact(
        cls,
        artifact_type: str,
        rendered_inspection: Any = None,
        calibration_report: Any = None,
        fidelity_report: Any = None,
        semantic_report: Any = None,
        legacy_report: Any = None,
        raw_signals: Optional[Sequence[QualitySignal]] = None,
    ) -> UnifiedQualityReport:
        norm_type = artifact_type.strip().upper()
        profile = get_profile_for_artifact(norm_type)

        # 1. Adapt and normalize signals from all heterogeneous sources
        signals: List[QualitySignal] = []
        if raw_signals:
            signals.extend(raw_signals)

        if rendered_inspection is not None:
            signals.extend(RenderedQualitySignalAdapter.adapt(rendered_inspection, artifact_type=norm_type))

        if calibration_report is not None:
            signals.extend(CalibrationSignalAdapter.adapt(calibration_report, artifact_type=norm_type))

        if fidelity_report is not None:
            signals.extend(FidelitySignalAdapter.adapt(fidelity_report, artifact_type=norm_type))

        if legacy_report is not None:
            signals.extend(LegacyDocumentQualitySignalAdapter.adapt(legacy_report, artifact_type=norm_type))

        if semantic_report is not None:
            # Semantic report can be adapted through legacy or calibration adapters
            signals.extend(CalibrationSignalAdapter.adapt(semantic_report, artifact_type=norm_type))

        # 2. Correlate co-occurring signals, discover clusters, and suppress double penalties
        findings, clusters = FindingCorrelationEngine.correlate_signals(signals)

        # 3. Compute dimension scores, truth layer scores, overall score, and detect degeneracy
        dim_scores, domain_scores, overall_score, degeneracy_info = QualityDimensionNormalizer.compute_dimension_scores(
            signals=signals,
            findings=findings,
            clusters=clusters,
            profile=profile,
        )

        # 4. Deterministically arbitrate authoritative decision
        decision = AuthoritativeDecisionEngine.arbitrate(
            artifact_type=norm_type,
            profile=profile,
            signals=signals,
            findings=findings,
            clusters=clusters,
            dim_scores=dim_scores,
            domain_scores=domain_scores,
            overall_score=overall_score,
            degeneracy_info=degeneracy_info,
        )

        # 5. Build full traceability provenance graph
        provenance = QualityProvenanceGraph()
        for sig in signals:
            provenance.record_signal(sig.model_dump(mode="json"))
        for cluster in clusters:
            provenance.record_cluster(cluster.cluster_id, [s.signal_id for s in cluster.contributing_signals])
        for fnd in findings:
            provenance.record_finding(fnd.model_dump(mode="json"))
        provenance.record_decision(decision.model_dump(mode="json"))

        # 6. Extract truth layer summary dictionaries
        semantic_integrity = {
            "score": domain_scores.get("semantic_integrity", 1.0),
            "dimensions": [
                dim_scores[d.value].model_dump(mode="json")
                for d in QualityDimensionNormalizer.LAYER_DIMENSIONS["semantic_integrity"]
            ],
        }
        artifact_fidelity = {
            "score": domain_scores.get("artifact_fidelity", 1.0),
            "dimensions": [
                dim_scores[d.value].model_dump(mode="json")
                for d in QualityDimensionNormalizer.LAYER_DIMENSIONS["artifact_fidelity"]
            ],
        }
        artifact_quality = {
            "score": domain_scores.get("artifact_quality", 1.0),
            "dimensions": [
                dim_scores[d.value].model_dump(mode="json")
                for d in QualityDimensionNormalizer.LAYER_DIMENSIONS["artifact_quality"]
            ],
        }
        rendered_quality = {
            "score": domain_scores.get("rendered_quality", 1.0),
            "dimensions": [
                dim_scores[d.value].model_dump(mode="json")
                for d in QualityDimensionNormalizer.LAYER_DIMENSIONS["rendered_quality"]
            ],
        }

        # 7. Construct and return canonical UnifiedQualityReport
        return UnifiedQualityReport(
            artifact_type=norm_type,
            decision=decision.decision,
            can_export=decision.can_export,
            repair_required=decision.repair_required,
            overall_quality_score=overall_score,
            domain_scores=domain_scores,
            semantic_integrity=semantic_integrity,
            artifact_fidelity=artifact_fidelity,
            artifact_quality=artifact_quality,
            rendered_quality=rendered_quality,
            dimension_scores=dim_scores,
            findings=findings,
            finding_clusters=clusters,
            causal_diagnoses=tuple(
                {"cluster_id": c.cluster_id, "rationale": c.rationale, "severity": c.severity.value}
                for c in clusters
            ),
            score_distribution={dim: ds.score for dim, ds in dim_scores.items()},
            provenance=provenance,
            hard_blockers=decision.hard_blockers,
            warnings=decision.warnings,
            summary=decision.rationale,
        )
