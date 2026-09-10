"""
Universal Document Intelligence System V5 — Quality Authority & Canonical Causal Contracts.

Phase 3A.2: Standardized, immutable canonical contracts for quality signals,
evidence references, lifecycle state machines, scope policies, and repair proposals.
"""

from __future__ import annotations

from app.quality.causal.taxonomy import (
    ArchitectureLayer,
    CanonicalFailureCategory,
    CanonicalFailureCode,
    CanonicalFailureDomain,
    CanonicalFailureSeverity,
    CanonicalRepairClass,
    CanonicalSeverity,
    CausalConfidence,
    CausalConfidenceLevel,
    DetectionConfidence,
    FailureScope,
    UnifiedDecisionStatus,
    get_codes_for_domain,
    get_domain_for_code,
    register_canonical_code,
)
from app.quality.causal.provenance import (
    EvidenceReference,
    EvidenceSourceType,
)
from app.quality.causal.contracts import (
    CanonicalFailure,
    CanonicalQualityAssessment,
    FailureCluster,
    QualityLocation,
    QualitySignal,
    QualitySnapshot,
    RootCauseHypothesis,
)
from app.quality.causal.scope import (
    ScopePolicy,
)
from app.quality.causal.lifecycle import (
    InvalidLifecycleTransitionError,
    QualitySignalLifecycleRecord,
    QualitySignalLifecycleState,
    SignalLifecycleStateMachine,
)
from app.quality.causal.repair_contract import (
    RepairProposal,
    RepairTransaction,
    RepairTransactionStatus,
)
from app.quality.causal.signal_normalization import (
    BaseSignalAdapter,
    CalibrationSignalAdapter,
    FidelitySignalAdapter,
    LegacyPresentationGateAdapter,
    QualitySignalNormalizer,
    RenderedSignalAdapter,
)

# Phase 3A.1 subsystems for backward compatibility
from app.quality.causal.failure_normalizer import FailureNormalizer
from app.quality.causal.evidence_collector import (
    CausalEvidenceCollector,
    MultiLayerEvidence,
)
from app.quality.causal.cause_catalog import CauseDefinition, CausalDefectCatalog
from app.quality.causal.confidence import CausalConfidenceEstimator
from app.quality.causal.scope_analyzer import ScopeAnalyzer
from app.quality.causal.failure_correlation import FailureCorrelationEngine
from app.quality.causal.repetition_analyzer import (
    ProgressionAwareRepetitionAnalyzer,
    RepetitionEvaluationResult,
)
from app.quality.causal.repair_authority import RepairAuthorityMatrix, RepairPolicyRule
from app.quality.causal.artifact_causes import ArtifactCausalRules
from app.quality.causal.attribution_engine import CausalAttributionEngine
from app.quality.causal.quality_authority import UnifiedQualityAuthority
from app.quality.causal.reporter import CausalQualityReporter

# Phase 3B Causal Attribution Subsystems
from app.quality.causal.config import CausalIntelligenceConfig, DEFAULT_CAUSAL_CONFIG
from app.quality.causal.context import QualityCorrelationContext
from app.quality.causal.correlation_graph import (
    CorrelationEdge,
    CorrelationGraph,
    CorrelationRelationshipType,
    CorrelationScoreBreakdown,
)
from app.quality.causal.correlation_engine import (
    CorrelationResult,
    FailureCorrelationEngine as SignalCorrelationEngine,
)
from app.quality.causal.cluster_builder import FailureClusterBuilder
from app.quality.causal.symptom_classifier import (
    FailureRole,
    FailureRoleAssignment,
    SymptomCauseClassifier,
)
from app.quality.causal.causal_taxonomy import (
    CausalArchitecturalLayer,
    CausalConfidenceLevel as Phase3BCausalConfidenceLevel,
    CausalDecision,
    HypothesisStatus,
    RootCauseCategory,
)
from app.quality.causal.causal_path import (
    CausalPath,
    CausalPathEdge,
    CausalPathNode,
)
from app.quality.causal.rules import (
    CausalRule,
    CausalRuleCatalog,
    CausalRuleMatch,
)
from app.quality.causal.evidence_scorer import (
    CausalConfidenceBreakdown,
    CausalEvidenceScorer,
)
from app.quality.causal.competing_analysis import (
    CompetingAnalysisResult,
    CompetingHypothesisAnalysisResult,
    CompetingHypothesisAnalyzer,
)
from app.quality.causal.validator_anomaly import ValidatorAnomalyDetector
from app.quality.causal.repair_readiness import (
    RepairAuthorityLevel,
    RepairReadinessAssessment,
    RepairReadinessAssessor,
)
from app.quality.causal.causal_engine import (
    CausalAnalysisResult,
    MasterCausalEngine,
)
from app.quality.causal.causal_reporter import CausalReporter

