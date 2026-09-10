"""
Universal Document Intelligence System V5 — Human-in-the-Loop Review Studio.

Phase 6: Governed Human Expert Decision Infrastructure.
Enforces epistemic separation (Observation -> Interpretation -> Decision -> Directive),
directive safety firewalls, independent review state machines, and immutable provenance.
"""

from app.review.contracts import (
    AdjudicationOutcome,
    CaseIdentity,
    DirectiveCategory,
    DirectiveType,
    DisagreementType,
    EpistemicStatus,
    EvidenceSufficiencyLevel,
    EvidenceSufficiencyResult,
    ExpertDecisionType,
    ReviewCase,
    ReviewConfidence,
    ReviewDecision,
    ReviewDirective,
    ReviewEvidencePackage,
    ReviewInterpretation,
    ReviewObservation,
    ReviewState,
    ReviewTrigger,
    ReviewabilityStatus,
    ReviewerCapability,
    ReviewerProfile,
)
from app.review.intake import ReviewIntakeRouter, ReviewabilityClassifier
from app.review.queue import (
    ExpertiseRouter,
    PriorityBand,
    ReviewPriorityModel,
    ReviewQueueRegistry,
)
from app.review.static_bundle import StaticReviewBundleGenerator
from app.review.evidence import (
    ArtifactSnapshotManager,
    EvidencePackageBuilder,
    EvidenceSufficiencyAnalyzer,
    ReviewLineageAdapter,
)
from app.review.decisions import (
    ConfidenceEvaluator,
    CounterfactualExplanation,
    ReviewDecisionEngine,
)
from app.review.safety import (
    AuthorityBoundaryGuard,
    DirectiveSafetyValidator,
    IllegalDirectiveException,
    SovereignAuthorityBypassAttemptError,
)
from app.review.governance import (
    AdjudicationManager,
    BlindReviewPolicy,
    CalibrationAssessment,
    DisagreementAnalyzer,
    ReviewerCalibrationEngine,
)
from app.review.provenance import (
    HashChainValidator,
    ReviewProvenanceEntry,
    ReviewProvenanceLedger,
)
from app.review.bridge import (
    BenchmarkCandidateProposal,
    BenchmarkGovernanceBridge,
    DirectiveRepairHint,
    ReviewRepairBridge,
)
from app.review.review_state import (
    IllegalReviewStateTransitionError,
    ReviewStateMachine,
    ReviewStateTransitionRecord,
)

__all__ = [
    # Contracts
    "ReviewState",
    "ReviewTrigger",
    "ReviewabilityStatus",
    "EpistemicStatus",
    "ReviewConfidence",
    "ExpertDecisionType",
    "DirectiveCategory",
    "DirectiveType",
    "EvidenceSufficiencyLevel",
    "DisagreementType",
    "AdjudicationOutcome",
    "ReviewerCapability",
    "CaseIdentity",
    "ReviewCase",
    "ReviewObservation",
    "ReviewInterpretation",
    "ReviewDecision",
    "ReviewDirective",
    "EvidenceSufficiencyResult",
    "ReviewEvidencePackage",
    "ReviewerProfile",
    # State Machine
    "ReviewStateMachine",
    "IllegalReviewStateTransitionError",
    "ReviewStateTransitionRecord",
    # Intake & Queue
    "ReviewabilityClassifier",
    "ReviewIntakeRouter",
    "PriorityBand",
    "ReviewPriorityModel",
    "ReviewQueueRegistry",
    "ExpertiseRouter",
    # Evidence
    "EvidenceSufficiencyAnalyzer",
    "ReviewLineageAdapter",
    "ArtifactSnapshotManager",
    "EvidencePackageBuilder",
    "StaticReviewBundleGenerator",
    # Decisions
    "ConfidenceEvaluator",
    "CounterfactualExplanation",
    "ReviewDecisionEngine",
    # Safety
    "DirectiveSafetyValidator",
    "AuthorityBoundaryGuard",
    "IllegalDirectiveException",
    "SovereignAuthorityBypassAttemptError",
    # Governance
    "BlindReviewPolicy",
    "DisagreementAnalyzer",
    "AdjudicationManager",
    "ReviewerCalibrationEngine",
    "CalibrationAssessment",
    # Provenance
    "HashChainValidator",
    "ReviewProvenanceEntry",
    "ReviewProvenanceLedger",
    # Bridges
    "DirectiveRepairHint",
    "ReviewRepairBridge",
    "BenchmarkCandidateProposal",
    "BenchmarkGovernanceBridge",
]
