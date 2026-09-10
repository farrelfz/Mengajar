"""
Tests for Phase 4 Benchmark Certification Engine.
"""

import pytest
from app.benchmarking.golden_contracts import (
    DimensionResult,
    VariationPolicy,
    CertificationDecision,
    ExpectedInvariants,
    GoldenArtifactReference
)
from app.benchmarking.certification import (
    CertificationPolicy,
    RegressionDetector,
    CertificationEngine
)

@pytest.fixture
def base_dimension_results():
    return {
        "SEMANTIC": DimensionResult(
            dimension="SEMANTIC",
            raw_measurements={},
            normalized_score=0.95,
            confidence=0.9,
            applicability=1.0,
            comparison_mode=VariationPolicy.EXACT
        ),
        "VISUAL": DimensionResult(
            dimension="VISUAL",
            raw_measurements={},
            normalized_score=0.80,
            confidence=0.9,
            applicability=1.0,
            comparison_mode=VariationPolicy.TOLERANT
        )
    }

@pytest.fixture
def base_invariants():
    return {
        "no_fabricated_claims": True,
        "no_unsupported_evidence": True,
        "no_text_clipping": True
    }

def test_policy_excellent(base_dimension_results, base_invariants):
    base_dimension_results["VISUAL"] = DimensionResult(
        dimension="VISUAL", raw_measurements={}, normalized_score=0.95,
        confidence=0.9, applicability=1.0, comparison_mode=VariationPolicy.TOLERANT
    )
    decision = CertificationPolicy.evaluate(base_dimension_results, base_invariants)
    assert decision == CertificationDecision.CERTIFIED_EXCELLENT

def test_policy_hard_blocker(base_dimension_results, base_invariants):
    # Perfect scores but failed invariant
    base_invariants["no_fabricated_claims"] = False
    decision = CertificationPolicy.evaluate(base_dimension_results, base_invariants)
    assert decision == CertificationDecision.BENCHMARK_INSUFFICIENT

def test_policy_critical_drop(base_dimension_results, base_invariants):
    # One dimension drops below minimum (0.50)
    base_dimension_results["VISUAL"] = DimensionResult(
        dimension="VISUAL", raw_measurements={}, normalized_score=0.40,
        confidence=0.9, applicability=1.0, comparison_mode=VariationPolicy.TOLERANT
    )
    decision = CertificationPolicy.evaluate(base_dimension_results, base_invariants)
    assert decision == CertificationDecision.MANUAL_BENCHMARK_REVIEW_REQUIRED

def test_regression_detector_noise_filter():
    current = {
        "SEMANTIC": DimensionResult(
            dimension="SEMANTIC", raw_measurements={}, normalized_score=0.88,
            confidence=0.9, applicability=1.0, comparison_mode=VariationPolicy.EXACT
        )
    }
    baseline = {"SEMANTIC": 0.90} # Drop of 0.02 is below noise threshold (0.05)
    
    analysis = RegressionDetector.detect(current, baseline)
    assert analysis["is_regression"] is False

def test_regression_detector_true_regression():
    current = {
        "SEMANTIC": DimensionResult(
            dimension="SEMANTIC", raw_measurements={}, normalized_score=0.80,
            confidence=0.9, applicability=1.0, comparison_mode=VariationPolicy.EXACT
        )
    }
    baseline = {"SEMANTIC": 0.90} # Drop of 0.10 is above 0.05 threshold
    
    analysis = RegressionDetector.detect(current, baseline)
    assert analysis["is_regression"] is True
    assert "SEMANTIC" in analysis["details"]

def test_certification_engine(base_dimension_results, base_invariants):
    ref = GoldenArtifactReference(
        artifact_id="golden-1",
        artifact_type="PRESENTATION",
        source_case_id="case-1",
        artifact_file_reference="path"
    )
    
    # Introduce a regression baseline
    baseline = {"SEMANTIC": 0.95, "VISUAL": 0.95} # Current visual is 0.80 -> 0.15 drop
    
    eval_result = CertificationEngine.certify(
        artifact_id="gen-1",
        golden_reference=ref,
        corpus_version="1.0.0",
        dimension_results=base_dimension_results,
        hard_invariant_results=base_invariants,
        historical_baseline=baseline
    )
    
    assert eval_result.regression_analysis["is_regression"] is True
    assert eval_result.certification_decision == CertificationDecision.BENCHMARK_REGRESSION
    assert eval_result.reference_alignment == pytest.approx(0.875) # (0.95 + 0.80) / 2
