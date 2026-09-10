"""
Universal Document Intelligence System V5 — Artifact-Specific Blueprint Validators.

Phase 4.1: Deterministic structural validation for each of the four artifact types.
All validation is offline and LLM-free. Emits BlueprintValidationReport signals only.
Does NOT make export decisions (UnifiedQualityAuthority retains that authority).
"""

from __future__ import annotations

import uuid
import time
from typing import Any

from app.intelligence.blueprint_validation.contracts import (
    BlueprintFailureType,
    BlueprintValidationReport,
)
from app.intelligence.blueprint_validation.field_validators import (
    INQUIRY_STAGE_ORDER,
    VALID_CLAIM_TYPES,
    VALID_EVIDENCE_DIRECTNESS,
    VALID_PRESENTATION_ROLES,
    VALID_QUESTION_TAXONOMY,
    VALID_UNCERTAINTY_STATES,
    VALID_VISUAL_GRAMMAR,
    check_density_target,
    check_required_fields,
    check_boolean_field,
    count_field_coverage,
    detect_consecutive_duplicates,
)


# ============================================================================
# 1. PRESENTATION BLUEPRINT VALIDATOR
# ============================================================================

PRESENTATION_REQUIRED_TOP = [
    "PRESENTATION_THESIS", "CENTRAL_QUESTION", "TARGET_AUDIENCE", "slides",
]

PRESENTATION_SLIDE_REQUIRED = [
    "SLIDE_ID", "SEMANTIC_ROLE", "CORE_MESSAGE", "VISUAL_GRAMMAR",
    "COGNITIVE_LOAD_TARGET", "HANDOUT_COLLAPSE_RISK",
]

NARRATIVE_ARC_ROLES = {"HOOK", "SYNTHESIS", "REFLECTION", "SUMMARY", "CALL_TO_ACTION"}


