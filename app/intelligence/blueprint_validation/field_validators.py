"""
Universal Document Intelligence System V5 — Blueprint Field Validators.

Phase 4.1: Deterministic, offline field-level validation primitives.
NO LLM calls. All validation is structural and rule-based.
"""

from __future__ import annotations
from typing import Any


# Information density thresholds by artifact type
DENSITY_THRESHOLDS = {
    "PRESENTATION": (0.15, 0.55),
    "HANDOUT": (0.50, 0.90),
    "WORKSHEET": (0.35, 0.70),
    "SCIENTIFIC_DOCUMENT": (0.65, 1.0),
}

# Valid semantic roles for presentations
VALID_PRESENTATION_ROLES = {
    "HOOK", "PHENOMENON", "QUESTION", "PROBLEM", "INTUITION",
    "CONCEPT", "DEFINITION", "VISUAL_EXPLANATION", "MECHANISM",
    "PROCESS", "COMPARISON", "CAUSE_EFFECT", "MODEL", "EQUATION",
    "DERIVATION", "EXAMPLE", "APPLICATION", "EXPERIMENT",
    "DATA_INTERPRETATION", "MISCONCEPTION", "CONNECTION",
    "SYNTHESIS", "REFLECTION", "SUMMARY", "CALL_TO_ACTION",
}

# Valid visual grammar types
VALID_VISUAL_GRAMMAR = {
    "CONCEPT", "COMPARISON", "PROCESS", "CAUSE_EFFECT", "TIMELINE",
    "HIERARCHY", "SYSTEM", "EQUATION", "EXPERIMENT", "DATA_STORY",
    "QUESTION", "PROBLEM", "SYNTHESIS", "DOMINANT_IMAGE",
}

# Valid question taxonomy for worksheets
VALID_QUESTION_TAXONOMY = {
    "OBSERVATIONAL", "PREDICTIVE", "COMPARATIVE", "CAUSAL",
    "ANALYTICAL", "EVIDENCE_BASED", "REFLECTIVE", "METACOGNITIVE",
}

# Valid claim types for scientific documents
VALID_CLAIM_TYPES = {
    "OBSERVATIONAL", "DESCRIPTIVE", "CORRELATIONAL",
    "CAUSAL", "THEORETICAL", "INFERENTIAL",
}

# Valid evidence directness
VALID_EVIDENCE_DIRECTNESS = {
    "DIRECT", "INDIRECT", "DERIVED", "SECONDARY", "INFERRED",
}

# Valid uncertainty states
VALID_UNCERTAINTY_STATES = {
    "KNOWN", "SUPPORTED", "INFERRED", "UNCERTAIN", "UNRESOLVED",
}

# Valid inquiry stages (ordered for causal validation)
INQUIRY_STAGE_ORDER = [
    "PHENOMENON", "OBSERVATION", "QUESTION", "PREDICTION",
    "HYPOTHESIS", "INVESTIGATION", "DATA_COLLECTION",
    "DATA_ANALYSIS", "REASONING", "CONCLUSION", "REFLECTION", "TRANSFER",
]


def check_required_fields(blueprint_dict: dict, required: list[str]) -> tuple[bool, list[str]]:
    """Returns (all_present, missing_fields)."""
    missing = [f for f in required if f not in blueprint_dict or blueprint_dict[f] is None]
    return len(missing) == 0, missing


def check_boolean_field(blueprint_dict: dict, field: str, expected: bool) -> tuple[bool, str]:
    """Validates a boolean field matches expected value."""
    val = blueprint_dict.get(field)
    if val is None:
        return False, f"Field '{field}' is missing."
    if val != expected:
        return False, f"Field '{field}' expected {expected}, got {val}."
    return True, ""


def check_enum_field(blueprint_dict: dict, field: str, allowed: set[str]) -> tuple[bool, str]:
    """Validates a string field is within allowed enum values."""
    val = blueprint_dict.get(field)
    if val is None:
        return False, f"Field '{field}' is missing."
    if str(val).upper() not in allowed:
        return False, f"Field '{field}' value '{val}' is not in allowed values: {allowed}."
    return True, ""


def check_density_target(value: Any, artifact_type: str) -> tuple[bool, str]:
    """Validates information density is within expected range for the artifact type."""
    if value is None:
        return False, "INFORMATION_DENSITY_TARGET is missing."
    try:
        v = float(value)
    except (TypeError, ValueError):
        return False, f"INFORMATION_DENSITY_TARGET must be numeric, got: {value}"

    low, high = DENSITY_THRESHOLDS.get(artifact_type.upper(), (0.0, 1.0))
    if not (low <= v <= high):
        return False, (
            f"INFORMATION_DENSITY_TARGET {v:.2f} is outside expected range "
            f"[{low}, {high}] for {artifact_type}."
        )
    return True, ""


def count_field_coverage(items: list[dict], field: str) -> float:
    """Returns fraction of items that have non-empty value for field."""
    if not items:
        return 0.0
    present = sum(1 for item in items if item.get(field) not in (None, "", False))
    return present / len(items)


def detect_consecutive_duplicates(items: list[dict], field: str, threshold: int = 3) -> list[str]:
    """Detects runs of >threshold identical values for a field across sequential items."""
    violations = []
    streak = 1
    for i in range(1, len(items)):
        if items[i].get(field) == items[i - 1].get(field) and items[i].get(field):
            streak += 1
            if streak > threshold:
                violations.append(
                    f"Consecutive {field} streak of {streak} identical values at index {i}: "
                    f"'{items[i].get(field)}'"
                )
        else:
            streak = 1
    return violations
