"""
Phase 4.1 — Canonical Artifact Blueprint Hardening: Contract Tests.

Tests deterministic structural validation of generated Markdown blueprints.
All validators are offline and LLM-free.
"""

from __future__ import annotations

import pytest
from app.intelligence.blueprint_validation import (
    BlueprintFailureType,
    BlueprintValidationReport,
    PresentationBlueprintValidator,
    HandoutBlueprintValidator,
    WorksheetBlueprintValidator,
    ScientificDocumentBlueprintValidator,
    BlueprintAntiPatternDetector,
)


# ============================================================================
# FIXTURES
# ============================================================================

def make_valid_slide(i: int, role: str = "CONCEPT", grammar: str = "CONCEPT") -> dict:
    return {
        "SLIDE_ID": f"slide_{i:02d}",
        "SEMANTIC_ROLE": role,
        "CORE_MESSAGE": "Core message here",
        "VISUAL_GRAMMAR": grammar,
        "COGNITIVE_LOAD_TARGET": 0.40,
        "HANDOUT_COLLAPSE_RISK": False,
        "WHY_THIS_SLIDE_EXISTS": "This visual communicates the concept",
        "KNOWLEDGE_UNITS_USED": ["ku_001"],
        "NARRATIVE_TRANSITION_OUT": "This leads to the next concept",
        "PROGRESSIVE_DISCLOSURE_PLAN": "Reveal layer by layer",
    }

def make_valid_presentation() -> dict:
    return {
        "PRESENTATION_THESIS": "Newton's laws explain inertia",
        "CENTRAL_QUESTION": "Why do objects keep moving?",
        "TARGET_AUDIENCE": "High school physics students",
        "slides": [
            make_valid_slide(1, "HOOK"),
            make_valid_slide(2, "PHENOMENON"),
            make_valid_slide(3, "CONCEPT"),
            make_valid_slide(4, "MECHANISM"),
            make_valid_slide(5, "SYNTHESIS"),
        ],
    }

def make_valid_section(i: int) -> dict:
    return {
        "SECTION_ID": f"sec_{i:02d}",
        "SECTION_PURPOSE": "Explain the concept",
        "KNOWLEDGE_UNITS_USED": ["ku_001"],
        "TRANSITION_FROM_PREVIOUS": "Building on the previous section",
        "TRANSITION_TO_NEXT": "Leading into the next concept",
        "LAYER_1_INTUITION": "Intuitively, this is like...",
        "LAYER_2_FORMAL_EXPLANATION": "Formally defined as...",
        "LAYER_3_MECHANISM": "The mechanism works by...",
        "LAYER_4_EXAMPLE": "For example...",
        "WALL_OF_TEXT_RISK": False,
    }

def make_valid_handout() -> dict:
    return {
        "READING_PURPOSE": "Independent study of Newton's laws",
        "TARGET_READER": "High school student",
        "INDEPENDENT_COMPREHENSION_TARGET": "Student can explain inertia without teacher",
        "sections": [make_valid_section(i) for i in range(1, 4)],
    }

def make_valid_activity(i: int, stage: str = "INVESTIGATION") -> dict:
    return {
        "ACTIVITY_ID": f"act_{i:02d}",
        "INQUIRY_STAGE": stage,
        "STUDENT_ACTION": "Measure and record",
        "WITHHOLD_EXPLANATION": True,
        "ANSWER_LEAK_RISK": False,
        "WORKSPACE_JUSTIFICATION": "Students need space to draw their observations",
        "WORKSPACE_REQUIREMENT": "Half-page blank space",
        "QUESTION_TAXONOMY": "OBSERVATIONAL",
        "KNOWLEDGE_UNITS_USED": ["ku_001"],
    }

def make_valid_worksheet() -> dict:
    return {
        "CENTRAL_INVESTIGATIVE_QUESTION": "How does surface area affect friction?",
        "INQUIRY_DEPTH": "DEEP",
        "activities": [
            make_valid_activity(1, "PHENOMENON"),
            make_valid_activity(2, "PREDICTION"),
            make_valid_activity(3, "INVESTIGATION"),
            make_valid_activity(4, "DATA_ANALYSIS"),
            make_valid_activity(5, "REFLECTION"),
        ],
    }