class PresentationBlueprintValidator:
    """Validates Markdown-derived Presentation blueprint dicts."""

    ARTIFACT_TYPE = "PRESENTATION"

    def validate(self, blueprint_dict: dict) -> BlueprintValidationReport:
        violations: list[str] = []
        warnings: list[str] = []
        missing_fields: list[str] = []
        anti_patterns: list[str] = []

        # 1. Top-level completeness
        ok, missing = check_required_fields(blueprint_dict, PRESENTATION_REQUIRED_TOP)
        if not ok:
            missing_fields.extend(missing)

        slides = blueprint_dict.get("slides", [])

        # 2. Minimum slide count
        if len(slides) < 3:
            violations.append(f"Presentation has only {len(slides)} slides — minimum is 3.")

        # 3. Slide-level field completeness
        for i, slide in enumerate(slides):
            ok, missing = check_required_fields(slide, PRESENTATION_SLIDE_REQUIRED)
            if not ok:
                missing_fields.extend([f"slide[{i}].{f}" for f in missing])

        # 4. Narrative arc validation — must have at least one opening & closing role
        if slides:
            roles = [str(s.get("SEMANTIC_ROLE", "")).upper() for s in slides]
            opening_roles = {"HOOK", "PHENOMENON", "QUESTION", "PROBLEM"}
            closing_roles = {"SYNTHESIS", "REFLECTION", "SUMMARY", "CALL_TO_ACTION"}
            if not any(r in opening_roles for r in roles):
                violations.append(
                    f"[{BlueprintFailureType.NARRATIVE_DISCONTINUITY.value}] "
                    "No opening arc role found (HOOK/PHENOMENON/QUESTION/PROBLEM)."
                )
            if not any(r in closing_roles for r in roles):
                warnings.append(
                    "No closing arc role found (SYNTHESIS/REFLECTION/SUMMARY/CALL_TO_ACTION)."
                )

        # 5. Visual grammar monotony — consecutive identical grammar
        grammar_streaks = detect_consecutive_duplicates(slides, "VISUAL_GRAMMAR", threshold=3)
        if grammar_streaks:
            anti_patterns.extend(grammar_streaks)

        # 6. Cognitive load target — check for handout territory (avg > 0.65)
        load_values = [
            s.get("COGNITIVE_LOAD_TARGET") for s in slides
            if isinstance(s.get("COGNITIVE_LOAD_TARGET"), (int, float))
        ]
        if load_values:
            avg_load = sum(load_values) / len(load_values)
            if avg_load > 0.65:
                violations.append(
                    f"[{BlueprintFailureType.PRESENTATION_HANDOUT_COLLAPSE.value}] "
                    f"Average cognitive load {avg_load:.2f} > 0.65 — presentation is in handout territory."
                )

        # 7. Handout collapse risk — too many slides at risk
        collapse_flags = [
            s for s in slides
            if s.get("HANDOUT_COLLAPSE_RISK") is True
        ]
        if slides and len(collapse_flags) / max(len(slides), 1) > 0.3:
            anti_patterns.append(
                f"[{BlueprintFailureType.PRESENTATION_HANDOUT_COLLAPSE.value}] "
                f"{len(collapse_flags)}/{len(slides)} slides flagged HANDOUT_COLLAPSE_RISK=True (>30%)."
            )

        # 8. Missing WHY_THIS_SLIDE_EXISTS — wall-of-text / unjustified slides
        unjustified = [
            i for i, s in enumerate(slides)
            if not s.get("WHY_THIS_SLIDE_EXISTS")
        ]
        if len(unjustified) > len(slides) * 0.5:
            anti_patterns.append(
                f"[WALL_OF_TEXT risk] {len(unjustified)} slides missing WHY_THIS_SLIDE_EXISTS justification."
            )

        # Scoring
        field_completeness = 1.0 - (len(missing_fields) / max(1, len(PRESENTATION_REQUIRED_TOP) + len(slides) * len(PRESENTATION_SLIDE_REQUIRED)))
        specificity = 1.0 if not violations else max(0.0, 1.0 - len(violations) * 0.2)
        coherence = 1.0 if not anti_patterns else max(0.0, 1.0 - len(anti_patterns) * 0.15)
        traceability = count_field_coverage(slides, "KNOWLEDGE_UNITS_USED")

        is_valid = len(violations) == 0 and len(missing_fields) == 0

        return BlueprintValidationReport(
            artifact_type=self.ARTIFACT_TYPE,
            is_valid=is_valid,
            completeness_score=max(0.0, min(1.0, field_completeness)),
            artifact_specificity_score=max(0.0, min(1.0, specificity)),
            semantic_coherence_score=max(0.0, min(1.0, coherence)),
            traceability_score=max(0.0, min(1.0, traceability)),
            anti_pattern_findings=anti_patterns,
            hard_invariant_violations=violations,
            warnings=warnings,
            missing_required_fields=missing_fields,
        )


# ============================================================================
# 2. HANDOUT BLUEPRINT VALIDATOR
# ============================================================================

HANDOUT_REQUIRED_TOP = [
    "READING_PURPOSE", "TARGET_READER", "INDEPENDENT_COMPREHENSION_TARGET", "sections",
]

HANDOUT_SECTION_REQUIRED = [
    "SECTION_ID", "SECTION_PURPOSE", "KNOWLEDGE_UNITS_USED",
    "TRANSITION_FROM_PREVIOUS", "TRANSITION_TO_NEXT",
]


