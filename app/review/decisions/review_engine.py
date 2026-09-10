"""
Universal Document Intelligence System V5 — Review Decision Engine.

Phase 6: Validates and commits structured human decisions, enforcing
epistemic checks, evidence references, and state machine transitions.
"""

from __future__ import annotations

import time
from typing import List, Optional, Tuple

from app.review.contracts.enums import (
    EvidenceSufficiencyLevel,
    ExpertDecisionType,
    ReviewState,
)
from app.review.contracts.evidence import ReviewEvidencePackage
from app.review.contracts.review_case import ReviewCase
from app.review.contracts.review_decision import ReviewDecision
from app.review.decisions.confidence import ConfidenceEvaluator
from app.review.review_state import ReviewStateMachine


class ReviewDecisionEngine:
    """Validates and processes expert determinations into ReviewCases."""

    @classmethod
    def validate_decision(
        cls,
        decision: ReviewDecision,
        evidence_package: Optional[ReviewEvidencePackage] = None,
    ) -> Tuple[bool, List[str]]:
        """Validates epistemic consistency, evidence links, and completeness."""
        violations: List[str] = []

        # 1. Rationale checks
        if len(decision.rationale.strip()) < 20:
            violations.append("Decision rationale must be at least 20 characters long.")

        # 2. Evidence sufficiency vs confidence
        if evidence_package:
            justified, note = ConfidenceEvaluator.audit_confidence(
                confidence=decision.confidence,
                sufficiency=evidence_package.sufficiency.overall_sufficiency,
            )
            if not justified:
                violations.append(note)

            # Check observation evidence references
            known_finding_ids = {f.get("finding_id") for f in evidence_package.findings}
            known_signal_ids = {s.get("signal_id") for s in evidence_package.signals}
            for obs in decision.observations:
                for ref_id in obs.referenced_evidence_ids:
                    if ref_id not in known_finding_ids and ref_id not in known_signal_ids:
                        violations.append(f"Observation references unknown evidence ID '{ref_id}'.")

        # 3. Directive consistency
        for d in decision.directives:
            if len(d.rationale.strip()) < 10:
                violations.append(f"Directive '{d.directive_type.value}' has insufficient rationale (< 10 chars).")

        return len(violations) == 0, violations

    @classmethod
    def apply_decision(
        cls,
        case: ReviewCase,
        decision: ReviewDecision,
        evidence_package: Optional[ReviewEvidencePackage] = None,
    ) -> Tuple[bool, ReviewCase, List[str]]:
        """Validates and applies an expert decision to a ReviewCase."""
        is_valid, errors = cls.validate_decision(decision, evidence_package)
        if not is_valid:
            return False, case, errors

        sm = ReviewStateMachine(initial_state=case.current_state)

        # Transition logic based on decision type and directives
        target_state: ReviewState
        if decision.decision_type == ExpertDecisionType.ESCALATE_TO_SPECIALIST:
            target_state = ReviewState.ESCALATED
        elif decision.directives:
            target_state = ReviewState.DIRECTIVE_PROPOSED
        elif case.current_state == ReviewState.ADJUDICATION:
            target_state = ReviewState.RESOLVED
        elif decision.decision_type == ExpertDecisionType.DISPUTE_FALSE_POSITIVE:
            target_state = ReviewState.AWAITING_SECOND_REVIEW
        else:
            target_state = ReviewState.UNDER_REVIEW

        try:
            sm.transition(target_state, actor_id=decision.reviewer_id, reason=decision.decision_type.value)
        except Exception as e:
            return False, case, [f"State transition error: {str(e)}"]

        updated_decisions = list(case.decisions) + [decision]
        updated_case = case.model_copy(
            update={
                "current_state": target_state,
                "decisions": tuple(updated_decisions),
                "updated_at": time.time(),
            }
        )

        return True, updated_case, []
