"""
Tests for Phase 3 Benchmark Comparison Models.
"""

import pytest
from app.benchmarking.golden_contracts import (
    GoldenArtifactReference,
    VariationPolicy
)
from app.benchmarking.comparison import (
    SemanticComparison,
    StructuralComparison,
    VisualComparison,
    create_pedagogical_comparison
)

@pytest.fixture
def golden_ref():
    return GoldenArtifactReference(
        artifact_id="art-1",
        artifact_type="PRESENTATION",
        source_case_id="case-1",
        artifact_file_reference="path",
        semantic_expectations={"concepts": ["newton_first_law", "inertia"]},
        structural_expectations={"block_count": 10},
        visual_expectations={"visual_density": 0.5},
        pedagogical_expectations={"inquiry_arc_complete": True},
        acceptable_variations={
            "semantic": VariationPolicy.EXACT,
            "structural": VariationPolicy.TOLERANT,
            "visual": VariationPolicy.FUNCTIONAL_EQUIVALENCE,
            "pedagogical": VariationPolicy.EXACT
        }
    )

def test_semantic_comparison_exact(golden_ref):
    comp = SemanticComparison()
    
    # Perfect match
    gen_state = {"concepts": ["newton_first_law", "inertia"]}
    res = comp.evaluate(gen_state, golden_ref)
    assert res.normalized_score == 1.0
    
    # Partial match
    gen_state = {"concepts": ["newton_first_law"]}
    res = comp.evaluate(gen_state, golden_ref)
    assert res.normalized_score == 0.5

def test_structural_comparison_tolerant(golden_ref):
    comp = StructuralComparison()
    
    # Exact match
    gen_state = {"block_count": 10}
    res = comp.evaluate(gen_state, golden_ref)
    assert res.normalized_score == 1.0
    
    # 20% deviation (within TOLERANT limits)
    gen_state = {"block_count": 12}
    res = comp.evaluate(gen_state, golden_ref)
    assert res.normalized_score == 1.0
    
    # 50% deviation
    gen_state = {"block_count": 15}
    res = comp.evaluate(gen_state, golden_ref)
    # 0.5 ratio, tolerant gives 1.0 - (0.5 - 0.2) = 0.7
    assert res.normalized_score == pytest.approx(0.7)

def test_visual_comparison_functional(golden_ref):
    comp = VisualComparison()
    
    # Exact match
    gen_state = {"visual_density": 0.5}
    res = comp.evaluate(gen_state, golden_ref)
    assert res.normalized_score == 1.0
    
    # 0.20 deviation (within FUNCTIONAL_EQUIVALENCE 0.25 limit)
    gen_state = {"visual_density": 0.3}
    res = comp.evaluate(gen_state, golden_ref)
    assert res.normalized_score == 1.0
    
    # 0.40 deviation
    gen_state = {"visual_density": 0.1}
    res = comp.evaluate(gen_state, golden_ref)
    # diff = 0.4. 1.0 - ((0.4 - 0.25) * 4) = 1.0 - (0.15 * 4) = 0.4
    assert res.normalized_score == pytest.approx(0.4)

def test_pedagogical_comparison(golden_ref):
    comp = create_pedagogical_comparison()
    
    gen_state = {"inquiry_arc_complete": True}
    res = comp.evaluate(gen_state, golden_ref)
    assert res.normalized_score == 1.0
    
    gen_state = {"inquiry_arc_complete": False}
    res = comp.evaluate(gen_state, golden_ref)
    assert res.normalized_score == 0.0

def test_empty_expectations_yield_zero_applicability():
    comp = SemanticComparison()
    empty_ref = GoldenArtifactReference(
        artifact_id="art-2",
        artifact_type="HANDOUT",
        source_case_id="case-2",
        artifact_file_reference="path",
    )
    res = comp.evaluate({}, empty_ref)
    assert res.applicability == 0.0
    assert res.normalized_score == 1.0