class HandoutBlueprintValidator:
    """Validates Markdown-derived Handout blueprint dicts."""

    ARTIFACT_TYPE = "HANDOUT"

    def validate(self, blueprint_dict: dict) -> BlueprintValidationReport:
        violations: list[str] = []
        warnings: list[str] = []
        missing_fields: list[str] = []
        anti_patterns: list[str] = []

        # 1. Top-level completeness
        ok, missing = check_required_fields(blueprint_dict, HANDOUT_REQUIRED_TOP)
        if not ok:
            missing_fields.extend(missing)

        sections = blueprint_dict.get("sections", [])

        # 2. Section completeness
        for i, sec in enumerate(sections):
            ok, missing = check_required_fields(sec, HANDOUT_SECTION_REQUIRED)
            if not ok:
                missing_fields.extend([f"section[{i}].{f}" for f in missing])

        # 3. Independent readability — must have explanation layer coverage
        layer_fields = [
            "LAYER_1_INTUITION", "LAYER_2_FORMAL_EXPLANATION",
            "LAYER_3_MECHANISM", "LAYER_4_EXAMPLE",
        ]
        for i, sec in enumerate(sections):
            covered = sum(1 for lf in layer_fields if sec.get(lf))
            if covered < 2:
                warnings.append(
                    f"section[{i}] has only {covered}/4 explanation layers — "
                    "independent comprehension may be insufficient."
                )

        # 4. Wall-of-text risk
        wall_of_text = [i for i, s in enumerate(sections) if s.get("WALL_OF_TEXT_RISK") is True]
        if wall_of_text:
            anti_patterns.append(
                f"[{BlueprintFailureType.HANDOUT_SLIDE_FRAGMENTATION.value}] "
                f"Sections {wall_of_text} flagged WALL_OF_TEXT_RISK=True."
            )

        # 5. Slide fragmentation detection — too many micro-sections with thin content
        if len(sections) > 12:
            thin_sections = [
                i for i, s in enumerate(sections)
                if len([k for k, v in s.items() if v and k != "SECTION_ID"]) < 4
            ]
            if len(thin_sections) > len(sections) * 0.4:
                anti_patterns.append(
                    f"[{BlueprintFailureType.HANDOUT_SLIDE_FRAGMENTATION.value}] "
                    f"{len(thin_sections)} thin micro-sections detected — possible slide-to-handout collapse."
                )

        # 6. Missing transitions
        missing_transitions = []
        for i, sec in enumerate(sections):
            if i > 0 and not sec.get("TRANSITION_FROM_PREVIOUS"):
                missing_transitions.append(i)
            if i < len(sections) - 1 and not sec.get("TRANSITION_TO_NEXT"):
                missing_transitions.append(i)
        if missing_transitions:
            violations.append(
                f"Sections {list(set(missing_transitions))} are missing transition fields — "
                "handout requires explicit reading flow."
            )

        # Scoring
        field_completeness = 1.0 - (len(missing_fields) / max(1, len(HANDOUT_REQUIRED_TOP) + len(sections) * len(HANDOUT_SECTION_REQUIRED)))
        specificity = 1.0 if not violations else max(0.0, 1.0 - len(violations) * 0.2)
        coherence = 1.0 if not anti_patterns else max(0.0, 1.0 - len(anti_patterns) * 0.2)
        traceability = count_field_coverage(sections, "KNOWLEDGE_UNITS_USED")

        is_valid = len(violations) == 0 and len(missing_fields) == 0

        return BlueprintValidationReport(
            artifact_type=self.ARTIFACT_TYPE,
            is_valid=is_valid,
            completeness_score=max(0.0, min(1.0, field_completeness)),
            artifact_specificity_score=max(0.0, min(1.0, specificity)),
            semantic_coherence_score=max(0.0, min(1.0, coherence)),
            traceability_score=max(0.0, min(1.0, traceability)),
            anti_pattern_findings=anti_patterns,
            hard_invariant_violations=violations,
            warnings=warnings,
            missing_required_fields=missing_fields,
        )


# ============================================================================
# 3. WORKSHEET BLUEPRINT VALIDATOR
# ============================================================================

WORKSHEET_REQUIRED_TOP = [
    "CENTRAL_INVESTIGATIVE_QUESTION", "INQUIRY_DEPTH", "activities",
]

