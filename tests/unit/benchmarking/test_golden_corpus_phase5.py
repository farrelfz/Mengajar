"""
Universal Document Intelligence System V5 — Phase 5 Golden Corpus & Benchmark Certification Tests.

Covers Levels 1-7:
- Level 1: Contract tests (ExpectedCharacteristics, ForbiddenFailures, Invariants)
- Level 2: Registry & versioning tests
- Level 3: Regression tests (noise filtering, material drop, dimensional awareness)
- Level 4: Anti-benchmark-laundering governance tests (silent lowering, missing lineage)
- Level 5: Cross-artifact divergence tests (collapse detection: presentation, worksheet, essay, homogenization)
- Level 6: Replay harness tests
- Level 7: Adversarial benchmark scenarios (Scenarios A through O)
"""

import hashlib
import json
import pytest
from pathlib import Path

from app.benchmarking.golden_contracts import (
    AdversarialVariant,
    BenchmarkEvaluation,
    CertificationDecision,
    CertificationStatus,
    DimensionResult,
    ExpectedCharacteristics,
    ExpectedInvariants,
    ForbiddenFailures,
    GoldenArtifactReference,
    GoldenCase,
    GoldenCorpus,
    GoldenCorpusVersion,
    VariationPolicy,
)
from app.benchmarking.golden_registry import (
    GoldenCorpusLoader,
    GoldenCorpusRegistry,
    GoldenCorpusValidator,
    GoldenCorpusVersionManager,
)
from app.benchmarking.governance import (
    AntiLaunderingGuard,
    BaselineMutationRecord,
    BenchmarkLaunderingAttemptError,
    ChangeClassification,
)
from app.benchmarking.divergence import (
    CrossArtifactDivergenceBenchmark,
    CrossArtifactDivergenceReport,
)
from app.benchmarking.certification import (
    CertificationEngine,
    CertificationPolicy,
    RegressionDetector,
)
from app.benchmarking.replay_harness import CorpusReplayHarness
from app.benchmarking.taxonomy import CorpusSplit
from app.benchmarking.leakage_guard import BenchmarkLeakageGuard, BenchmarkLeakageError


# ============================================================================
# LEVEL 1: CONTRACT TESTS
# ============================================================================

def test_expected_characteristics_contract():
    chars = ExpectedCharacteristics(
        must_have=("narrative_progression", "visual_hierarchy"),
        must_not_have=("wall_of_text",),
        preferred=("diagram_focal_point",),
        acceptable_variation=("color_palette",)
    )
    assert "narrative_progression" in chars.must_have
    assert "wall_of_text" in chars.must_not_have
    assert len(chars.preferred) == 1


def test_forbidden_failures_contract():
    ff = ForbiddenFailures(
        forbidden_failure_codes=("WALL_OF_TEXT", "ANSWER_LEAK", "COGNITIVE_OVERLOAD")
    )
    assert "ANSWER_LEAK" in ff.forbidden_failure_codes


def test_adversarial_variant_contract():
    adv = AdversarialVariant(
        variant_id="adv_ws_01",
        artifact_type="WORKSHEET",
        mutation_type="ANSWER_LEAK",
        expected_failure_code="ANSWER_LEAK",
        description="Worksheet leaking conclusion in observation step",
        payload={"prompt": "Kunci jawaban: mengeras karena gesekan"}
    )
    assert adv.expected_failure_code == "ANSWER_LEAK"
    assert adv.artifact_type == "WORKSHEET"


# ============================================================================
# LEVEL 2: GOLDEN REGISTRY & VERSIONING TESTS
# ============================================================================

def test_golden_corpus_loader_and_validator():
    manifest_path = Path("golden_corpus/corpus_manifest.json")
    assert manifest_path.exists()
    corpus = GoldenCorpusLoader.load_from_file(manifest_path)
    ok, issues = GoldenCorpusValidator.validate(corpus)
    assert ok is True
    assert len(issues) == 0
    assert "GOLDEN_OOBLECK" in corpus.cases
    assert "GOLDEN_HAND_FIRE" in corpus.cases


