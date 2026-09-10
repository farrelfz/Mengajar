"""
Universal Document Intelligence System V5 — Certification Engine.

Phase 5: Orchestrates policy and regression detection to produce the final BenchmarkEvaluation.
"""

import time
import uuid
from typing import Dict, Any, Optional

from app.benchmarking.golden_contracts import (
    GoldenArtifactReference,
    DimensionResult,
    BenchmarkEvaluation,
    CertificationDecision
)
from app.benchmarking.certification.policy import CertificationPolicy
from app.benchmarking.certification.regression_detector import RegressionDetector

class CertificationEngine:
    """Core engine evaluating benchmark signals and issuing certification decisions."""
    
    @classmethod
    def certify(
        cls,
        artifact_id: str,
        golden_reference: GoldenArtifactReference,
        corpus_version: str,
        dimension_results: Dict[str, DimensionResult],
        hard_invariant_results: Dict[str, bool],
        historical_baseline: Optional[Dict[str, float]] = None
    ) -> BenchmarkEvaluation:
        
        # 1. Detect regression
        regression_analysis = RegressionDetector.detect(dimension_results, historical_baseline)
        is_regression = regression_analysis.get("is_regression", False)
        
        # 2. Evaluate policy
        decision = CertificationPolicy.evaluate(
            dimension_results=dimension_results,
            hard_invariant_results=hard_invariant_results,
            is_regression=is_regression
        )
        
        # 3. Calculate overall alignment
        applicable_scores = [
            res.normalized_score for res in dimension_results.values() 
            if res.applicability > 0.0
        ]
        alignment = sum(applicable_scores) / len(applicable_scores) if applicable_scores else 0.0
        
        return BenchmarkEvaluation(
            evaluation_id=str(uuid.uuid4()),
            artifact_id=artifact_id,
            golden_reference_id=golden_reference.artifact_id,
            corpus_version=corpus_version,
            benchmark_protocol_version="1.0.0",
            dimension_results=dimension_results,
            hard_invariant_results=hard_invariant_results,
            variation_interpretations={
                dim: res.comparison_mode.value 
                for dim, res in dimension_results.items()
            },
            reference_alignment=alignment,
            regression_analysis=regression_analysis,
            certification_decision=decision,
            reproducibility_metadata={"timestamp": time.time()}
        )
