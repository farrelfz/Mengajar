"""
Unit tests for benchmark taxonomy, splits, evidence ratings, and failure classifications.
"""

from app.benchmarking.taxonomy import (
    CorpusCategory,
    CorpusSplit,
    EvidenceStrength,
    GeneralizationFailureType,
)


def test_01_corpus_categories_exist_and_distinct():
    categories = [
        CorpusCategory.CONCEPT_HEAVY,
        CorpusCategory.EXPERIMENT_HEAVY,
        CorpusCategory.NARRATIVE_HEAVY,
        CorpusCategory.SCIENTIFIC_HEAVY,
        CorpusCategory.PATHOLOGICAL,
    ]
    assert len(set(categories)) == 5
    for c in categories:
        assert isinstance(c.value, str)


def test_02_corpus_splits_exist_and_distinct():
    splits = [
        CorpusSplit.TRAINING_REFERENCE,
        CorpusSplit.VALIDATION_REFERENCE,
        CorpusSplit.UNSEEN_GENERALIZATION,
        CorpusSplit.ADVERSARIAL,
    ]
    assert len(set(splits)) == 4


def test_03_evidence_strength_hierarchy():
    ratings = [
        EvidenceStrength.INSUFFICIENT,
        EvidenceStrength.LIMITED,
        EvidenceStrength.MODERATE,
        EvidenceStrength.STRONG,
    ]
    assert len(set(ratings)) == 4


def test_04_failure_taxonomy_completeness():
    required = [
        "EXECUTION_FAILURE",
        "ZERO_EFFECT_FAILURE",
        "CAUSAL_MISMATCH",
        "UNDER_SCOPED_MUTATION",
        "OVER_SCOPED_MUTATION",
        "REGRESSION_FAILURE",
        "CROSS_ARTIFACT_INCOMPATIBILITY",
        "STRUCTURAL_GENERALIZATION_FAILURE",
        "SEMANTIC_GENERALIZATION_FAILURE",
        "BENCHMARK_LEAKAGE_RISK",
        "INSUFFICIENT_EVIDENCE_FOR_OPERATOR",
        "NON_AUTOMATABLE_GENERALIZATION_FAILURE",
    ]
    for r in required:
        assert hasattr(GeneralizationFailureType, r)
        assert getattr(GeneralizationFailureType, r).value == r
