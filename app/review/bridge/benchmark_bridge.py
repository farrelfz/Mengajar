"""
Universal Document Intelligence System V5 — Benchmark Governance Bridge.

Phase 6: Allows expert reviewers to propose reviewed edge-cases as Golden Corpus
candidates while strictly enforcing AntiLaunderingGuard rules against baseline descent.
"""

from __future__ import annotations

import time
import uuid
from enum import Enum
from typing import Any, Dict, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.benchmarking.governance import (
    AntiLaunderingGuard,
    BaselineMutationRecord,
    BenchmarkLaunderingAttemptError,
    ChangeClassification,
)


class BenchmarkProposalType(str, Enum):
    NEW_GOLDEN_CASE = "NEW_GOLDEN_CASE"
    NEW_ADVERSARIAL_CASE = "NEW_ADVERSARIAL_CASE"
    BASELINE_REVIEW_REQUEST = "BASELINE_REVIEW_REQUEST"
    VARIATION_POLICY_REVIEW = "VARIATION_POLICY_REVIEW"


class BenchmarkCandidateProposal(BaseModel):
    """Proposal contract submitted by an expert reviewer to Golden Corpus governance."""
    model_config = ConfigDict(frozen=True)

    proposal_id: str = Field(default_factory=lambda: f"bgp_{uuid.uuid4().hex[:8]}")
    case_id: str
    artifact_id: str
    artifact_type: str
    proposal_type: BenchmarkProposalType
    proposer_id: str
    rationale: str = Field(min_length=20)
    classification: ChangeClassification = ChangeClassification.CORPUS_EXPANSION
    previous_scores: Dict[str, float] = Field(default_factory=dict)
    proposed_scores: Dict[str, float] = Field(default_factory=dict)
    created_at: float = Field(default_factory=time.time)


class BenchmarkGovernanceBridge:
    """Safely mediates reviewer benchmark proposals to the Golden Corpus."""

    @classmethod
    def validate_and_submit_proposal(
        cls,
        proposal: BenchmarkCandidateProposal,
    ) -> Tuple[bool, Optional[BaselineMutationRecord], str]:
        """
        Validates proposal against AntiLaunderingGuard.
        Returns (is_accepted, mutation_record, explanation).
        """
        # If baseline scores are being modified, check that scores are not lowered
        for dim, prev_val in proposal.previous_scores.items():
            new_val = proposal.proposed_scores.get(dim)
            if new_val is not None and new_val < prev_val:
                raise BenchmarkLaunderingAttemptError(
                    f"Forbidden benchmark laundering attempt: Proposed score for dimension '{dim}' "
                    f"({new_val:.3f}) is lower than historical baseline ({prev_val:.3f})."
                )

        # Build mutation record
        record = BaselineMutationRecord(
            target_case_id=proposal.artifact_id,
            target_artifact_type=proposal.artifact_type,
            previous_baseline_reference=proposal.case_id,
            previous_scores=dict(proposal.previous_scores),
            new_scores=dict(proposal.proposed_scores),
            change_reason=proposal.rationale,
            expected_quality_impact=f"Proposal {proposal.proposal_type.value} submitted by {proposal.proposer_id}",
            change_classification=proposal.classification,
        )

        return True, record, "Benchmark proposal accepted and verified against anti-laundering governance."
