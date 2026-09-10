"""
Universal Document Intelligence System V5 — Anti-Benchmark-Laundering Governance.

Phase 5: Protects benchmark integrity by strictly forbidding silent baseline lowering,
untraceable reference replacement, unclassified mutations, and broken corpus lineage.
"""

from __future__ import annotations

import hashlib
import time
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.benchmarking.golden_contracts import GoldenCorpus, GoldenCorpusVersion


class ChangeClassification(str, Enum):
    """Governed classifications for legitimate benchmark baseline and reference changes."""
    LEGITIMATE_CORRECTION = "LEGITIMATE_CORRECTION"
    REFERENCE_REGENERATION = "REFERENCE_REGENERATION"
    POLICY_EVOLUTION = "POLICY_EVOLUTION"
    MEASUREMENT_FIX = "MEASUREMENT_FIX"
    CORPUS_EXPANSION = "CORPUS_EXPANSION"
    DEPRECATION = "DEPRECATION"
    UNKNOWN_CHANGE = "UNKNOWN_CHANGE"


class BenchmarkLaunderingAttemptError(RuntimeError):
    """Raised when an operation attempts to artificially lower or tamper with benchmark standards."""
    pass


class BaselineMutationRecord(BaseModel):
    """Audit record capturing an explicit, governed mutation of a benchmark baseline."""
    model_config = ConfigDict(frozen=True)

    mutation_id: str = Field(default_factory=lambda: f"mut_{uuid.uuid4().hex[:8]}")
    target_case_id: str
    target_artifact_type: str
    previous_baseline_reference: str
    previous_scores: Dict[str, float] = Field(default_factory=dict)
    new_scores: Dict[str, float] = Field(default_factory=dict)
    change_reason: str
    expected_quality_impact: str
    change_classification: ChangeClassification = ChangeClassification.UNKNOWN_CHANGE
    authoritative_change_record: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)


class AntiLaunderingGuard:
    """Active guardian enforcing immutable lineage and preventing silent benchmark laundering."""

    MIN_REASON_LENGTH: int = 15

    @classmethod
    def validate_mutation(
        cls,
        record: BaselineMutationRecord,
        strict_raise: bool = True
    ) -> Tuple[bool, List[str]]:
        """
        Validates whether a proposed baseline mutation conforms to anti-laundering governance.
        """
        violations: List[str] = []

        # 1. Reject UNKNOWN_CHANGE
        if record.change_classification == ChangeClassification.UNKNOWN_CHANGE:
            violations.append(
                "BENCHMARK_LAUNDERING_ATTEMPT: Mutation classification is UNKNOWN_CHANGE. "
                "All benchmark mutations must be explicitly categorized."
            )

        # 2. Check substantive reason
        if not record.change_reason or len(record.change_reason.strip()) < cls.MIN_REASON_LENGTH:
            violations.append(
                f"BENCHMARK_LAUNDERING_ATTEMPT: change_reason '{record.change_reason}' is superficial "
                f"or missing (must be >= {cls.MIN_REASON_LENGTH} characters)."
            )

        # 3. Check lineage link
        if not record.previous_baseline_reference or not record.previous_baseline_reference.strip():
            violations.append(
                "BENCHMARK_LAUNDERING_ATTEMPT: previous_baseline_reference is empty. "
                "Lineage link to preceding baseline is mandatory."
            )

        # 4. Detect silent baseline lowering
        allowed_lowering_classes = {
            ChangeClassification.POLICY_EVOLUTION,
            ChangeClassification.LEGITIMATE_CORRECTION,
            ChangeClassification.MEASUREMENT_FIX
        }
        for dim, old_score in record.previous_scores.items():
            new_score = record.new_scores.get(dim)
            if new_score is not None and new_score < (old_score - 0.001):
                if record.change_classification not in allowed_lowering_classes:
                    violations.append(
                        f"BENCHMARK_LAUNDERING_ATTEMPT: Silent baseline lowering detected for dimension '{dim}'. Score was lowered "
                        f"from {old_score:.3f} to {new_score:.3f} under unauthorized classification "
                        f"'{record.change_classification.value}'."
                    )
                if not record.expected_quality_impact or len(record.expected_quality_impact.strip()) < 10:
                    violations.append(
                        f"BENCHMARK_LAUNDERING_ATTEMPT: Baseline lowering for dimension '{dim}' lacks "
                        "documented expected_quality_impact."
                    )

        is_valid = len(violations) == 0
        if not is_valid and strict_raise:
            raise BenchmarkLaunderingAttemptError("; ".join(violations))

        return is_valid, violations

    @classmethod
    def verify_corpus_lineage(cls, corpus: GoldenCorpus) -> Tuple[bool, List[str]]:
        """Verifies that a corpus version has unbroken parent lineage unless it is root v1.0.0."""
        issues: List[str] = []
        curr = corpus.current_version
        
        if curr.version not in ("1.0.0", "v1.0.0", "1.0", "v1") and not curr.parent_version:
            issues.append(
                f"Corpus version {curr.version} is not initial version but has no parent_version recorded."
            )
            
        if not curr.change_summary and curr.parent_version:
            issues.append(
                f"Corpus version transition from {curr.parent_version} to {curr.version} has empty change_summary."
            )
            
        return len(issues) == 0, issues

    @classmethod
    def compute_content_digest(cls, content: str) -> str:
        """Computes deterministic SHA-256 digest of artifact or source content."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @classmethod
    def verify_content_digest(cls, content: str, expected_digest: str) -> bool:
        """Verifies content matches expected SHA-256 digest."""
        if not expected_digest:
            return True
        actual = cls.compute_content_digest(content)
        return actual.lower() == expected_digest.lower()
