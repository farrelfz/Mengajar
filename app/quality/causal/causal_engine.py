"""
Universal Document Intelligence System V5 — Master Causal Attribution Engine.

Phase 3B: End-to-end integration orchestrating signal correlation, cluster building,
symptom vs cause classification, multi-hypothesis generation, evidence scoring,
competing hypothesis analysis, validator anomaly detection, and repair readiness assessment.

STRICT CONTRACT INVARIANT:
This engine NEVER executes any repair. It is strictly read-only and analytical.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Sequence, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.quality.causal.causal_path import CausalPath, CausalPathNode
from app.quality.causal.causal_taxonomy import (
    CausalArchitecturalLayer,
    CausalConfidenceLevel,
    CausalDecision,
    HypothesisStatus,
    RootCauseCategory,
)
from app.quality.causal.cluster_builder import FailureClusterBuilder
from app.quality.causal.competing_analysis import CompetingAnalysisResult, CompetingHypothesisAnalyzer
from app.quality.causal.config import CausalIntelligenceConfig, DEFAULT_CAUSAL_CONFIG
from app.quality.causal.contracts import FailureCluster, QualitySignal, RootCauseHypothesis
from app.quality.causal.correlation_engine import CorrelationResult, FailureCorrelationEngine
from app.quality.causal.correlation_graph import CorrelationGraph
from app.quality.causal.evidence_scorer import CausalEvidenceScorer
from app.quality.causal.lifecycle import (
    QualitySignalLifecycleRecord,
    QualitySignalLifecycleState,
    SignalLifecycleStateMachine,
)
from app.quality.causal.repair_readiness import (
    RepairAuthorityLevel,
    RepairReadinessAssessment,
    RepairReadinessAssessor,
)
from app.quality.causal.rules import CausalRuleCatalog, CausalRuleMatch
from app.quality.causal.scope import ScopePolicy
from app.quality.causal.symptom_classifier import FailureRoleAssignment, SymptomCauseClassifier
from app.quality.causal.taxonomy import CanonicalRepairClass, FailureScope
from app.quality.causal.validator_anomaly import ValidatorAnomalyDetector


class CausalAnalysisResult(BaseModel):
    """Authoritative, explainable outcome of the Phase 3B Causal Attribution Engine."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    clusters: Tuple[FailureCluster, ...] = Field(default_factory=tuple)
    correlation_graph: CorrelationGraph
    readiness_assessments: Dict[str, RepairReadinessAssessment] = Field(default_factory=dict)
    competing_results: Dict[str, CompetingAnalysisResult] = Field(default_factory=dict)
    signal_lifecycle_records: Dict[str, QualitySignalLifecycleRecord] = Field(default_factory=dict)
    total_signals: int = 0
    correlated_pairs_count: int = 0
    clusters_count: int = 0
    unattributed_signals: Tuple[str, ...] = Field(default_factory=tuple)
    summary: str = ""
    timestamp: float = Field(default_factory=time.time)