WORKSHEET_ACTIVITY_REQUIRED = [
    "ACTIVITY_ID", "INQUIRY_STAGE", "STUDENT_ACTION",
    "WITHHOLD_EXPLANATION", "ANSWER_LEAK_RISK", "WORKSPACE_JUSTIFICATION",
]

# Inquiry stages that MUST withhold explanations
INVESTIGATION_STAGES = {
    "PHENOMENON", "OBSERVATION", "PREDICTION", "HYPOTHESIS",
    "INVESTIGATION", "DATA_COLLECTION",
}


class WorksheetBlueprintValidator:
    """Validates Markdown-derived Worksheet blueprint dicts."""

    ARTIFACT_TYPE = "WORKSHEET"

    def validate(self, blueprint_dict: dict) -> BlueprintValidationReport:
        violations: list[str] = []
        warnings: list[str] = []
        missing_fields: list[str] = []
        anti_patterns: list[str] = []

        # 1. Top-level completeness
        ok, missing = check_required_fields(blueprint_dict, WORKSHEET_REQUIRED_TOP)
        if not ok:
            missing_fields.extend(missing)

        activities = blueprint_dict.get("activities", [])

        # 2. Activity completeness
        for i, act in enumerate(activities):
            ok, missing = check_required_fields(act, WORKSHEET_ACTIVITY_REQUIRED)
            if not ok:
                missing_fields.extend([f"activity[{i}].{f}" for f in missing])

        # 3. HARD INVARIANT: Answer leak detection
        # Any investigation-stage activity must have WITHHOLD_EXPLANATION=True and ANSWER_LEAK_RISK=False
        for i, act in enumerate(activities):
            stage = str(act.get("INQUIRY_STAGE", "")).upper()
            if stage in INVESTIGATION_STAGES:
                if act.get("WITHHOLD_EXPLANATION") is not True:
                    violations.append(
                        f"[{BlueprintFailureType.WORKSHEET_ANSWER_LEAK.value}] "
                        f"activity[{i}] (stage={stage}): WITHHOLD_EXPLANATION must be True."
                    )
                if act.get("ANSWER_LEAK_RISK") is True:
                    violations.append(
                        f"[{BlueprintFailureType.WORKSHEET_ANSWER_LEAK.value}] "
                        f"activity[{i}] (stage={stage}): ANSWER_LEAK_RISK is True — answers may be exposed."
                    )

        # 4. Quiz collapse detection — all activities are QUESTION type with no inquiry variety
        if activities:
            question_taxonomy_vals = [
                str(a.get("QUESTION_TAXONOMY", "")).upper() for a in activities
                if a.get("QUESTION_TAXONOMY")
            ]
            if len(question_taxonomy_vals) >= 3:
                unique_types = set(question_taxonomy_vals)
                if len(unique_types) == 1 and "OBSERVATIONAL" not in unique_types:
                    anti_patterns.append(
                        f"[{BlueprintFailureType.WORKSHEET_QUIZ_COLLAPSE.value}] "
                        f"All {len(question_taxonomy_vals)} activities share identical QUESTION_TAXONOMY "
                        f"'{unique_types.pop()}' — quiz collapse detected."
                    )

        # 5. Inquiry arc causal order — CONCLUSION must not precede REASONING/DATA_ANALYSIS
        stage_sequence = [
            str(a.get("INQUIRY_STAGE", "")).upper()
            for a in activities if a.get("INQUIRY_STAGE")
        ]
        if stage_sequence:
            conclusion_indices = [i for i, s in enumerate(stage_sequence) if s == "CONCLUSION"]
            reasoning_indices = [i for i, s in enumerate(stage_sequence) if s in {"DATA_ANALYSIS", "REASONING"}]
            for ci in conclusion_indices:
                if not any(ri < ci for ri in reasoning_indices):
                    violations.append(
                        f"[{BlueprintFailureType.INQUIRY_ARC_BROKEN.value}] "
                        f"CONCLUSION at position {ci} precedes DATA_ANALYSIS/REASONING — "
                        "inquiry arc causality broken."
                    )

        # 6. Workspace justification
        missing_workspace = [
            i for i, a in enumerate(activities)
            if a.get("WORKSPACE_REQUIREMENT") and not a.get("WORKSPACE_JUSTIFICATION")
        ]
        if missing_workspace:
            warnings.append(
                f"activities {missing_workspace} have WORKSPACE_REQUIREMENT but no WORKSPACE_JUSTIFICATION."
            )

        # Scoring
        field_completeness = 1.0 - (len(missing_fields) / max(1, len(WORKSHEET_REQUIRED_TOP) + len(activities) * len(WORKSHEET_ACTIVITY_REQUIRED)))
        specificity = 1.0 if not violations else max(0.0, 1.0 - len(violations) * 0.25)
        coherence = 1.0 if not anti_patterns else max(0.0, 1.0 - len(anti_patterns) * 0.25)
        traceability = count_field_coverage(activities, "KNOWLEDGE_UNITS_USED")

        is_valid = len(violations) == 0 and len(missing_fields) == 0

        return BlueprintValidationReport(
            artifact_type=self.ARTIFACT_TYPE,
            is_valid=is_valid,
            completeness_score=max(0.0, min(1.0, field_completeness)),
            artifact_specificity_score=max(0.0, min(1.0, specificity)),
            semantic_coherence_score=max(0.0, min(1.0, coherence)),
            traceability_score=max(0.0, min(1.0, traceability)),
            anti_pattern_findings=anti_patterns,
            hard_invariant_violations=violations,
            warnings=warnings,
            missing_required_fields=missing_fields,
        )