def make_valid_argument(i: int, claim_type: str = "OBSERVATIONAL", uncertainty: str = "SUPPORTED") -> dict:
    return {
        "ARGUMENT_UNIT_ID": f"arg_{i:02d}",
        "CLAIM": "Non-Newtonian fluids exhibit variable viscosity.",
        "CLAIM_TYPE": claim_type,
        "CLAIM_STRENGTH": "MODERATE",
        "EVIDENCE": "Cornstarch-water mixture hardens under rapid force.",
        "EVIDENCE_TYPE": "EXPERIMENTAL_RESULT",
        "EVIDENCE_DIRECTNESS": "DIRECT",
        "UNCERTAINTY_STATE": uncertainty,
        "LIMITATION": "Limited to cornstarch-water at room temperature.",
        "SOURCE_TRACEABILITY": "ku_012",
        "FORBIDDEN_FABRICATION_CHECK": True,
    }

def make_valid_scientific() -> dict:
    return {
        "RESEARCH_PROBLEM": "Understanding non-Newtonian fluid behavior",
        "RESEARCH_QUESTION": "How does shear rate affect viscosity in oobleck?",
        "ARGUMENT_THESIS": "Oobleck viscosity is shear-rate dependent.",
        "arguments": [make_valid_argument(i) for i in range(1, 4)],
    }


# ============================================================================
# A. CONTRACT COMPLETENESS TESTS
# ============================================================================

class TestContractCompleteness:
    def test_contract_completeness_presentation(self):
        bp = make_valid_presentation()
        report = PresentationBlueprintValidator().validate(bp)
        assert report.is_valid
        assert report.completeness_score > 0.8
        assert len(report.missing_required_fields) == 0

    def test_contract_completeness_handout(self):
        bp = make_valid_handout()
        report = HandoutBlueprintValidator().validate(bp)
        assert report.is_valid
        assert report.completeness_score > 0.8
        assert len(report.missing_required_fields) == 0

    def test_contract_completeness_worksheet(self):
        bp = make_valid_worksheet()
        report = WorksheetBlueprintValidator().validate(bp)
        assert report.is_valid
        assert len(report.missing_required_fields) == 0

    def test_contract_completeness_scientific(self):
        bp = make_valid_scientific()
        report = ScientificDocumentBlueprintValidator().validate(bp)
        assert report.is_valid
        assert len(report.missing_required_fields) == 0


# ============================================================================
# B. PRESENTATION NEGATIVE TESTS
# ============================================================================

class TestPresentationNegative:
    def test_presentation_negative_wall_of_text(self):
        """Presentation with no WHY_THIS_SLIDE_EXISTS on most slides is flagged."""
        bp = make_valid_presentation()
        for slide in bp["slides"]:
            slide.pop("WHY_THIS_SLIDE_EXISTS")
        report = PresentationBlueprintValidator().validate(bp)
        # At least a warning about unjustified slides
        all_issues = report.anti_pattern_findings + report.hard_invariant_violations + report.warnings
        assert any("WHY_THIS_SLIDE_EXISTS" in issue or "unjustified" in issue.lower() for issue in all_issues)

    def test_presentation_negative_no_narrative_arc(self):
        """Presentation with no opening or closing arc roles fails."""
        bp = make_valid_presentation()
        # Replace all roles with CONCEPT (no hook, no synthesis)
        for slide in bp["slides"]:
            slide["SEMANTIC_ROLE"] = "CONCEPT"
        report = PresentationBlueprintValidator().validate(bp)
        assert not report.is_valid
        assert any("opening arc" in v.lower() or "NARRATIVE_DISCONTINUITY" in v for v in report.hard_invariant_violations)

    def test_presentation_negative_handout_collapse(self):
        """Presentation with all slides flagged HANDOUT_COLLAPSE_RISK triggers violation."""
        bp = make_valid_presentation()
        for slide in bp["slides"]:
            slide["HANDOUT_COLLAPSE_RISK"] = True
        report = PresentationBlueprintValidator().validate(bp)
        collapse_signals = [f for f in report.anti_pattern_findings if "HANDOUT_COLLAPSE" in f]
        assert len(collapse_signals) > 0

    def test_presentation_high_cognitive_load_collapse(self):
        """Presentation with avg cognitive load > 0.65 is flagged."""
        bp = make_valid_presentation()
        for slide in bp["slides"]:
            slide["COGNITIVE_LOAD_TARGET"] = 0.80
        report = PresentationBlueprintValidator().validate(bp)
        assert not report.is_valid
        assert any("cognitive load" in v.lower() for v in report.hard_invariant_violations)


# ============================================================================
# C. HANDOUT NEGATIVE TESTS
# ============================================================================