__all__ = [
    # Taxonomy
    "CanonicalFailureDomain",
    "CanonicalSeverity",
    "CanonicalFailureSeverity",
    "DetectionConfidence",
    "CausalConfidence",
    "CausalConfidenceLevel",
    "CanonicalFailureCode",
    "get_domain_for_code",
    "get_codes_for_domain",
    "register_canonical_code",
    "FailureScope",
    "ArchitectureLayer",
    "CanonicalRepairClass",
    "UnifiedDecisionStatus",
    "CanonicalFailureCategory",
    # Provenance
    "EvidenceSourceType",
    "EvidenceReference",
    # Contracts
    "QualityLocation",
    "QualitySignal",
    "QualitySnapshot",
    "RootCauseHypothesis",
    "FailureCluster",
    "CanonicalFailure",
    "CanonicalQualityAssessment",
    # Scope
    "ScopePolicy",
    # Lifecycle
    "QualitySignalLifecycleState",
    "QualitySignalLifecycleRecord",
    "SignalLifecycleStateMachine",
    "InvalidLifecycleTransitionError",
    # Repair Contract
    "RepairProposal",
    "RepairTransaction",
    "RepairTransactionStatus",
    # Signal Normalization
    "BaseSignalAdapter",
    "CalibrationSignalAdapter",
    "RenderedSignalAdapter",
    "LegacyPresentationGateAdapter",
    "FidelitySignalAdapter",
    "QualitySignalNormalizer",
    # Subsystems (Phase 3A.1 compatibility)
    "FailureNormalizer",
    "CausalEvidenceCollector",
    "MultiLayerEvidence",
    "CauseDefinition",
    "CausalDefectCatalog",
    "CausalConfidenceEstimator",
    "ScopeAnalyzer",
    "FailureCorrelationEngine",
    "ProgressionAwareRepetitionAnalyzer",
    "RepetitionEvaluationResult",
    "RepairAuthorityMatrix",
    "RepairPolicyRule",
    "ArtifactCausalRules",
    "CausalAttributionEngine",
    "UnifiedQualityAuthority",
    "CausalQualityReporter",
    # Phase 3B Exports
    "CausalIntelligenceConfig",
    "DEFAULT_CAUSAL_CONFIG",
    "QualityCorrelationContext",
    "CorrelationEdge",
    "CorrelationGraph",
    "CorrelationRelationshipType",
    "CorrelationScoreBreakdown",
    "CorrelationResult",
    "SignalCorrelationEngine",
    "FailureClusterBuilder",
    "FailureRole",
    "FailureRoleAssignment",
    "SymptomCauseClassifier",
    "CausalArchitecturalLayer",
    "Phase3BCausalConfidenceLevel",
    "CausalDecision",
    "HypothesisStatus",
    "RootCauseCategory",
    "CausalPath",
    "CausalPathEdge",
    "CausalPathNode",
    "CausalRule",
    "CausalRuleCatalog",
    "CausalRuleMatch",
    "CausalConfidenceBreakdown",
    "CausalEvidenceScorer",
    "CompetingAnalysisResult",
    "CompetingHypothesisAnalysisResult",
    "CompetingHypothesisAnalyzer",
    "ValidatorAnomalyDetector",
    "RepairAuthorityLevel",
    "RepairReadinessAssessment",
    "RepairReadinessAssessor",
    "CausalAnalysisResult",
    "MasterCausalEngine",
    "CausalReporter",
]
