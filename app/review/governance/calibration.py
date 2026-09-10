"""
Universal Document Intelligence System V5 — Reviewer Calibration Engine.

Phase 6: Empirical evaluation of reviewer reliability using blind golden benchmarks.
Tracks leniency and harshness biases non-punitively.
"""

from __future__ import annotations

import time
from typing import Dict, List, Optional, Sequence
from pydantic import BaseModel, ConfigDict, Field

from app.review.contracts.enums import ExpertDecisionType
from app.review.contracts.review_decision import ReviewDecision
from app.review.contracts.reviewer import ReviewerProfile


class CalibrationAssessment(BaseModel):
    """Empirical calibration metrics for an expert reviewer."""
    model_config = ConfigDict(frozen=True)

    reviewer_id: str
    total_golden_cases: int
    correct_count: int
    false_positives: int
    false_negatives: int
    accuracy: float = Field(ge=0.0, le=1.0)
    precision: float = Field(ge=0.0, le=1.0)
    recall: float = Field(ge=0.0, le=1.0)
    leniency_index: float  # > 0 indicates overlooking real defects
    harshness_index: float  # > 0 indicates disputing valid documents
    calibration_score: float = Field(ge=0.0, le=1.0)
    is_qualified: bool = True
    assessed_at: float = Field(default_factory=time.time)


class ReviewerCalibrationEngine:
    """Evaluates reviewer decision history against canonical ground-truth cases."""

    @classmethod
    def evaluate_reviewer(
        cls,
        reviewer: ReviewerProfile,
        golden_case_outcomes: Sequence[Dict[str, Any]],  # List of {"decision": DecisionType, "ground_truth": DecisionType}
    ) -> CalibrationAssessment:
        if not golden_case_outcomes:
            return CalibrationAssessment(
                reviewer_id=reviewer.reviewer_id,
                total_golden_cases=0,
                correct_count=0,
                false_positives=0,
                false_negatives=0,
                accuracy=reviewer.calibration_score,
                precision=1.0,
                recall=1.0,
                leniency_index=0.0,
                harshness_index=0.0,
                calibration_score=reviewer.calibration_score,
                is_qualified=reviewer.calibration_score >= 0.85,
            )

        total = len(golden_case_outcomes)
        correct = 0
        fp = 0
        fn = 0

        for item in golden_case_outcomes:
            actual = item.get("decision")
            expected = item.get("ground_truth")

            if actual == expected:
                correct += 1
            elif actual == ExpertDecisionType.DISPUTE_FALSE_POSITIVE and expected == ExpertDecisionType.CONFIRM_DEFECT:
                # Reviewer excused a real defect -> Leniency / False Negative
                fn += 1
            elif actual == ExpertDecisionType.CONFIRM_DEFECT and expected == ExpertDecisionType.DISPUTE_FALSE_POSITIVE:
                # Reviewer falsely flagged a valid document -> Harshness / False Positive
                fp += 1
            else:
                fn += 1

        acc = correct / float(total)
        prec = (correct / float(correct + fp)) if (correct + fp) > 0 else 0.0
        rec = (correct / float(correct + fn)) if (correct + fn) > 0 else 0.0
        cal_score = round(0.5 * acc + 0.25 * prec + 0.25 * rec, 3)

        leniency = round(fn / float(total), 3)
        harshness = round(fp / float(total), 3)

        return CalibrationAssessment(
            reviewer_id=reviewer.reviewer_id,
            total_golden_cases=total,
            correct_count=correct,
            false_positives=fp,
            false_negatives=fn,
            accuracy=round(acc, 3),
            precision=round(prec, 3),
            recall=round(rec, 3),
            leniency_index=leniency,
            harshness_index=harshness,
            calibration_score=cal_score,
            is_qualified=cal_score >= 0.85,
        )