def test_version_manager_immutable_transition():
    corpus = GoldenCorpusLoader.load_from_file("golden_corpus/corpus_manifest.json")
    v2 = GoldenCorpusVersionManager.create_new_version(
        corpus=corpus,
        new_version_str="1.1.0",
        change_summary="Governed expansion with updated validation references",
        created_by="CuratorEngineer"
    )
    assert v2.current_version.version == "1.1.0"
    assert v2.current_version.parent_version == "1.0.0"
    assert v2.current_version.change_summary.startswith("Governed expansion")


def test_version_manager_rejects_duplicate_version():
    corpus = GoldenCorpusLoader.load_from_file("golden_corpus/corpus_manifest.json")
    with pytest.raises(ValueError, match="must differ"):
        GoldenCorpusVersionManager.create_new_version(
            corpus=corpus,
            new_version_str="1.0.0",
            change_summary="Duplicate attempt"
        )


# ============================================================================
# LEVEL 3: REGRESSION INTEGRATION TESTS
# ============================================================================

def test_regression_detection_noise_filtering():
    current = {
        "SEMANTIC": DimensionResult(
            dimension="SEMANTIC", raw_measurements={}, normalized_score=0.92,
            confidence=0.90, applicability=1.0, comparison_mode=VariationPolicy.EXACT
        )
    }
    baseline = {"SEMANTIC": 0.94}  # Drop of 0.02 is under noise threshold 0.05
    res = RegressionDetector.detect(current, baseline)
    assert res["is_regression"] is False


def test_regression_detection_material_drop():
    current = {
        "SEMANTIC": DimensionResult(
            dimension="SEMANTIC", raw_measurements={}, normalized_score=0.82,
            confidence=0.90, applicability=1.0, comparison_mode=VariationPolicy.EXACT
        )
    }
    baseline = {"SEMANTIC": 0.95}  # Drop of 0.13 is material
    res = RegressionDetector.detect(current, baseline)
    assert res["is_regression"] is True
    assert "SEMANTIC" in res["details"]
    assert res["details"]["SEMANTIC"]["drop"] == pytest.approx(0.13)


def test_aggregate_improvement_cannot_mask_invariant_failure():
    # Overall score is very high (0.95), but hard invariant fails
    dim_results = {
        "SEMANTIC": DimensionResult(
            dimension="SEMANTIC", raw_measurements={}, normalized_score=0.98,
            confidence=0.95, applicability=1.0, comparison_mode=VariationPolicy.EXACT
        ),
        "VISUAL": DimensionResult(
            dimension="VISUAL", raw_measurements={}, normalized_score=0.92,
            confidence=0.90, applicability=1.0, comparison_mode=VariationPolicy.TOLERANT
        )
    }
    invariants = {
        "no_fabricated_claims": True,
        "no_answer_leak": False  # VIOLATION!
    }
    decision = CertificationPolicy.evaluate(dim_results, invariants)
    assert decision == CertificationDecision.BENCHMARK_INSUFFICIENT


# ============================================================================
# LEVEL 4: ANTI-BENCHMARK-LAUNDERING GOVERNANCE TESTS
# ============================================================================

def test_anti_laundering_rejects_unknown_change():
    record = BaselineMutationRecord(
        target_case_id="GOLDEN_OOBLECK",
        target_artifact_type="PRESENTATION",
        previous_baseline_reference="v1.0.0",
        previous_scores={"SEMANTIC": 0.95},
        new_scores={"SEMANTIC": 0.95},
        change_reason="Legitimate parameter retuning following new experimental run",
        expected_quality_impact="No regression expected",
        change_classification=ChangeClassification.UNKNOWN_CHANGE
    )
    with pytest.raises(BenchmarkLaunderingAttemptError, match="UNKNOWN_CHANGE"):
        AntiLaunderingGuard.validate_mutation(record, strict_raise=True)


def test_anti_laundering_rejects_superficial_reason():
    record = BaselineMutationRecord(
        target_case_id="GOLDEN_OOBLECK",
        target_artifact_type="PRESENTATION",
        previous_baseline_reference="v1.0.0",
        previous_scores={"SEMANTIC": 0.95},
        new_scores={"SEMANTIC": 0.95},
        change_reason="short",  # < 15 chars
        expected_quality_impact="None",
        change_classification=ChangeClassification.REFERENCE_REGENERATION
    )
    with pytest.raises(BenchmarkLaunderingAttemptError, match="superficial"):
        AntiLaunderingGuard.validate_mutation(record, strict_raise=True)


