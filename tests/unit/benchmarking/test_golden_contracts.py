"""
Tests for Phase 5 Golden Benchmark Contracts.
"""

import pytest
from pydantic import ValidationError
from app.benchmarking.golden_contracts import (
    VariationPolicy,
    CertificationStatus,
    CertificationDecision,
    ExpectedInvariants,
    GoldenArtifactReference,
    GoldenCase,
    GoldenCorpusVersion,
    GoldenCorpus,
    DimensionResult,
    BenchmarkEvaluation
)

def test_expected_invariants_defaults():
    invariants = ExpectedInvariants()
    assert invariants.no_fabricated_claims is True
    assert invariants.no_unsupported_evidence is True
    assert invariants.no_text_clipping is True
    
def test_golden_artifact_reference_creation():
    ref = GoldenArtifactReference(
        artifact_id="test-art-1",
        artifact_type="PRESENTATION",
        source_case_id="case-1",
        artifact_file_reference="path/to/golden.pdf",
        acceptable_variations={"layout": VariationPolicy.FUNCTIONAL_EQUIVALENCE},
        review_status=CertificationStatus.CERTIFIED
    )
    assert ref.artifact_id == "test-art-1"
    assert ref.review_status == CertificationStatus.CERTIFIED
    assert ref.acceptable_variations["layout"] == VariationPolicy.FUNCTIONAL_EQUIVALENCE
    assert ref.hard_invariants.no_fabricated_claims is True

def test_dimension_result_bounds():
    with pytest.raises(ValidationError):
        DimensionResult(
            dimension="SEMANTIC",
            raw_measurements={"score": 1.5},
            normalized_score=1.5,  # Invalid, must be <= 1.0
            confidence=0.9,
            applicability=1.0
        )
        
    res = DimensionResult(
        dimension="SEMANTIC",
        raw_measurements={"overlap": 0.9},
        normalized_score=0.9,
        confidence=0.95,
        applicability=1.0,
        comparison_mode=VariationPolicy.TOLERANT
    )
    assert res.normalized_score == 0.9

def test_benchmark_evaluation_creation():
    eval_result = BenchmarkEvaluation(
        evaluation_id="eval-1",
        artifact_id="gen-art-1",
        golden_reference_id="test-art-1",
        corpus_version="1.0.0",
        benchmark_protocol_version="1.0",
        certification_decision=CertificationDecision.CERTIFIED_ACCEPTABLE,
        reference_alignment=0.95
    )
    assert eval_result.certification_decision == CertificationDecision.CERTIFIED_ACCEPTABLE
    assert eval_result.reference_alignment == 0.95
    
def test_golden_corpus_versioning():
    version = GoldenCorpusVersion(
        version="2.0.0",
        parent_version="1.0.0",
        change_summary="Added adversarial fixtures",
        created_by="ExpertReviewer"
    )
    
    corpus = GoldenCorpus(
        corpus_id="physics-corpus",
        current_version=version
    )
    
    assert corpus.current_version.version == "2.0.0"
    assert corpus.current_version.parent_version == "1.0.0"
