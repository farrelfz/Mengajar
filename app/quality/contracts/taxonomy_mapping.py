"""
Universal Document Intelligence System V5 — Canonical Failure Taxonomy Mapping.

Phase 3A.1: Unified taxonomy mappings bridging legacy evaluators, Phase 2B fidelity reports,
Phase 2C calibration reports, and Phase 3A rendered output geometry checkers into
canonical quality codes and domains.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from app.quality.contracts.dimensions import CanonicalQualityDimension
from app.quality.contracts.signals import QualityDomain, SignalSeverity


# =============================================================================
# 1. RENDERED OUTPUT FAILURE CODE MAPPINGS (PHASE 3A -> CANONICAL)
# =============================================================================

RENDERED_CODE_TO_CANONICAL_MAP: Dict[str, str] = {
    "TEXT_CLIPPING": "TEXT_CLIPPING",
    "TEXT_OVERFLOW": "TEXT_OVERFLOW",
    "CONTENT_OVERFLOW": "TEXT_OVERFLOW",
    "OVERLAPPING_CONTENT": "ELEMENT_COLLISION",
    "ELEMENT_COLLISION": "ELEMENT_COLLISION",
    "COLLISION": "ELEMENT_COLLISION",
    "TINY_TEXT": "FONT_TOO_SMALL",
    "FONT_TOO_SMALL": "FONT_TOO_SMALL",
    "UNDERSIZED_FONT": "FONT_TOO_SMALL",
    "EXTREME_WHITESPACE": "UNDERUTILIZED_SPACE",
    "UNDERUTILIZED_SPACE": "UNDERUTILIZED_SPACE",
    "PAGE_COUNT_EXCEEDED": "ACCIDENTAL_PAGE",
    "ACCIDENTAL_PAGE": "ACCIDENTAL_PAGE",
    "ORPHAN_PAGE": "ACCIDENTAL_PAGE",
    "ALMOST_EMPTY_PAGE": "ACCIDENTAL_PAGE",
    "VIEWPORT_BREACH": "MARGIN_VIOLATION",
    "MARGIN_VIOLATION": "MARGIN_VIOLATION",
    "MARGIN_COLLISION": "MARGIN_VIOLATION",
    "LINE_LENGTH_EXCEEDED": "EXCESSIVE_LINE_LENGTH",
    "EXCESSIVE_LINE_LENGTH": "EXCESSIVE_LINE_LENGTH",
    "RENDER_SCALE_FAILURE": "RENDER_SCALE_FAILURE",
}


# =============================================================================
# 2. CALIBRATION & QUALITY FAILURE CODE MAPPINGS (PHASE 2C -> CANONICAL)
# =============================================================================

CALIBRATION_CODE_TO_CANONICAL_MAP: Dict[str, str] = {
    # Presentation
    "EXACT_DUPLICATE_SLIDES": "DUPLICATE_CONTENT",
    "NEAR_DUPLICATE_COMPOSITION": "NEAR_DUPLICATE_CONTENT",
    "FIVE_CONSECUTIVE_IDENTICAL_LAYOUT": "LAYOUT_MONOTONY",
    "REPEATED_GENERIC_CARD": "LAYOUT_MONOTONY",
    "HEADLINE_BODY_RATIO_SMALL": "TYPOGRAPHIC_COLLAPSE",
    "ALL_TEXT_VISUALLY_EQUAL": "TYPOGRAPHIC_COLLAPSE",
    "COMPETING_PRIMARY_ELEMENTS": "VISUAL_HIERARCHY_CONFUSION",
    "EXCESSIVE_DENSITY": "COGNITIVE_OVERLOAD",
    "MORE_THAN_SIX_CARDS": "COGNITIVE_OVERLOAD",
    "PROCESS_AS_CARDS": "LAYOUT_TAXONOMY_MISMATCH",
    "COMPARISON_AS_PARAGRAPH": "LAYOUT_TAXONOMY_MISMATCH",
    "QUESTION_AS_DENSE_EXPLANATION": "PEDAGOGICAL_STRUCTURE_COLLAPSE",
    "CAUSE_EFFECT_UNRELATED": "PEDAGOGICAL_STRUCTURE_COLLAPSE",
    "LONG_STREAK_HIGH_DENSITY": "COGNITIVE_OVERLOAD",
    # Handout
    "HEADING_HIERARCHY_INVERSION": "STRUCTURAL_HIERARCHY_INVERSION",
    "EXTREME_DENSE_PAGE": "COGNITIVE_OVERLOAD",
    "ALMOST_EMPTY_ACCIDENTAL_PAGE": "ACCIDENTAL_PAGE",
    "PARAGRAPH_FRAGMENTATION": "NARRATIVE_FRAGMENTATION",
    "DUPLICATE_EXPLANATORY_BLOCK": "DUPLICATE_CONTENT",
    "TINY_BODY_TEXT": "FONT_TOO_SMALL",
    "CRITICAL_CONCEPT_BURIED": "PEDAGOGICAL_STRUCTURE_COLLAPSE",
    # Worksheet / LKS
    "QUESTION_SEQUENCE_NO_INQUIRY": "INQUIRY_ARC_BROKEN",
    "REFLECTION_BEFORE_OBSERVATION": "INQUIRY_ARC_BROKEN",
    "DATA_ANALYSIS_BEFORE_COLLECTION": "INQUIRY_ARC_BROKEN",
    "PREDICTION_AFTER_EXPLANATION": "INQUIRY_ARC_BROKEN",
    "EXPLANATION_LEAKED_BEFORE_PREDICTION": "ANTI_SPOILING_BREACH",
    "ANSWER_LEAKED_INSIDE_QUESTION": "ANTI_SPOILING_BREACH",
    "OBSERVATION_CONCLUSION_PREFILLED": "ANTI_SPOILING_BREACH",
    "WORKSPACE_TOO_SMALL": "INSUFFICIENT_WORKSPACE",
    "WORKSPACE_DETACHED": "WORKSPACE_DETACHED",
    "NO_OBSERVATION_RECORDING_STRUCTURE": "INSUFFICIENT_WORKSPACE",
    "NO_DATA_ANALYSIS_SPACE": "INSUFFICIENT_WORKSPACE",
    "TEN_CONSECUTIVE_SHORT_ANSWER_QUIZ_COLLAPSE": "QUIZ_COLLAPSE",
    "DOMINATED_BY_MULTIPLE_CHOICE_QUIZ_COLLAPSE": "QUIZ_COLLAPSE",
    "ACTIVITY_HIERARCHY_INVISIBLE": "STRUCTURAL_HIERARCHY_INVERSION",
    "WORKSPACE_OVERLAPS_CONTENT": "ELEMENT_COLLISION",
    "UNEVEN_WORKSPACE_ALLOCATION": "INSUFFICIENT_WORKSPACE",
    # Scientific Document / KTI
    "BAB_HIERARCHY_INVERSION": "STRUCTURAL_HIERARCHY_INVERSION",
    "RESULTS_BEFORE_METHODOLOGY": "SCIENTIFIC_METHODOLOGY_ORDER_INVERSION",
    "CONCLUSION_BEFORE_DISCUSSION": "SCIENTIFIC_METHODOLOGY_ORDER_INVERSION",
    "MISSING_ARGUMENT_TRANSITION": "NARRATIVE_FRAGMENTATION",
    "CLAIM_WITHOUT_EVIDENCE": "UNSUPPORTED_SCIENTIFIC_CLAIM",
    "EVIDENCE_ATTACHED_TO_WRONG_CLAIM": "MISATTRIBUTED_EVIDENCE",
    "UNSUPPORTED_CLAIM_AS_FACT": "UNSUPPORTED_SCIENTIFIC_CLAIM",
    "EVIDENCE_RELATIONSHIP_SILENTLY_REMOVED": "MISATTRIBUTED_EVIDENCE",
    "CITATION_MISSING": "CITATION_MISSING",
    "CITATION_DETACHED": "CITATION_DETACHED",
    "FABRICATED_CITATION_MARKER": "FABRICATED_CITATION",
    "ORPHAN_SUBSECTION": "STRUCTURAL_HIERARCHY_INVERSION",
    "EMPTY_ACADEMIC_SUBSECTION": "STRUCTURAL_HIERARCHY_INVERSION",
    "TABLE_SPLIT": "ELEMENT_COLLISION",
    "FIGURE_CAPTION_DETACHED": "CITATION_DETACHED",
    "DUPLICATE_ARGUMENT": "DUPLICATE_CONTENT",
    "CONTRADICTORY_ADJACENT_CLAIMS": "CONTRADICTORY_CLAIMS",
}


# =============================================================================
# 3. FIDELITY & TRACEABILITY FAILURE CODE MAPPINGS (PHASE 2B -> CANONICAL)
# =============================================================================

FIDELITY_CODE_TO_CANONICAL_MAP: Dict[str, str] = {
    "DROPPED_SOURCE_UNITS": "TRACEABILITY_BREAK",
    "TRACEABILITY_BREAK": "TRACEABILITY_BREAK",
    "UNRESOLVED_SLOTS": "UNRESOLVED_SLOT",
    "UNRESOLVED_SLOT": "UNRESOLVED_SLOT",
    "SLOT_MISMATCH": "UNRESOLVED_SLOT",
    "CAPACITY_OVERFLOW": "COGNITIVE_OVERLOAD",
    "UNRESOLVED_CROSS_REFERENCES": "TRACEABILITY_BREAK",
}


# =============================================================================
# 4. CANONICAL CODE TO DOMAIN MAPPING
# =============================================================================

CANONICAL_CODE_TO_DOMAIN_MAP: Dict[str, QualityDomain] = {
    # Render
    "TEXT_CLIPPING": QualityDomain.RENDERED,
    "TEXT_OVERFLOW": QualityDomain.RENDERED,
    "ELEMENT_COLLISION": QualityDomain.RENDERED,
    "FONT_TOO_SMALL": QualityDomain.RENDERED,
    "UNDERUTILIZED_SPACE": QualityDomain.RENDERED,
    "ACCIDENTAL_PAGE": QualityDomain.RENDERED,
    "MARGIN_VIOLATION": QualityDomain.RENDERED,
    "EXCESSIVE_LINE_LENGTH": QualityDomain.RENDERED,
    "RENDER_SCALE_FAILURE": QualityDomain.RENDERED,
    # Fidelity
    "TRACEABILITY_BREAK": QualityDomain.FIDELITY,
    "UNRESOLVED_SLOT": QualityDomain.FIDELITY,
    # Semantic
    "UNSUPPORTED_SCIENTIFIC_CLAIM": QualityDomain.SEMANTIC,
    "MISATTRIBUTED_EVIDENCE": QualityDomain.SEMANTIC,
    "FABRICATED_CITATION": QualityDomain.SEMANTIC,
    "CONTRADICTORY_CLAIMS": QualityDomain.SEMANTIC,
    "SEMANTIC_FABRICATION": QualityDomain.SEMANTIC,
    # Artifact Quality
    "DUPLICATE_CONTENT": QualityDomain.ARTIFACT,
    "NEAR_DUPLICATE_CONTENT": QualityDomain.ARTIFACT,
    "LAYOUT_MONOTONY": QualityDomain.ARTIFACT,
    "TYPOGRAPHIC_COLLAPSE": QualityDomain.ARTIFACT,
    "VISUAL_HIERARCHY_CONFUSION": QualityDomain.ARTIFACT,
    "COGNITIVE_OVERLOAD": QualityDomain.ARTIFACT,
    "LAYOUT_TAXONOMY_MISMATCH": QualityDomain.ARTIFACT,
    "PEDAGOGICAL_STRUCTURE_COLLAPSE": QualityDomain.ARTIFACT,
    "STRUCTURAL_HIERARCHY_INVERSION": QualityDomain.ARTIFACT,
    "NARRATIVE_FRAGMENTATION": QualityDomain.ARTIFACT,
    "INQUIRY_ARC_BROKEN": QualityDomain.ARTIFACT,
    "ANTI_SPOILING_BREACH": QualityDomain.ARTIFACT,
    "INSUFFICIENT_WORKSPACE": QualityDomain.ARTIFACT,
    "WORKSPACE_DETACHED": QualityDomain.ARTIFACT,
    "QUIZ_COLLAPSE": QualityDomain.ARTIFACT,
    "SCIENTIFIC_METHODOLOGY_ORDER_INVERSION": QualityDomain.ARTIFACT,
    "CITATION_MISSING": QualityDomain.ARTIFACT,
    "CITATION_DETACHED": QualityDomain.ARTIFACT,
}


# =============================================================================
# 5. CANONICAL CODE TO CANONICAL DIMENSION MAPPING
# =============================================================================

CANONICAL_CODE_TO_DIMENSION_MAP: Dict[str, CanonicalQualityDimension] = {
    # Render
    "TEXT_CLIPPING": CanonicalQualityDimension.PHYSICAL_GEOMETRY,
    "TEXT_OVERFLOW": CanonicalQualityDimension.PHYSICAL_GEOMETRY,
    "ELEMENT_COLLISION": CanonicalQualityDimension.PHYSICAL_GEOMETRY,
    "FONT_TOO_SMALL": CanonicalQualityDimension.READABILITY,
    "UNDERUTILIZED_SPACE": CanonicalQualityDimension.PAGE_BALANCE,
    "ACCIDENTAL_PAGE": CanonicalQualityDimension.PAGE_BALANCE,
    "MARGIN_VIOLATION": CanonicalQualityDimension.PHYSICAL_GEOMETRY,
    "EXCESSIVE_LINE_LENGTH": CanonicalQualityDimension.READABILITY,
    "RENDER_SCALE_FAILURE": CanonicalQualityDimension.PHYSICAL_GEOMETRY,
    # Fidelity
    "TRACEABILITY_BREAK": CanonicalQualityDimension.KNOWLEDGE_TRACEABILITY,
    "UNRESOLVED_SLOT": CanonicalQualityDimension.BLUEPRINT_FIDELITY,
    # Semantic
    "UNSUPPORTED_SCIENTIFIC_CLAIM": CanonicalQualityDimension.CLAIM_VERACITY,
    "MISATTRIBUTED_EVIDENCE": CanonicalQualityDimension.CLAIM_VERACITY,
    "FABRICATED_CITATION": CanonicalQualityDimension.SEMANTIC_GROUNDING,
    "CONTRADICTORY_CLAIMS": CanonicalQualityDimension.CLAIM_VERACITY,
    "SEMANTIC_FABRICATION": CanonicalQualityDimension.SEMANTIC_GROUNDING,
    # Artifact Quality
    "DUPLICATE_CONTENT": CanonicalQualityDimension.STYLE_DESIGN,
    "NEAR_DUPLICATE_CONTENT": CanonicalQualityDimension.STYLE_DESIGN,
    "LAYOUT_MONOTONY": CanonicalQualityDimension.STYLE_DESIGN,
    "TYPOGRAPHIC_COLLAPSE": CanonicalQualityDimension.STYLE_DESIGN,
    "VISUAL_HIERARCHY_CONFUSION": CanonicalQualityDimension.STYLE_DESIGN,
    "COGNITIVE_OVERLOAD": CanonicalQualityDimension.COGNITIVE_LOAD,
    "LAYOUT_TAXONOMY_MISMATCH": CanonicalQualityDimension.NARRATIVE_FLOW,
    "PEDAGOGICAL_STRUCTURE_COLLAPSE": CanonicalQualityDimension.NARRATIVE_FLOW,
    "STRUCTURAL_HIERARCHY_INVERSION": CanonicalQualityDimension.SCIENTIFIC_RIGOR,
    "NARRATIVE_FRAGMENTATION": CanonicalQualityDimension.NARRATIVE_FLOW,
    "INQUIRY_ARC_BROKEN": CanonicalQualityDimension.INQUIRY_STRUCTURE,
    "ANTI_SPOILING_BREACH": CanonicalQualityDimension.INQUIRY_STRUCTURE,
    "INSUFFICIENT_WORKSPACE": CanonicalQualityDimension.INQUIRY_STRUCTURE,
    "WORKSPACE_DETACHED": CanonicalQualityDimension.INQUIRY_STRUCTURE,
    "QUIZ_COLLAPSE": CanonicalQualityDimension.INQUIRY_STRUCTURE,
    "SCIENTIFIC_METHODOLOGY_ORDER_INVERSION": CanonicalQualityDimension.SCIENTIFIC_RIGOR,
    "CITATION_MISSING": CanonicalQualityDimension.SCIENTIFIC_RIGOR,
    "CITATION_DETACHED": CanonicalQualityDimension.SCIENTIFIC_RIGOR,
}


# =============================================================================
# 6. LEGACY QUALITY DIMENSION MAPPING
# =============================================================================

LEGACY_DIMENSION_TO_CANONICAL_DOMAIN: Dict[str, QualityDomain] = {
    "SEMANTIC_FIDELITY": QualityDomain.SEMANTIC,
    "STRUCTURAL_INTEGRITY": QualityDomain.FIDELITY,
    "PEDAGOGICAL_ALIGNMENT": QualityDomain.ARTIFACT,
    "INFORMATION_DENSITY": QualityDomain.ARTIFACT,
    "FORMAT_COMPLIANCE": QualityDomain.ARTIFACT,
    "CROSS_ARTIFACT_CONSISTENCY": QualityDomain.ARTIFACT,
    "REDUNDANCY": QualityDomain.ARTIFACT,
}

LEGACY_DIMENSION_TO_CANONICAL_DIMENSION: Dict[str, CanonicalQualityDimension] = {
    "SEMANTIC_FIDELITY": CanonicalQualityDimension.SEMANTIC_GROUNDING,
    "STRUCTURAL_INTEGRITY": CanonicalQualityDimension.BLUEPRINT_FIDELITY,
    "PEDAGOGICAL_ALIGNMENT": CanonicalQualityDimension.NARRATIVE_FLOW,
    "INFORMATION_DENSITY": CanonicalQualityDimension.COGNITIVE_LOAD,
    "FORMAT_COMPLIANCE": CanonicalQualityDimension.CONTRACT_COMPLIANCE,
    "CROSS_ARTIFACT_CONSISTENCY": CanonicalQualityDimension.STYLE_DESIGN,
    "REDUNDANCY": CanonicalQualityDimension.STYLE_DESIGN,
}


# =============================================================================
# 7. PUBLIC LOOKUP FUNCTIONS
# =============================================================================

def map_to_canonical_code(code: str) -> str:
    """Normalize any failure code into canonical failure code."""
    c_up = str(code).strip().upper()
    if c_up in RENDERED_CODE_TO_CANONICAL_MAP:
        return RENDERED_CODE_TO_CANONICAL_MAP[c_up]
    if c_up in CALIBRATION_CODE_TO_CANONICAL_MAP:
        return CALIBRATION_CODE_TO_CANONICAL_MAP[c_up]
    if c_up in FIDELITY_CODE_TO_CANONICAL_MAP:
        return FIDELITY_CODE_TO_CANONICAL_MAP[c_up]
    return c_up


def map_to_canonical_domain(code_or_dim: str) -> QualityDomain:
    """Resolve QualityDomain for a code or legacy dimension."""
    c_str = str(code_or_dim).strip()
    c_up = c_str.upper()

    if c_up in CANONICAL_CODE_TO_DOMAIN_MAP:
        return CANONICAL_CODE_TO_DOMAIN_MAP[c_up]

    canonical_code = map_to_canonical_code(c_up)
    if canonical_code in CANONICAL_CODE_TO_DOMAIN_MAP:
        return CANONICAL_CODE_TO_DOMAIN_MAP[canonical_code]

    if c_up in LEGACY_DIMENSION_TO_CANONICAL_DOMAIN:
        return LEGACY_DIMENSION_TO_CANONICAL_DOMAIN[c_up]

    return QualityDomain.ARTIFACT


def map_to_canonical_dimension(code_or_dim: str) -> CanonicalQualityDimension:
    """Resolve CanonicalQualityDimension for a code or legacy dimension."""
    c_str = str(code_or_dim).strip()
    c_up = c_str.upper()

    if c_up in CANONICAL_CODE_TO_DIMENSION_MAP:
        return CANONICAL_CODE_TO_DIMENSION_MAP[c_up]

    canonical_code = map_to_canonical_code(c_up)
    if canonical_code in CANONICAL_CODE_TO_DIMENSION_MAP:
        return CANONICAL_CODE_TO_DIMENSION_MAP[canonical_code]

    if c_up in LEGACY_DIMENSION_TO_CANONICAL_DIMENSION:
        return LEGACY_DIMENSION_TO_CANONICAL_DIMENSION[c_up]

    return CanonicalQualityDimension.STYLE_DESIGN


def map_legacy_severity(severity: Any) -> SignalSeverity:
    """Maps any legacy or external severity representation to SignalSeverity."""
    if isinstance(severity, SignalSeverity):
        return severity

    sev_str = str(getattr(severity, "name", getattr(severity, "value", severity))).upper()
    if "BLOCK" in sev_str or "CRIT" in sev_str:
        return SignalSeverity.BLOCKING
    if "ERROR" in sev_str or "MAJOR" in sev_str:
        return SignalSeverity.ERROR
    if "WARN" in sev_str or "MINOR" in sev_str:
        return SignalSeverity.WARNING
    return SignalSeverity.INFO