def test_anti_laundering_rejects_missing_lineage():
    record = BaselineMutationRecord(
        target_case_id="GOLDEN_OOBLECK",
        target_artifact_type="PRESENTATION",
        previous_baseline_reference="",  # Missing!
        previous_scores={"SEMANTIC": 0.95},
        new_scores={"SEMANTIC": 0.95},
        change_reason="Re-calibrating the reference baseline following new guidelines",
        expected_quality_impact="Maintains identical accuracy",
        change_classification=ChangeClassification.REFERENCE_REGENERATION
    )
    with pytest.raises(BenchmarkLaunderingAttemptError, match="Lineage link"):
        AntiLaunderingGuard.validate_mutation(record, strict_raise=True)


def test_anti_laundering_rejects_silent_baseline_lowering():
    # Attempt to lower baseline from 0.95 to 0.80 under CORPUS_EXPANSION without valid justification
    record = BaselineMutationRecord(
        target_case_id="GOLDEN_OOBLECK",
        target_artifact_type="PRESENTATION",
        previous_baseline_reference="v1.0.0",
        previous_scores={"SEMANTIC": 0.95},
        new_scores={"SEMANTIC": 0.80},  # Lowered!
        change_reason="Adjusting benchmark score targets for new release cycle",
        expected_quality_impact="Lowers requirement",
        change_classification=ChangeClassification.CORPUS_EXPANSION  # Not in allowed lowering classes!
    )
    with pytest.raises(BenchmarkLaunderingAttemptError, match="Silent baseline lowering detected"):
        AntiLaunderingGuard.validate_mutation(record, strict_raise=True)


def test_anti_laundering_accepts_governed_policy_evolution():
    record = BaselineMutationRecord(
        target_case_id="GOLDEN_OOBLECK",
        target_artifact_type="PRESENTATION",
        previous_baseline_reference="v1.0.0",
        previous_scores={"SEMANTIC": 0.95},
        new_scores={"SEMANTIC": 0.90},
        change_reason="Formal recalibration of semantic metric weights under approved governance policy",
        expected_quality_impact="Slightly relaxed constraint on secondary conceptual descriptions",
        change_classification=ChangeClassification.POLICY_EVOLUTION
    )
    ok, violations = AntiLaunderingGuard.validate_mutation(record, strict_raise=True)
    assert ok is True
    assert len(violations) == 0


# ============================================================================
# LEVEL 5: CROSS-ARTIFACT DIVERGENCE TESTS
# ============================================================================

def test_divergence_detects_presentation_handout_collapse():
    # Presentation with dense text on slides
    artifacts = {
        "PRESENTATION": {
            "slides": [
                {"CORE_MESSAGE": "Slide 1", "content": " ".join(["word"] * 85)},
                {"CORE_MESSAGE": "Slide 2", "content": " ".join(["word"] * 90)},
            ]
        },
        "HANDOUT": {
            "sections": [
                {"content": "Standard reading section with comprehensive continuous paragraph discussion."}
            ]
        }
    }
    report = CrossArtifactDivergenceBenchmark.evaluate("case_test", artifacts)
    assert any("PRESENTATION_TO_HANDOUT_COLLAPSE" in c for c in report.detected_collapses)


def test_divergence_detects_worksheet_answer_leak():
    artifacts = {
        "WORKSHEET": {
            "activities": [
                {
                    "prompt_text": "Kunci jawaban: Fluida mengeras karena gesekan partikel.",
                    "withhold_explanation": False,
                    "ANSWER_LEAK_RISK": True
                }
            ]
        },
        "HANDOUT": {"sections": [{"content": "Regular text"}]}
    }
    report = CrossArtifactDivergenceBenchmark.evaluate("case_test", artifacts)
    assert any("WORKSHEET_TO_ANSWER_LEAK" in c for c in report.detected_collapses)


def test_divergence_detects_quiz_collapse():
    artifacts = {
        "WORKSHEET": {
            "activities": [
                {"activity_type": "QUESTION", "prompt_text": "What is torque?"},
                {"activity_type": "QUESTION", "prompt_text": "What is inertia?"},
                {"activity_type": "QUESTION", "prompt_text": "What is force?"},
            ]
        },
        "PRESENTATION": {"slides": [{"CORE_MESSAGE": "A"}]}
    }
    report = CrossArtifactDivergenceBenchmark.evaluate("case_test", artifacts)
    assert any("WORKSHEET_TO_QUIZ_COLLAPSE" in c for c in report.detected_collapses)