class TestHandoutNegative:
    def test_handout_negative_slide_fragmentation(self):
        """Handout with WALL_OF_TEXT_RISK flags anti-patterns."""
        bp = make_valid_handout()
        for sec in bp["sections"]:
            sec["WALL_OF_TEXT_RISK"] = True
        report = HandoutBlueprintValidator().validate(bp)
        wall_signals = [f for f in report.anti_pattern_findings if "WALL_OF_TEXT" in f or "fragmentation" in f.lower()]
        assert len(wall_signals) > 0

    def test_handout_negative_missing_transitions(self):
        """Handout sections missing TRANSITION fields fail validation."""
        bp = make_valid_handout()
        # Remove transitions from middle sections
        for sec in bp["sections"][1:]:
            sec.pop("TRANSITION_FROM_PREVIOUS", None)
        report = HandoutBlueprintValidator().validate(bp)
        assert not report.is_valid
        assert any("transition" in v.lower() for v in report.hard_invariant_violations)

    def test_handout_missing_required_fields(self):
        """Handout without READING_PURPOSE fails completeness."""
        bp = make_valid_handout()
        bp.pop("READING_PURPOSE")
        report = HandoutBlueprintValidator().validate(bp)
        assert not report.is_valid
        assert "READING_PURPOSE" in report.missing_required_fields


# ============================================================================
# D. WORKSHEET ADVERSARIAL TESTS
# ============================================================================

class TestWorksheetAdversarial:
    def test_worksheet_adversarial_answer_leak(self):
        """Worksheet with WITHHOLD_EXPLANATION=False on investigation activity fails."""
        bp = make_valid_worksheet()
        # Leak the answer on the investigation activity
        bp["activities"][2]["WITHHOLD_EXPLANATION"] = False
        report = WorksheetBlueprintValidator().validate(bp)
        assert not report.is_valid
        leak_violations = [v for v in report.hard_invariant_violations if "ANSWER_LEAK" in v]
        assert len(leak_violations) > 0

    def test_worksheet_adversarial_answer_leak_risk_flag(self):
        """Worksheet with ANSWER_LEAK_RISK=True on investigation activity fails."""
        bp = make_valid_worksheet()
        bp["activities"][2]["ANSWER_LEAK_RISK"] = True
        report = WorksheetBlueprintValidator().validate(bp)
        assert not report.is_valid
        assert any("ANSWER_LEAK" in v for v in report.hard_invariant_violations)

    def test_worksheet_adversarial_quiz_collapse(self):
        """Worksheet with all QUESTION_TAXONOMY identical triggers collapse detection."""
        bp = make_valid_worksheet()
        for act in bp["activities"]:
            act["QUESTION_TAXONOMY"] = "CAUSAL"
        report = WorksheetBlueprintValidator().validate(bp)
        quiz_signals = [f for f in report.anti_pattern_findings if "QUIZ_COLLAPSE" in f]
        assert len(quiz_signals) > 0

    def test_worksheet_adversarial_broken_inquiry_order(self):
        """CONCLUSION before DATA_ANALYSIS triggers inquiry arc broken violation."""
        bp = make_valid_worksheet()
        # Inject CONCLUSION before DATA_ANALYSIS
        broken = make_valid_activity(6, "CONCLUSION")
        bp["activities"] = [broken] + bp["activities"]  # CONCLUSION first
        report = WorksheetBlueprintValidator().validate(bp)
        arc_violations = [v for v in report.hard_invariant_violations if "INQUIRY_ARC_BROKEN" in v]
        assert len(arc_violations) > 0

    def test_worksheet_adversarial_missing_workspace_justification(self):
        """Workspace requirement without justification triggers a warning."""
        bp = make_valid_worksheet()
        for act in bp["activities"]:
            act.pop("WORKSPACE_JUSTIFICATION", None)
        report = WorksheetBlueprintValidator().validate(bp)
        workspace_warnings = [w for w in report.warnings if "WORKSPACE_JUSTIFICATION" in w]
        assert len(workspace_warnings) > 0


# ============================================================================
# E. SCIENTIFIC ADVERSARIAL TESTS
# ============================================================================

