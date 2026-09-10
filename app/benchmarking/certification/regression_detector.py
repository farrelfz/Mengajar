"""
Universal Document Intelligence System V5 — Benchmark Regression Detector.

Phase 5: Detects quality degradation against historical baselines.
Hardened with dimension-aware noise tolerances, confidence gating, and granular regression severity levels.
"""

from enum import Enum
from typing import Dict, Any, Optional
from app.benchmarking.golden_contracts import DimensionResult


class RegressionSeverity(str, Enum):
    """Categorical classification of regression magnitude."""
    NO_REGRESSION = "NO_REGRESSION"
    MINOR_VARIATION = "MINOR_VARIATION"                  # Drop <= dimension tolerance
    INSUFFICIENT_CONFIDENCE = "INSUFFICIENT_CONFIDENCE"  # Drop observed but confidence < 0.80
    DIMENSION_REGRESSION = "DIMENSION_REGRESSION"        # Single dimension drop > tolerance
    SIGNIFICANT_REGRESSION = "SIGNIFICANT_REGRESSION"    # Drop > 0.15 or multiple dimensions
    CRITICAL_REGRESSION = "CRITICAL_REGRESSION"          # Zero-tolerance dimension drop (e.g. citations)
    INVARIANT_REGRESSION = "INVARIANT_REGRESSION"        # Previously satisfied hard invariant now fails


class RegressionDetector:
    """Detects statistically significant regressions in benchmark performance."""
    
    # Default minimum score drop required to trigger a regression (filters out noise)
    DEFAULT_NOISE_THRESHOLD = 0.05
    MIN_CONFIDENCE_FOR_REGRESSION = 0.80

    # Dimension-aware tolerances: Visual is more flexible, Citation/Factuality is zero-tolerance
    DIMENSION_NOISE_THRESHOLDS: Dict[str, float] = {
        "VISUAL": 0.08,
        "PHYSICAL_RENDER": 0.08,
        "STRUCTURAL": 0.06,
        "SEMANTIC": 0.05,
        "PEDAGOGICAL": 0.04,
        "SCIENTIFIC": 0.00,  # Zero-tolerance for evidence/citation regression
        "FACTUAL_GROUNDING": 0.00,
        "SAFETY_INVARIANTS": 0.00,
    }

    @classmethod
    def detect(
        cls,
        current_results: Dict[str, DimensionResult],
        historical_baseline: Optional[Dict[str, float]]
    ) -> Dict[str, Any]:
        """
        Compares current dimension results to a historical baseline with dimension-aware tolerances.
        
        Args:
            current_results: Mapping of dimension name to its DimensionResult.
            historical_baseline: Mapping of dimension name to historical normalized score.
            
        Returns:
            Dict containing regression flags, severity classification, and granular details.
        """
        if not historical_baseline:
            return {
                "is_regression": False,
                "severity": RegressionSeverity.NO_REGRESSION.value,
                "details": {}
            }
            
        details = {}
        is_regression = False
        max_drop = 0.0
        critical_hit = False
        insufficient_confidence_count = 0
        
        for dim_name, current_res in current_results.items():
            if current_res.applicability == 0.0:
                continue
                
            historical_score = historical_baseline.get(dim_name)
            if historical_score is None:
                continue
                
            drop = round(historical_score - current_res.normalized_score, 4)
            threshold = cls.DIMENSION_NOISE_THRESHOLDS.get(dim_name.upper(), cls.DEFAULT_NOISE_THRESHOLD)
            
            # Check drop against dimension-specific tolerance
            if drop > threshold:
                if current_res.confidence < cls.MIN_CONFIDENCE_FOR_REGRESSION:
                    insufficient_confidence_count += 1
                else:
                    is_regression = True
                    details[dim_name] = {
                        "historical": historical_score,
                        "current": current_res.normalized_score,
                        "drop": drop,
                        "tolerance": threshold,
                        "confidence": current_res.confidence
                    }
                    if drop > max_drop:
                        max_drop = drop
                    if threshold == 0.00:
                        critical_hit = True

        # Assign Severity Classification
        if critical_hit:
            severity = RegressionSeverity.CRITICAL_REGRESSION
        elif max_drop > 0.15 or len(details) >= 2:
            severity = RegressionSeverity.SIGNIFICANT_REGRESSION
        elif is_regression:
            severity = RegressionSeverity.DIMENSION_REGRESSION
        elif insufficient_confidence_count > 0:
            severity = RegressionSeverity.INSUFFICIENT_CONFIDENCE
        elif max_drop > 0.0:
            severity = RegressionSeverity.MINOR_VARIATION
        else:
            severity = RegressionSeverity.NO_REGRESSION
                
        return {
            "is_regression": is_regression,
            "severity": severity.value,
            "details": details
        }