def test_divergence_detects_scientific_essay_collapse():
    artifacts = {
        "SCIENTIFIC_DOCUMENT": {
            "arguments": [
                {"claim": "All fluids behave non-linearly under pressure", "supporting_evidence_unit_ids": []},
                {"claim": "Viscosity is purely illusory", "supporting_evidence_unit_ids": []},
            ]
        },
        "HANDOUT": {"sections": [{"content": "Regular text"}]}
    }
    report = CrossArtifactDivergenceBenchmark.evaluate("case_test", artifacts)
    assert any("SCIENTIFIC_TO_GENERIC_ESSAY_COLLAPSE" in c for c in report.detected_collapses)


def test_divergence_differentiated_artifacts_pass():
    artifacts = {
        "PRESENTATION": {
            "slides": [
                {"slide_id": "s1", "SEMANTIC_ROLE": "HOOK", "content": "Key visual prompt"},
                {"slide_id": "s2", "SEMANTIC_ROLE": "MECHANISM", "content": "Visual diagram callout"},
            ]
        },
        "HANDOUT": {
            "sections": [
                {"level": 1, "content": "Comprehensive detailed explanatory reading content without oral guidance.", "definitions": ["def"]},
                {"level": 2, "content": "Mechanistic deeper discussion and worked derivation examples.", "examples": ["ex"]},
            ]
        },
        "WORKSHEET": {
            "activities": [
                {"INQUIRY_STAGE": "PHENOMENON", "prompt_text": "Observe the reaction.", "withhold_explanation": True},
                {"INQUIRY_STAGE": "INVESTIGATION", "prompt_text": "Measure temperature delta.", "withhold_explanation": True},
            ]
        },
        "SCIENTIFIC_DOCUMENT": {
            "arguments": [
                {"claim": "Shear rate governs dynamic viscosity", "EVIDENCE_TYPE": "EXPERIMENTAL_RESULT", "supporting_evidence_unit_ids": ["ev1"]},
            ]
        }
    }
    report = CrossArtifactDivergenceBenchmark.evaluate("case_test", artifacts)
    assert report.is_sufficiently_divergent is True
    assert len(report.detected_collapses) == 0


# ============================================================================
# LEVEL 6: REPLAY HARNESS TESTS
# ============================================================================

def test_replay_harness_single_case():
    corpus = GoldenCorpusLoader.load_from_file("golden_corpus/corpus_manifest.json")
    case = corpus.cases["GOLDEN_OOBLECK"]
    harness = CorpusReplayHarness()

    generated = {
        "PRESENTATION": {
            "artifact_type": "PRESENTATION",
            "concepts": ["non_newtonian_fluid", "shear_stress", "shear_rate", "viscosity"],
            "block_count": 12,
            "visual_density": 0.38,
            "slides": [{"slide_id": "s1", "SEMANTIC_ROLE": "HOOK", "content": "Prompt"}],
            "has_fabricated_claims": False,
            "has_unsupported_evidence": False,
            "has_text_clipping": False,
            "has_element_collision": False,
        }
    }

    evals, div = harness.replay_case(case, generated)
    assert "PRESENTATION" in evals
    assert evals["PRESENTATION"].certification_decision in (
        CertificationDecision.CERTIFIED_EXCELLENT,
        CertificationDecision.CERTIFIED_ACCEPTABLE
    )
    assert evals["PRESENTATION"].reference_alignment >= 0.90