class TestScientificAdversarial:
    def test_scientific_adversarial_unsupported_claim(self):
        """Argument with no EVIDENCE fails claim-evidence linkage check."""
        bp = make_valid_scientific()
        bp["arguments"][0]["EVIDENCE"] = None
        report = ScientificDocumentBlueprintValidator().validate(bp)
        assert not report.is_valid
        unsupported = [v for v in report.hard_invariant_violations if "UNSUPPORTED_SCIENTIFIC_CLAIM" in v]
        assert len(unsupported) > 0

    def test_scientific_adversarial_inference_as_fact(self):
        """CLAIM_TYPE=CAUSAL + EVIDENCE_DIRECTNESS=INFERRED is rejected."""
        bp = make_valid_scientific()
        bp["arguments"][0]["CLAIM_TYPE"] = "CAUSAL"
        bp["arguments"][0]["EVIDENCE_DIRECTNESS"] = "INFERRED"
        report = ScientificDocumentBlueprintValidator().validate(bp)
        assert not report.is_valid
        contradiction = [v for v in report.hard_invariant_violations if "SEMANTIC_FIELD_CONTRADICTION" in v]
        assert len(contradiction) > 0

    def test_scientific_adversarial_missing_uncertainty(self):
        """Invalid UNCERTAINTY_STATE is rejected."""
        bp = make_valid_scientific()
        bp["arguments"][0]["UNCERTAINTY_STATE"] = "ABSOLUTE_FACT"  # invalid
        report = ScientificDocumentBlueprintValidator().validate(bp)
        assert not report.is_valid
        unc_violations = [v for v in report.hard_invariant_violations if "UNCERTAINTY_POLICY_VIOLATION" in v]
        assert len(unc_violations) > 0

    def test_scientific_adversarial_missing_limitation(self):
        """Arguments with no LIMITATION generate warnings."""
        bp = make_valid_scientific()
        for arg in bp["arguments"]:
            arg["LIMITATION"] = None
        report = ScientificDocumentBlueprintValidator().validate(bp)
        limitation_warnings = [w for w in report.warnings if "LIMITATION" in w]
        assert len(limitation_warnings) > 0

    def test_scientific_adversarial_fabrication_check_missing(self):
        """FORBIDDEN_FABRICATION_CHECK must be True on all arguments."""
        bp = make_valid_scientific()
        bp["arguments"][1]["FORBIDDEN_FABRICATION_CHECK"] = False
        report = ScientificDocumentBlueprintValidator().validate(bp)
        assert not report.is_valid
        fab_violations = [v for v in report.hard_invariant_violations if "FORBIDDEN_FABRICATION_CHECK" in v]
        assert len(fab_violations) > 0


# ============================================================================
# F. CROSS-ARTIFACT COLLAPSE TESTS
# ============================================================================

class TestCrossArtifactCollapse:
    def test_cross_artifact_structural_convergence_detected(self):
        """Blueprints with identical top-level structure trigger homogenization warning."""
        detector = BlueprintAntiPatternDetector()
        # Make all four blueprints share the same keys (homogenized)
        same_structure = {
            "title": "x", "sections": [], "slides": [], "arguments": [],
            "SECTION_PURPOSE": "x", "KNOWLEDGE_UNITS_USED": [],
        }
        blueprints = {
            "PRESENTATION": dict(same_structure),
            "HANDOUT": dict(same_structure),
            "WORKSHEET": dict(same_structure),
            "SCIENTIFIC_DOCUMENT": dict(same_structure),
        }
        signals = detector.detect_cross_artifact_homogenization(blueprints)
        assert len(signals) > 0

    def test_cross_artifact_differentiated_blueprints_no_signal(self):
        """Genuinely different blueprints produce no homogenization signals."""
        detector = BlueprintAntiPatternDetector()
        blueprints = {
            "PRESENTATION": {k: v for k, v in make_valid_presentation().items()},
            "HANDOUT": {k: v for k, v in make_valid_handout().items()},
            "WORKSHEET": {k: v for k, v in make_valid_worksheet().items()},
            "SCIENTIFIC_DOCUMENT": {k: v for k, v in make_valid_scientific().items()},
        }
        signals = detector.detect_cross_artifact_homogenization(blueprints)
        # Genuinely different blueprints should not trigger high similarity
        assert len(signals) == 0

    def test_anti_pattern_detector_quiz_collapse(self):
        """Quiz collapse detection identifies worksheet with only QUESTION stages."""
        detector = BlueprintAntiPatternDetector()
        quiz_blueprint = {
            "activities": [
                {"INQUIRY_STAGE": "QUESTION", "STUDENT_ACTION": "Answer q"},
                {"INQUIRY_STAGE": "QUESTION", "STUDENT_ACTION": "Answer q"},
                {"INQUIRY_STAGE": "QUESTION", "STUDENT_ACTION": "Answer q"},
            ]
        }
        signals = detector.detect_quiz_collapse(quiz_blueprint)
        assert any("WORKSHEET→QUIZ" in s for s in signals)


# ============================================================================
# G. PYTHON COMPATIBILITY TESTS
# ============================================================================