class MasterCausalEngine:
    """Master causal attribution pipeline executing complete Phase 3B intelligence workflow."""

    def __init__(
        self,
        config: Optional[CausalIntelligenceConfig] = None,
        rule_catalog: Optional[CausalRuleCatalog] = None,
        scope_policy: Optional[ScopePolicy] = None,
    ):
        self.config = config or DEFAULT_CAUSAL_CONFIG
        self.rule_catalog = rule_catalog or CausalRuleCatalog()
        self.scope_policy = scope_policy or ScopePolicy()

        # Engine subcomponents
        self.correlation_engine = FailureCorrelationEngine(config=self.config)
        self.cluster_builder = FailureClusterBuilder(config=self.config, scope_policy=self.scope_policy)
        self.evidence_scorer = CausalEvidenceScorer(config=self.config)
        self.competing_analyzer = CompetingHypothesisAnalyzer(config=self.config)
        self.repair_assessor = RepairReadinessAssessor()
        self.anomaly_detector = ValidatorAnomalyDetector()

    def analyze(
        self,
        signals: Sequence[QualitySignal],
        total_pages: int = 1,
        artifact_type: str = "UNKNOWN",
    ) -> CausalAnalysisResult:
        """Executes the full Phase 3B causal attribution workflow."""
        if not signals:
            empty_graph = CorrelationGraph()
            return CausalAnalysisResult(
                clusters=(),
                correlation_graph=empty_graph,
                readiness_assessments={},
                competing_results={},
                signal_lifecycle_records={},
                total_signals=0,
                correlated_pairs_count=0,
                clusters_count=0,
                unattributed_signals=(),
                summary="Clean artifact: zero quality signals detected.",
            )

        # 1. Initialize signal lifecycles
        lifecycle_records: Dict[str, QualitySignalLifecycleRecord] = {}
        for s in signals:
            rec = SignalLifecycleStateMachine.create_initial(s.signal_id)
            rec = SignalLifecycleStateMachine.transition(
                rec, QualitySignalLifecycleState.NORMALIZED, rationale="QualitySignal normalized into causal pipeline"
            )
            lifecycle_records[s.signal_id] = rec

        # 2. Correlate signals across 5 dimensions
        correlation_result: CorrelationResult = self.correlation_engine.correlate(signals)
        correlation_graph = correlation_result.graph

        # Update lifecycle to CORRELATED for correlated signals
        for edge in correlation_result.correlation_edges:
            for sid in (edge.signal_a_id, edge.signal_b_id):
                rec = lifecycle_records.get(sid)
                if rec and rec.current_state == QualitySignalLifecycleState.NORMALIZED:
                    lifecycle_records[sid] = SignalLifecycleStateMachine.transition(
                        rec, QualitySignalLifecycleState.CORRELATED, rationale=f"Correlated with score {edge.score:.2f}"
                    )

        # 3. Construct clusters from connected components
        preliminary_clusters: List[FailureCluster] = self.cluster_builder.build_clusters(
            correlation_result=correlation_result,
            total_pages=total_pages,
            artifact_type=artifact_type,
        )

        # Update lifecycle to CLUSTERED
        for clust in preliminary_clusters:
            for s in clust.signals:
                rec = lifecycle_records.get(s.signal_id)
                if rec and rec.current_state in (QualitySignalLifecycleState.NORMALIZED, QualitySignalLifecycleState.CORRELATED):
                    lifecycle_records[s.signal_id] = SignalLifecycleStateMachine.transition(
                        rec, QualitySignalLifecycleState.CLUSTERED, rationale=f"Grouped into cluster {clust.cluster_id}"
                    )

        finalized_clusters: List[FailureCluster] = []
        readiness_assessments: Dict[str, RepairReadinessAssessment] = {}
        competing_results: Dict[str, CompetingAnalysisResult] = {}
        unattributed: List[str] = []

        # 4. Analyze each cluster independently
        for cluster in preliminary_clusters:
            # a. Classify roles (primary symptoms vs causes)
            role_assignments: List[FailureRoleAssignment] = SymptomCauseClassifier.classify_cluster_signals(cluster)

            # b. Rule matching
            matches: List[CausalRuleMatch] = self.rule_catalog.match(cluster, artifact_type=artifact_type)

            hypotheses: List[RootCauseHypothesis] = []

            # c. Formulate hypotheses from matches
            for rank, match in enumerate(matches, start=1):
                rule = match.rule

                # Format explainable causal path
                path_str = ""
                if rule.causal_path_template:
                    path = CausalPath.from_steps(rule.causal_path_template)
                    path_str = path.format_chain()
                else:
                    path_str = f"{rule.architectural_layer.value} -> {rule.candidate_root_cause.value}"

                # Score evidence
                score, conf_level, breakdown, ev_notes = self.evidence_scorer.score_hypothesis(
                    cluster=cluster,
                    candidate_layer=rule.architectural_layer,
                    explains_signal_count=len(match.matched_signal_ids),
                    base_match_score=match.match_score,
                    competition_count=max(0, len(matches) - 1),
                )

                supporting = match.supporting_evidence + ev_notes

                hyp = RootCauseHypothesis(
                    cause_code=rule.candidate_root_cause.value,
                    cause_layer=rule.architectural_layer.value,
                    confidence_score=score,
                    confidence_level=conf_level.value,
                    supporting_evidence=supporting,
                    contradicting_evidence=(),
                    affected_scope=cluster.scope,
                    repair_authority=rule.architectural_layer.value,
                    confidence_components=breakdown.to_dict(),
                    causal_path=path_str,
                    status=HypothesisStatus.CANDIDATE.value,
                    explains_signal_ids=match.matched_signal_ids,
                    alternative_rank=rank,
                )
                hypotheses.append(hyp)

            # d. Check for validator anomaly
            anomaly_hyp = self.anomaly_detector.detect_anomaly_hypothesis(cluster)
            if anomaly_hyp:
                hypotheses.append(anomaly_hyp)

            # e. Fallback hypothesis if no rules matched
            if not hypotheses:
                dom_symptom = cluster.symptoms[0].value if cluster.symptoms else "UNKNOWN_DEFECT"
                fallback_layer = CausalArchitecturalLayer.BLUEPRINT
                if any(s.failure_domain.value == "PHYSICAL_RENDER" for s in cluster.signals):
                    fallback_layer = CausalArchitecturalLayer.RENDERING

                score, conf_level, breakdown, ev_notes = self.evidence_scorer.score_hypothesis(
                    cluster=cluster,
                    candidate_layer=fallback_layer,
                    explains_signal_count=len(cluster.signals),
                    base_match_score=0.40,
                )

                hyp = RootCauseHypothesis(
                    cause_code=RootCauseCategory.UNKNOWN_CAUSE.value,
                    cause_layer=fallback_layer.value,
                    confidence_score=score,
                    confidence_level=conf_level.value,
                    supporting_evidence=(f"Fallback heuristic for unclassified symptoms: {dom_symptom}",),
                    contradicting_evidence=(),
                    affected_scope=cluster.scope,
                    repair_authority=fallback_layer.value,
                    confidence_components=breakdown.to_dict(),
                    causal_path=f"{fallback_layer.value} -> UNKNOWN_CAUSE",
                    status=HypothesisStatus.CANDIDATE.value,
                    explains_signal_ids=tuple(s.signal_id for s in cluster.signals),
                    alternative_rank=1,
                )
                hypotheses.append(hyp)

            # f. Evaluate competing hypotheses & ambiguity
            competing_result = self.competing_analyzer.analyze(hypotheses)
            competing_results[cluster.cluster_id] = competing_result

            # g. Assess repair readiness
            readiness = self.repair_assessor.assess(cluster, competing_result, total_pages=total_pages)
            readiness_assessments[cluster.cluster_id] = readiness

            # h. Update signal lifecycle to CAUSAL_HYPOTHESIS
            for s in cluster.signals:
                rec = lifecycle_records.get(s.signal_id)
                if rec and rec.current_state == QualitySignalLifecycleState.CLUSTERED:
                    lifecycle_records[s.signal_id] = SignalLifecycleStateMachine.transition(
                        rec,
                        QualitySignalLifecycleState.CAUSAL_HYPOTHESIS,
                        rationale=f"Causal decision: {competing_result.decision.value}",
                        failure_code=s.failure_code.value,
                    )

            # Track unattributed signals if decision is INSUFFICIENT_EVIDENCE
            if competing_result.decision == CausalDecision.INSUFFICIENT_EVIDENCE:
                for s in cluster.signals:
                    unattributed.append(s.signal_id)

            # i. Finalize cluster with causal outputs
            final_cluster = FailureCluster(
                cluster_id=cluster.cluster_id,
                affected_pages=cluster.affected_pages,
                symptoms=cluster.symptoms,
                signals=cluster.signals,
                scope=cluster.scope,
                dominant_failure_patterns=cluster.dominant_failure_patterns,
                affected_locations=cluster.affected_locations,
                shared_context=cluster.shared_context,
                correlation_strength=cluster.correlation_strength,
                cluster_summary=cluster.cluster_summary,
                cluster_evidence=cluster.cluster_evidence,
                primary_root_cause=competing_result.primary_hypothesis,
                alternative_hypotheses=competing_result.alternative_hypotheses,
                is_ambiguous=competing_result.is_ambiguous,
                recommended_repair_class=readiness.recommended_action_class,
                rationale=competing_result.rationale,
                causal_decision=competing_result.decision.value,
            )
            finalized_clusters.append(final_cluster)

        # Build comprehensive summary
        summary = (
            f"Causal Analysis completed: {len(signals)} signals partitioned into {len(finalized_clusters)} clusters. "
            f"Decisions: {sum(1 for r in competing_results.values() if r.decision == CausalDecision.ROOT_CAUSE_CONFIRMED)} confirmed, "
            f"{sum(1 for r in competing_results.values() if r.decision == CausalDecision.ROOT_CAUSE_LIKELY)} likely, "
            f"{sum(1 for r in competing_results.values() if r.decision == CausalDecision.MULTIPLE_PLAUSIBLE_CAUSES)} ambiguous, "
            f"{sum(1 for r in competing_results.values() if r.decision == CausalDecision.VALIDATOR_ANOMALY_SUSPECTED)} validator anomalies."
        )

        return CausalAnalysisResult(
            clusters=tuple(finalized_clusters),
            correlation_graph=correlation_graph,
            readiness_assessments=readiness_assessments,
            competing_results=competing_results,
            signal_lifecycle_records=lifecycle_records,
            total_signals=len(signals),
            correlated_pairs_count=len(correlation_result.correlation_edges),
            clusters_count=len(finalized_clusters),
            unattributed_signals=tuple(unattributed),
            summary=summary,
        )