# ============================================================================
# 4. SCIENTIFIC DOCUMENT BLUEPRINT VALIDATOR
# ============================================================================

SCIENTIFIC_REQUIRED_TOP = [
    "RESEARCH_PROBLEM", "RESEARCH_QUESTION", "ARGUMENT_THESIS", "arguments",
]

SCIENTIFIC_ARGUMENT_REQUIRED = [
    "ARGUMENT_UNIT_ID", "CLAIM", "CLAIM_TYPE", "EVIDENCE_TYPE",
    "UNCERTAINTY_STATE", "LIMITATION", "FORBIDDEN_FABRICATION_CHECK",
]


class ScientificDocumentBlueprintValidator:
    """Validates Markdown-derived Scientific Document (KTI) blueprint dicts."""

    ARTIFACT_TYPE = "SCIENTIFIC_DOCUMENT"

    def validate(self, blueprint_dict: dict) -> BlueprintValidationReport:
        violations: list[str] = []
        warnings: list[str] = []
        missing_fields: list[str] = []
        anti_patterns: list[str] = []

        # 1. Top-level completeness
        ok, missing = check_required_fields(blueprint_dict, SCIENTIFIC_REQUIRED_TOP)
        if not ok:
            missing_fields.extend(missing)

        arguments = blueprint_dict.get("arguments", [])

        # 2. Argument completeness
        for i, arg in enumerate(arguments):
            ok, missing = check_required_fields(arg, SCIENTIFIC_ARGUMENT_REQUIRED)
            if not ok:
                missing_fields.extend([f"argument[{i}].{f}" for f in missing])

        # 3. HARD INVARIANT: Forbidden fabrication check must be True on all arguments
        for i, arg in enumerate(arguments):
            ffc = arg.get("FORBIDDEN_FABRICATION_CHECK")
            if ffc is not True:
                violations.append(
                    f"[{BlueprintFailureType.UNSUPPORTED_SCIENTIFIC_CLAIM.value}] "
                    f"argument[{i}]: FORBIDDEN_FABRICATION_CHECK must be True "
                    f"(got '{ffc}'). Fabrication was not checked."
                )

        # 4. Claim-Evidence linkage — every claim needs evidence
        for i, arg in enumerate(arguments):
            claim = arg.get("CLAIM")
            evidence = arg.get("EVIDENCE")
            if claim and not evidence:
                violations.append(
                    f"[{BlueprintFailureType.UNSUPPORTED_SCIENTIFIC_CLAIM.value}] "
                    f"argument[{i}]: CLAIM '{str(claim)[:50]}' has no EVIDENCE."
                )

        # 5. Inference-as-fact detection
        # CLAIM_TYPE=CAUSAL + EVIDENCE_DIRECTNESS=INFERRED is a contradiction
        for i, arg in enumerate(arguments):
            claim_type = str(arg.get("CLAIM_TYPE", "")).upper()
            ev_directness = str(arg.get("EVIDENCE_DIRECTNESS", "")).upper()
            if claim_type == "CAUSAL" and ev_directness in {"INFERRED", "SECONDARY"}:
                violations.append(
                    f"[{BlueprintFailureType.SEMANTIC_FIELD_CONTRADICTION.value}] "
                    f"argument[{i}]: CLAIM_TYPE=CAUSAL with EVIDENCE_DIRECTNESS={ev_directness} "
                    "is invalid — causal claims require direct or derived evidence."
                )

        # 6. Uncertainty state must be populated
        for i, arg in enumerate(arguments):
            unc = str(arg.get("UNCERTAINTY_STATE", "")).upper()
            if unc not in VALID_UNCERTAINTY_STATES:
                violations.append(
                    f"[{BlueprintFailureType.UNCERTAINTY_POLICY_VIOLATION.value}] "
                    f"argument[{i}]: UNCERTAINTY_STATE '{unc}' is not valid. "
                    f"Must be one of: {VALID_UNCERTAINTY_STATES}"
                )

        # 7. Limitation presence
        missing_limitations = [
            i for i, arg in enumerate(arguments) if not arg.get("LIMITATION")
        ]
        if missing_limitations:
            warnings.append(
                f"arguments {missing_limitations} are missing LIMITATION — "
                "epistemic boundaries should be explicit."
            )

        # 8. Narrative essay collapse — detect if no arguments have EVIDENCE_TYPE populated
        typed_args = [a for a in arguments if a.get("EVIDENCE_TYPE")]
        if arguments and len(typed_args) / len(arguments) < 0.5:
            anti_patterns.append(
                f"[{BlueprintFailureType.SCIENTIFIC_ARGUMENT_WEAKNESS.value}] "
                f"Only {len(typed_args)}/{len(arguments)} arguments have EVIDENCE_TYPE — "
                "possible narrative essay collapse."
            )

        # Scoring
        field_completeness = 1.0 - (len(missing_fields) / max(1, len(SCIENTIFIC_REQUIRED_TOP) + len(arguments) * len(SCIENTIFIC_ARGUMENT_REQUIRED)))
        specificity = 1.0 if not violations else max(0.0, 1.0 - len(violations) * 0.2)
        coherence = 1.0 if not anti_patterns else max(0.0, 1.0 - len(anti_patterns) * 0.25)
        traceability = count_field_coverage(arguments, "SOURCE_TRACEABILITY")

        is_valid = len(violations) == 0 and len(missing_fields) == 0

        return BlueprintValidationReport(
            artifact_type=self.ARTIFACT_TYPE,
            is_valid=is_valid,
            completeness_score=max(0.0, min(1.0, field_completeness)),
            artifact_specificity_score=max(0.0, min(1.0, specificity)),
            semantic_coherence_score=max(0.0, min(1.0, coherence)),
            traceability_score=max(0.0, min(1.0, traceability)),
            anti_pattern_findings=anti_patterns,
            hard_invariant_violations=violations,
            warnings=warnings,
            missing_required_fields=missing_fields,
        )
