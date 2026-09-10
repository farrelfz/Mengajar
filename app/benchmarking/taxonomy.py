"""
Universal Document Intelligence System V5 — Benchmark Corpus Taxonomy & Failure Classifications.

Phase 4.1: Defines standardized categorical partitions for benchmark corpora,
dataset splits, evidence strength criteria, and generalization failure modes.
"""

from __future__ import annotations

from enum import Enum


class CorpusCategory(str, Enum):
    """Orthogonal categories describing the primary epistemic style of source fixtures."""
    CONCEPT_HEAVY = "CONCEPT_HEAVY"
    EXPERIMENT_HEAVY = "EXPERIMENT_HEAVY"
    NARRATIVE_HEAVY = "NARRATIVE_HEAVY"
    SCIENTIFIC_HEAVY = "SCIENTIFIC_HEAVY"
    PATHOLOGICAL = "PATHOLOGICAL"


class CorpusSplit(str, Enum):
    """Rigorous train/val/unseen/adversarial split assignments."""
    TRAINING_REFERENCE = "TRAINING_REFERENCE"
    VALIDATION_REFERENCE = "VALIDATION_REFERENCE"
    UNSEEN_GENERALIZATION = "UNSEEN_GENERALIZATION"
    ADVERSARIAL = "ADVERSARIAL"


class EvidenceStrength(str, Enum):
    """Evidence rating evaluating operator reliability across diverse conditions."""
    INSUFFICIENT = "INSUFFICIENT"  # < 3 distinct fixture signatures or single success
    LIMITED = "LIMITED"            # 3-5 fixtures, single artifact type
    MODERATE = "MODERATE"          # > 5 fixtures across at least 2 structural signatures
    STRONG = "STRONG"              # Proven across unseen fixtures, >= 2 artifact types, zero regressive outcomes


class GeneralizationFailureType(str, Enum):
    """Explicit taxonomy distinguishing generalization failures from ordinary local repair failures."""
    EXECUTION_FAILURE = "EXECUTION_FAILURE"
    ZERO_EFFECT_FAILURE = "ZERO_EFFECT_FAILURE"
    CAUSAL_MISMATCH = "CAUSAL_MISMATCH"
    UNDER_SCOPED_MUTATION = "UNDER_SCOPED_MUTATION"
    OVER_SCOPED_MUTATION = "OVER_SCOPED_MUTATION"
    REGRESSION_FAILURE = "REGRESSION_FAILURE"
    CROSS_ARTIFACT_INCOMPATIBILITY = "CROSS_ARTIFACT_INCOMPATIBILITY"
    STRUCTURAL_GENERALIZATION_FAILURE = "STRUCTURAL_GENERALIZATION_FAILURE"
    SEMANTIC_GENERALIZATION_FAILURE = "SEMANTIC_GENERALIZATION_FAILURE"
    BENCHMARK_LEAKAGE_RISK = "BENCHMARK_LEAKAGE_RISK"
    INSUFFICIENT_EVIDENCE_FOR_OPERATOR = "INSUFFICIENT_EVIDENCE_FOR_OPERATOR"
    NON_AUTOMATABLE_GENERALIZATION_FAILURE = "NON_AUTOMATABLE_GENERALIZATION_FAILURE"