class TestPythonCompatibility:
    def test_python_blueprint_classes_unaffected(self):
        """Existing Python blueprint Pydantic classes still import and instantiate correctly."""
        from app.intelligence.transformation.blueprints import (
            PresentationBlueprint,
            HandoutBlueprint,
            WorksheetBlueprint,
            ScientificDocumentBlueprint,
            ConceptualBeat,
            ExplanatorySection,
            LearningActivity,
            LearningActivityType,
            ScientificArgumentUnit,
            ScientificArgumentRole,
        )
        from app.intelligence.transformation.intent import ArtifactType, get_default_intent

        intent = get_default_intent(ArtifactType.PRESENTATION)
        bp = PresentationBlueprint(
            blueprint_id="test-bp-1",
            artifact_type=ArtifactType.PRESENTATION,
            source_manifest_id="test-manifest",
            document_title="Test",
            intent=intent,
        )
        assert bp.blueprint_id == "test-bp-1"
        assert bp.artifact_type == ArtifactType.PRESENTATION

    def test_differentiation_validator_unaffected(self):
        """ArtifactDifferentiationValidator still works correctly."""
        from app.intelligence.transformation.differentiation_validator import (
            ArtifactDifferentiationValidator,
        )
        from app.intelligence.transformation.blueprints import (
            PresentationBlueprint, HandoutBlueprint,
            WorksheetBlueprint, ScientificDocumentBlueprint,
        )
        from app.intelligence.transformation.intent import ArtifactType, get_default_intent

        p_intent = get_default_intent(ArtifactType.PRESENTATION)
        h_intent = get_default_intent(ArtifactType.HANDOUT)
        w_intent = get_default_intent(ArtifactType.WORKSHEET)
        s_intent = get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT)

        p_bp = PresentationBlueprint(blueprint_id="p", artifact_type=ArtifactType.PRESENTATION, source_manifest_id="m", document_title="T", intent=p_intent)
        h_bp = HandoutBlueprint(blueprint_id="h", artifact_type=ArtifactType.HANDOUT, source_manifest_id="m", document_title="T", intent=h_intent)
        w_bp = WorksheetBlueprint(blueprint_id="w", artifact_type=ArtifactType.WORKSHEET, source_manifest_id="m", document_title="T", intent=w_intent)
        s_bp = ScientificDocumentBlueprint(blueprint_id="s", artifact_type=ArtifactType.SCIENTIFIC_DOCUMENT, source_manifest_id="m", document_title="T", intent=s_intent)

        validator = ArtifactDifferentiationValidator()
        result = validator.validate(p_bp, h_bp, w_bp, s_bp)
        assert result is not None


# ============================================================================
# H. VALIDATION REPORT STRUCTURE TESTS
# ============================================================================

class TestValidationReportStructure:
    def test_validation_report_fields_present(self):
        """BlueprintValidationReport has all required fields."""
        bp = make_valid_presentation()
        report = PresentationBlueprintValidator().validate(bp)
        assert isinstance(report, BlueprintValidationReport)
        assert isinstance(report.is_valid, bool)
        assert 0.0 <= report.completeness_score <= 1.0
        assert 0.0 <= report.artifact_specificity_score <= 1.0
        assert 0.0 <= report.semantic_coherence_score <= 1.0
        assert 0.0 <= report.traceability_score <= 1.0
        assert isinstance(report.anti_pattern_findings, list)
        assert isinstance(report.hard_invariant_violations, list)
        assert isinstance(report.warnings, list)
        assert isinstance(report.missing_required_fields, list)
        assert report.artifact_type == "PRESENTATION"
        assert report.report_id.startswith("bvr_")

    def test_failure_type_enum_coverage(self):
        """BlueprintFailureType covers all required failure types."""
        required = {
            "BLUEPRINT_INCOMPLETE", "ARTIFACT_COLLAPSE_RISK",
            "PRESENTATION_HANDOUT_COLLAPSE", "HANDOUT_SLIDE_FRAGMENTATION",
            "WORKSHEET_QUIZ_COLLAPSE", "WORKSHEET_ANSWER_LEAK",
            "SCIENTIFIC_ARGUMENT_WEAKNESS", "UNSUPPORTED_SCIENTIFIC_CLAIM",
            "MISSING_TRACEABILITY", "UNCERTAINTY_POLICY_VIOLATION",
            "NARRATIVE_DISCONTINUITY", "INQUIRY_ARC_BROKEN",
            "SEMANTIC_FIELD_CONTRADICTION",
        }
        actual = {f.value for f in BlueprintFailureType}
        assert required.issubset(actual)