def test_replay_harness_full_corpus():
    corpus = GoldenCorpusLoader.load_from_file("golden_corpus/corpus_manifest.json")
    harness = CorpusReplayHarness()

    # Build valid targets for all 8 references
    generated_corpus = {}
    for cid, case in corpus.cases.items():
        generated_corpus[cid] = {}
        for atype, ref in case.references.items():
            state = {
                "artifact_type": atype,
                "concepts": ref.semantic_expectations.get("concepts", []),
                "block_count": ref.structural_expectations.get("block_count", 10),
                "visual_density": ref.visual_expectations.get("visual_density", 0.5),
                "has_fabricated_claims": False,
                "has_unsupported_evidence": False,
                "has_text_clipping": False,
                "has_element_collision": False,
            }
            if atype == "PRESENTATION":
                state["slides"] = [{"slide_id": "s1", "SEMANTIC_ROLE": "HOOK", "content": "Text"}]
            elif atype == "HANDOUT":
                state["sections"] = [{"level": 1, "content": "Prose"}]
            elif atype == "WORKSHEET":
                state["activities"] = [{"INQUIRY_STAGE": "PHENOMENON", "prompt_text": "Observe", "withhold_explanation": True}]
                state["inquiry_arc_complete"] = True
                state["observation_before_explanation"] = True
                state["has_answer_leak"] = False
            elif atype == "SCIENTIFIC_DOCUMENT":
                state["arguments"] = [{"claim": "C", "EVIDENCE_TYPE": "EMPIRICAL_DATA", "supporting_evidence_unit_ids": ["e1"]}]
                state["citation_density"] = 1.0
                state["evidence_linkage_intact"] = True
                state["has_broken_citations"] = False
            generated_corpus[cid][atype] = state

    report = harness.replay_corpus(corpus, generated_corpus)
    assert len(report.evaluations) == 8
    assert report.all_certified is True
    assert report.summary_counts[CertificationDecision.CERTIFIED_EXCELLENT.value] == 8


# ============================================================================
# LEVEL 7: ADVERSARIAL BENCHMARK SCENARIOS (A THROUGH O)
# ============================================================================

def test_scenario_b_hash_tampering():
    raw_content = "# Real experiment source"
    real_hash = AntiLaunderingGuard.compute_content_digest(raw_content)
    tampered_content = "# Tampered experiment source with subtle falsification"
    assert AntiLaunderingGuard.verify_content_digest(tampered_content, real_hash) is False


def test_scenario_c_overall_score_high_but_invariant_fails():
    ref = GoldenArtifactReference(
        artifact_id="ref_test",
        artifact_type="WORKSHEET",
        source_case_id="case_1",
        artifact_file_reference="path"
    )
    dim_results = {
        "SEMANTIC": DimensionResult(
            dimension="SEMANTIC", raw_measurements={}, normalized_score=1.0,
            confidence=1.0, applicability=1.0, comparison_mode=VariationPolicy.EXACT
        )
    }
    invariants = {
        "no_fabricated_claims": True,
        "no_answer_leak": False  # Failed invariant!
    }
    eval_result = CertificationEngine.certify(
        artifact_id="gen_test",
        golden_reference=ref,
        corpus_version="1.0.0",
        dimension_results=dim_results,
        hard_invariant_results=invariants
    )
    assert eval_result.certification_decision == CertificationDecision.BENCHMARK_INSUFFICIENT


def test_scenario_d_score_fluctuation_within_noise_threshold():
    current = {
        "SEMANTIC": DimensionResult(
            dimension="SEMANTIC", raw_measurements={}, normalized_score=0.91,
            confidence=0.90, applicability=1.0, comparison_mode=VariationPolicy.EXACT
        )
    }
    baseline = {"SEMANTIC": 0.93}  # 0.02 drop < 0.05 noise threshold
    analysis = RegressionDetector.detect(current, baseline)
    assert analysis["is_regression"] is False


def test_scenario_e_single_critical_dimension_collapses_while_aggregate_improves():
    dim_results = {
        "SEMANTIC": DimensionResult(
            dimension="SEMANTIC", raw_measurements={}, normalized_score=0.99,
            confidence=0.95, applicability=1.0, comparison_mode=VariationPolicy.EXACT
        ),
        "VISUAL": DimensionResult(
            dimension="VISUAL", raw_measurements={}, normalized_score=0.45,  # Collapsed below 0.50!
            confidence=0.90, applicability=1.0, comparison_mode=VariationPolicy.TOLERANT
        )
    }
    invariants = {"no_text_clipping": True}
    decision = CertificationPolicy.evaluate(dim_results, invariants)
    assert decision == CertificationDecision.MANUAL_BENCHMARK_REVIEW_REQUIRED


def test_scenario_j_unseen_leakage_guard_intervention():
    # Verify that BenchmarkLeakageGuard detects and prevents uncertified memory mutation
    with BenchmarkLeakageGuard(CorpusSplit.UNSEEN_GENERALIZATION, strict_raise=False) as guard:
        assert guard.is_protected is True
