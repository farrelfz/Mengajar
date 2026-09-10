"""
Universal Document Intelligence System V5 — Benchmark Certification Policy.

Phase 5: Defines the threshold rules for scoring certification.
"""

from typing import Dict
from app.benchmarking.golden_contracts import (
    DimensionResult,
    CertificationDecision,
    ExpectedInvariants
)

class CertificationPolicy:
    """Rules engine mapping dimension scores and invariants to a final certification."""
    
    # Minimum scores to not be considered an automatic failure
    MIN_DIMENSION_SCORE = 0.50
    EXCELLENT_THRESHOLD = 0.90
    ACCEPTABLE_THRESHOLD = 0.70

    @classmethod
    def evaluate(
        cls,
        dimension_results: Dict[str, DimensionResult],
        hard_invariant_results: Dict[str, bool],
        is_regression: bool = False
    ) -> CertificationDecision:
        """
        Evaluates the aggregated results and decides the final certification.
        """
        # 1. Hard Invariants are absolute blockers.
        for inv_name, passed in hard_invariant_results.items():
            if not passed:
                return CertificationDecision.BENCHMARK_INSUFFICIENT
                
        # 2. Regression overrides standard passing rules.
        if is_regression:
            return CertificationDecision.BENCHMARK_REGRESSION
            
        # 3. Calculate alignment
        applicable_scores = [
            res.normalized_score for res in dimension_results.values() 
            if res.applicability > 0.0
        ]
        
        if not applicable_scores:
            # If nothing was applicable, we can't certify it blindly.
            return CertificationDecision.MANUAL_BENCHMARK_REVIEW_REQUIRED
            
        avg_score = sum(applicable_scores) / len(applicable_scores)
        min_score = min(applicable_scores)
        
        # 4. Critical drop in any single dimension requires review or is insufficient
        if min_score < cls.MIN_DIMENSION_SCORE:
            return CertificationDecision.MANUAL_BENCHMARK_REVIEW_REQUIRED
            
        # 5. Threshold-based decisions
        if avg_score >= cls.EXCELLENT_THRESHOLD and min_score >= cls.ACCEPTABLE_THRESHOLD:
            return CertificationDecision.CERTIFIED_EXCELLENT
            
        if avg_score >= cls.ACCEPTABLE_THRESHOLD:
            # If the average is acceptable but there's a weak dimension, it's a warning
            if min_score < cls.ACCEPTABLE_THRESHOLD:
                return CertificationDecision.CERTIFIED_WITH_WARNINGS
            return CertificationDecision.CERTIFIED_ACCEPTABLE
            
        return CertificationDecision.CERTIFIED_WITH_WARNINGS
