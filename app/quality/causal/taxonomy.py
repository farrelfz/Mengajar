"""
Universal Document Intelligence System V5 — Canonical Quality Failure Taxonomy.

Phase 3A.2: Unified taxonomy for failure domains, canonical failure codes,
severities, detection/causal confidence levels, architectural layers, scopes,
and repair action classes.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Set


class CanonicalFailureDomain(str, Enum):
    """The 10 canonical failure domains governing document quality."""
    PHYSICAL_RENDER = "PHYSICAL_RENDER"
    BLUEPRINT_INTEGRITY = "BLUEPRINT_INTEGRITY"
    SEMANTIC_TRACEABILITY = "SEMANTIC_TRACEABILITY"
    PEDAGOGICAL_STRUCTURE = "PEDAGOGICAL_STRUCTURE"
    COGNITIVE_LOAD = "COGNITIVE_LOAD"
    STYLE_DESIGN = "STYLE_DESIGN"
    SCIENTIFIC_RIGOR = "SCIENTIFIC_RIGOR"
    ACCESSIBILITY = "ACCESSIBILITY"
    EXECUTION_CONTRACT = "EXECUTION_CONTRACT"
    EXPORT_PACKAGING = "EXPORT_PACKAGING"


class CanonicalSeverity(str, Enum):
    """Standardized failure severity levels with strict ranking."""
    INFO = "INFO"
    WARNING = "WARNING"
    MINOR = "MINOR"
    MAJOR = "MAJOR"
    CRITICAL = "CRITICAL"
    BLOCKING = "BLOCKING"

    def _rank(self) -> int:
        ranks = {
            CanonicalSeverity.INFO: 0,
            CanonicalSeverity.WARNING: 1,
            CanonicalSeverity.MINOR: 2,
            CanonicalSeverity.MAJOR: 3,
            CanonicalSeverity.CRITICAL: 4,
            CanonicalSeverity.BLOCKING: 5,
        }
        return ranks.get(self, 0)

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, CanonicalSeverity):
            return self._rank() < other._rank()
        return NotImplemented

    def __le__(self, other: Any) -> bool:
        if isinstance(other, CanonicalSeverity):
            return self._rank() <= other._rank()
        return NotImplemented

    def __gt__(self, other: Any) -> bool:
        if isinstance(other, CanonicalSeverity):
            return self._rank() > other._rank()
        return NotImplemented

    def __ge__(self, other: Any) -> bool:
        if isinstance(other, CanonicalSeverity):
            return self._rank() >= other._rank()
        return NotImplemented


# Backward-compatible alias for Phase 3A.1
CanonicalFailureSeverity = CanonicalSeverity


class DetectionConfidence(str, Enum):
    """Confidence that a detected symptom/defect physically or structurally exists."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class CausalConfidence(str, Enum):
    """Confidence in root cause hypothesis attribution."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"
    AMBIGUOUS = "AMBIGUOUS"  # Backward compatibility with Phase 3A.1


# Backward-compatible alias for Phase 3A.1
CausalConfidenceLevel = CausalConfidence


class FailureScope(str, Enum):
    """Spatial and structural breadth of a failure across an artifact."""
    LOCAL = "LOCAL"                 # Isolated to 1-2 pages/elements (<= 15% of document)
    CLUSTER = "CLUSTER"             # Consecutive streak of pages (e.g. 3-5 slides/pages)
    SYSTEMIC = "SYSTEMIC"           # Spread across majority of pages (> 50% of document)
    ARTIFACT_WIDE = "ARTIFACT_WIDE" # Document-level structural defect (citations, cover, template)


class CanonicalFailureCategory(str, Enum):
    """Universal high-level categories of document flaws (Phase 3A.1 compatibility)."""
    SOURCE_SEMANTIC = "SOURCE_SEMANTIC"
    TRANSFORMATION = "TRANSFORMATION"
    BLUEPRINT = "BLUEPRINT"
    LAYOUT = "LAYOUT"
    RENDER = "RENDER"
    DENSITY = "DENSITY"
    ARTIFACT_SPECIFIC = "ARTIFACT_SPECIFIC"


class ArchitectureLayer(str, Enum):
    """The 10 distinct architectural layers in the document production pipeline."""
    SOURCE = "SOURCE"
    SEMANTIC = "SEMANTIC"
    TRANSFORMATION = "TRANSFORMATION"
    SELECTION = "SELECTION"
    BLUEPRINT = "BLUEPRINT"
    LAYOUT = "LAYOUT"
    COMPOSITION = "COMPOSITION"
    TYPOGRAPHY = "TYPOGRAPHY"
    RENDER = "RENDER"
    ARTIFACT_POLICY = "ARTIFACT_POLICY"


class CanonicalRepairClass(str, Enum):
    """Standardized repair action classes for future Phase 3B engine."""
    CLASS_A_GEOMETRY = "CLASS_A_GEOMETRY"
    CLASS_B_TYPOGRAPHY = "CLASS_B_TYPOGRAPHY"
    CLASS_C_LAYOUT_REMAPPING = "CLASS_C_LAYOUT_REMAPPING"
    CLASS_D_BLUEPRINT_REGROUPING = "CLASS_D_BLUEPRINT_REGROUPING"
    CLASS_E_TRANSFORMATION_STRATEGY = "CLASS_E_TRANSFORMATION_STRATEGY"
    CLASS_F_ARTIFACT_POLICY = "CLASS_F_ARTIFACT_POLICY"
    CLASS_G_MANUAL_REVIEW = "CLASS_G_MANUAL_REVIEW"
    NONE = "NONE"


class UnifiedDecisionStatus(str, Enum):
    """Canonical lifecycle status issued by UnifiedQualityAuthority."""
    PASS = "PASS"
    PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
    NEEDS_REPAIR = "NEEDS_REPAIR"
    BLOCKED = "BLOCKED"


class CanonicalFailureCode(str, Enum):
    """Single-source-of-truth failure codes across all failure domains."""
    # 1. PHYSICAL_RENDER
    TEXT_CLIPPING = "TEXT_CLIPPING"
    ELEMENT_COLLISION = "ELEMENT_COLLISION"
    TEXT_TOO_SMALL = "TEXT_TOO_SMALL"
    PAGE_BOUNDARY_VIOLATION = "PAGE_BOUNDARY_VIOLATION"
    RENDER_SCALE_FAILURE = "RENDER_SCALE_FAILURE"
    BLANK_PAGE = "BLANK_PAGE"
    MARGIN_INCONSISTENCY = "MARGIN_INCONSISTENCY"
    OVERFLOW_HIDDEN_CUTOFF = "OVERFLOW_HIDDEN_CUTOFF"
    RENDER_TIMEOUT = "RENDER_TIMEOUT"

    # 2. BLUEPRINT_INTEGRITY
    BLUEPRINT_CAPACITY_MISMATCH = "BLUEPRINT_CAPACITY_MISMATCH"
    NARRATIVE_FRAGMENTATION = "NARRATIVE_FRAGMENTATION"
    UNRESOLVED_SLOT = "UNRESOLVED_SLOT"
    EMPTY_SECTION = "EMPTY_SECTION"
    SLOT_TYPE_MISMATCH = "SLOT_TYPE_MISMATCH"

    # 3. SEMANTIC_TRACEABILITY
    SOURCE_GROUNDING_FAILURE = "SOURCE_GROUNDING_FAILURE"
    UNSUPPORTED_CLAIM = "UNSUPPORTED_CLAIM"
    TRACEABILITY_BREAK = "TRACEABILITY_BREAK"
    EVIDENCE_DISCIPLINE_FAILURE = "EVIDENCE_DISCIPLINE_FAILURE"

    # 4. PEDAGOGICAL_STRUCTURE
    INQUIRY_FLOW_BREAK = "INQUIRY_FLOW_BREAK"
    PRESENTATION_HANDOUT_COLLAPSE = "PRESENTATION_HANDOUT_COLLAPSE"
    PRESENTATION_RHYTHM_FAILURE = "PRESENTATION_RHYTHM_FAILURE"
    PRESENTATION_DUPLICATE_SEQUENCE = "PRESENTATION_DUPLICATE_SEQUENCE"
    HANDOUT_READING_FLOW_FAILURE = "HANDOUT_READING_FLOW_FAILURE"
    HANDOUT_FRAGMENTATION = "HANDOUT_FRAGMENTATION"
    HANDOUT_PAGE_BALANCE_FAILURE = "HANDOUT_PAGE_BALANCE_FAILURE"
    ORPHAN_HEADING = "ORPHAN_HEADING"
    WORKSHEET_QUIZ_COLLAPSE = "WORKSHEET_QUIZ_COLLAPSE"
    WORKSHEET_WORKSPACE_FAILURE = "WORKSHEET_WORKSPACE_FAILURE"
    WORKSHEET_WORKSPACE_INSUFFICIENT = "WORKSHEET_WORKSPACE_INSUFFICIENT"
    WORKSHEET_INQUIRY_FLOW_FAILURE = "WORKSHEET_INQUIRY_FLOW_FAILURE"
    WORKSHEET_SPOILING_FAILURE = "WORKSHEET_SPOILING_FAILURE"

    # 5. COGNITIVE_LOAD
    COGNITIVE_LOAD_OVERFLOW = "COGNITIVE_LOAD_OVERFLOW"
    DENSITY_OVERLOAD = "DENSITY_OVERLOAD"
    DENSITY_UNDERFLOW = "DENSITY_UNDERFLOW"
    WALL_OF_TEXT = "WALL_OF_TEXT"
    SUSPICIOUS_VOID = "SUSPICIOUS_VOID"
    DENSITY_IMBALANCE = "DENSITY_IMBALANCE"
    COMPRESSION_FAILURE = "COMPRESSION_FAILURE"
    SEQUENCING_FAILURE = "SEQUENCING_FAILURE"
    CONTENT_SELECTION_FAILURE = "CONTENT_SELECTION_FAILURE"
    SEMANTIC_GROUPING_FAILURE = "SEMANTIC_GROUPING_FAILURE"
    ARTIFACT_DIFFERENTIATION_FAILURE = "ARTIFACT_DIFFERENTIATION_FAILURE"

    # 6. STYLE_DESIGN
    LAYOUT_SEMANTIC_MISMATCH = "LAYOUT_SEMANTIC_MISMATCH"
    LAYOUT_CAPACITY_MISMATCH = "LAYOUT_CAPACITY_MISMATCH"
    LAYOUT_MONOTONY = "LAYOUT_MONOTONY"
    CARD_OVERLOAD = "CARD_OVERLOAD"
    VISUAL_HIERARCHY_FAILURE = "VISUAL_HIERARCHY_FAILURE"
    DUPLICATE_COMPOSITION = "DUPLICATE_COMPOSITION"
    REPETITION_STREAK = "REPETITION_STREAK"

    # 7. SCIENTIFIC_RIGOR
    SCIENTIFIC_HIERARCHY_FAILURE = "SCIENTIFIC_HIERARCHY_FAILURE"
    SCIENTIFIC_EVIDENCE_VISIBILITY_FAILURE = "SCIENTIFIC_EVIDENCE_VISIBILITY_FAILURE"
    SCIENTIFIC_EVIDENCE_DETACHED = "SCIENTIFIC_EVIDENCE_DETACHED"
    SCIENTIFIC_CITATION_INVISIBLE = "SCIENTIFIC_CITATION_INVISIBLE"
    SCIENTIFIC_ARGUMENT_IMBALANCE = "SCIENTIFIC_ARGUMENT_IMBALANCE"
    SCIENTIFIC_CHAPTER_IMBALANCE = "SCIENTIFIC_CHAPTER_IMBALANCE"
    ARGUMENT_STRUCTURE_BREAK = "ARGUMENT_STRUCTURE_BREAK"

    # 8. ACCESSIBILITY
    CONTRAST_DEFICIT = "CONTRAST_DEFICIT"
    FONT_LEGIBILITY_FAILURE = "FONT_LEGIBILITY_FAILURE"
    UNTAGGED_STRUCTURE = "UNTAGGED_STRUCTURE"
    TARGET_SIZE_DEFICIT = "TARGET_SIZE_DEFICIT"

    # 9. EXECUTION_CONTRACT
    EXECUTION_TIMEOUT = "EXECUTION_TIMEOUT"
    ASSET_MISSING = "ASSET_MISSING"
    ADAPTER_PAYLOAD_MISMATCH = "ADAPTER_PAYLOAD_MISMATCH"
    RENDER_CRASH = "RENDER_CRASH"

    # 10. EXPORT_PACKAGING
    METADATA_CORRUPTION = "METADATA_CORRUPTION"
    PDF_CONFORMANCE_VIOLATION = "PDF_CONFORMANCE_VIOLATION"
    PAGE_COUNT_DISCREPANCY = "PAGE_COUNT_DISCREPANCY"
    BUNDLE_PACKAGING_FAILURE = "BUNDLE_PACKAGING_FAILURE"

    @property
    def domain(self) -> CanonicalFailureDomain:
        return get_domain_for_code(self)


# Canonical Code-to-Domain Mapping
_DEFAULT_CODE_DOMAIN_MAP: Dict[CanonicalFailureCode, CanonicalFailureDomain] = {
    # 1. PHYSICAL_RENDER
    CanonicalFailureCode.TEXT_CLIPPING: CanonicalFailureDomain.PHYSICAL_RENDER,
    CanonicalFailureCode.ELEMENT_COLLISION: CanonicalFailureDomain.PHYSICAL_RENDER,
    CanonicalFailureCode.TEXT_TOO_SMALL: CanonicalFailureDomain.PHYSICAL_RENDER,
    CanonicalFailureCode.PAGE_BOUNDARY_VIOLATION: CanonicalFailureDomain.PHYSICAL_RENDER,
    CanonicalFailureCode.RENDER_SCALE_FAILURE: CanonicalFailureDomain.PHYSICAL_RENDER,
    CanonicalFailureCode.BLANK_PAGE: CanonicalFailureDomain.PHYSICAL_RENDER,
    CanonicalFailureCode.MARGIN_INCONSISTENCY: CanonicalFailureDomain.PHYSICAL_RENDER,
    CanonicalFailureCode.OVERFLOW_HIDDEN_CUTOFF: CanonicalFailureDomain.PHYSICAL_RENDER,
    CanonicalFailureCode.RENDER_TIMEOUT: CanonicalFailureDomain.PHYSICAL_RENDER,

    # 2. BLUEPRINT_INTEGRITY
    CanonicalFailureCode.BLUEPRINT_CAPACITY_MISMATCH: CanonicalFailureDomain.BLUEPRINT_INTEGRITY,
    CanonicalFailureCode.NARRATIVE_FRAGMENTATION: CanonicalFailureDomain.BLUEPRINT_INTEGRITY,
    CanonicalFailureCode.UNRESOLVED_SLOT: CanonicalFailureDomain.BLUEPRINT_INTEGRITY,
    CanonicalFailureCode.EMPTY_SECTION: CanonicalFailureDomain.BLUEPRINT_INTEGRITY,
    CanonicalFailureCode.SLOT_TYPE_MISMATCH: CanonicalFailureDomain.BLUEPRINT_INTEGRITY,

    # 3. SEMANTIC_TRACEABILITY
    CanonicalFailureCode.SOURCE_GROUNDING_FAILURE: CanonicalFailureDomain.SEMANTIC_TRACEABILITY,
    CanonicalFailureCode.UNSUPPORTED_CLAIM: CanonicalFailureDomain.SEMANTIC_TRACEABILITY,
    CanonicalFailureCode.TRACEABILITY_BREAK: CanonicalFailureDomain.SEMANTIC_TRACEABILITY,
    CanonicalFailureCode.EVIDENCE_DISCIPLINE_FAILURE: CanonicalFailureDomain.SEMANTIC_TRACEABILITY,

    # 4. PEDAGOGICAL_STRUCTURE
    CanonicalFailureCode.INQUIRY_FLOW_BREAK: CanonicalFailureDomain.PEDAGOGICAL_STRUCTURE,
    CanonicalFailureCode.PRESENTATION_HANDOUT_COLLAPSE: CanonicalFailureDomain.PEDAGOGICAL_STRUCTURE,
    CanonicalFailureCode.PRESENTATION_RHYTHM_FAILURE: CanonicalFailureDomain.PEDAGOGICAL_STRUCTURE,
    CanonicalFailureCode.PRESENTATION_DUPLICATE_SEQUENCE: CanonicalFailureDomain.PEDAGOGICAL_STRUCTURE,
    CanonicalFailureCode.HANDOUT_READING_FLOW_FAILURE: CanonicalFailureDomain.PEDAGOGICAL_STRUCTURE,
    CanonicalFailureCode.HANDOUT_FRAGMENTATION: CanonicalFailureDomain.PEDAGOGICAL_STRUCTURE,
    CanonicalFailureCode.HANDOUT_PAGE_BALANCE_FAILURE: CanonicalFailureDomain.PEDAGOGICAL_STRUCTURE,
    CanonicalFailureCode.ORPHAN_HEADING: CanonicalFailureDomain.PEDAGOGICAL_STRUCTURE,
    CanonicalFailureCode.WORKSHEET_QUIZ_COLLAPSE: CanonicalFailureDomain.PEDAGOGICAL_STRUCTURE,
    CanonicalFailureCode.WORKSHEET_WORKSPACE_FAILURE: CanonicalFailureDomain.PEDAGOGICAL_STRUCTURE,
    CanonicalFailureCode.WORKSHEET_WORKSPACE_INSUFFICIENT: CanonicalFailureDomain.PEDAGOGICAL_STRUCTURE,
    CanonicalFailureCode.WORKSHEET_INQUIRY_FLOW_FAILURE: CanonicalFailureDomain.PEDAGOGICAL_STRUCTURE,
    CanonicalFailureCode.WORKSHEET_SPOILING_FAILURE: CanonicalFailureDomain.PEDAGOGICAL_STRUCTURE,

    # 5. COGNITIVE_LOAD
    CanonicalFailureCode.COGNITIVE_LOAD_OVERFLOW: CanonicalFailureDomain.COGNITIVE_LOAD,
    CanonicalFailureCode.DENSITY_OVERLOAD: CanonicalFailureDomain.COGNITIVE_LOAD,
    CanonicalFailureCode.DENSITY_UNDERFLOW: CanonicalFailureDomain.COGNITIVE_LOAD,
    CanonicalFailureCode.WALL_OF_TEXT: CanonicalFailureDomain.COGNITIVE_LOAD,
    CanonicalFailureCode.SUSPICIOUS_VOID: CanonicalFailureDomain.COGNITIVE_LOAD,
    CanonicalFailureCode.DENSITY_IMBALANCE: CanonicalFailureDomain.COGNITIVE_LOAD,
    CanonicalFailureCode.COMPRESSION_FAILURE: CanonicalFailureDomain.COGNITIVE_LOAD,
    CanonicalFailureCode.SEQUENCING_FAILURE: CanonicalFailureDomain.COGNITIVE_LOAD,
    CanonicalFailureCode.CONTENT_SELECTION_FAILURE: CanonicalFailureDomain.COGNITIVE_LOAD,
    CanonicalFailureCode.SEMANTIC_GROUPING_FAILURE: CanonicalFailureDomain.COGNITIVE_LOAD,
    CanonicalFailureCode.ARTIFACT_DIFFERENTIATION_FAILURE: CanonicalFailureDomain.COGNITIVE_LOAD,

    # 6. STYLE_DESIGN
    CanonicalFailureCode.LAYOUT_SEMANTIC_MISMATCH: CanonicalFailureDomain.STYLE_DESIGN,
    CanonicalFailureCode.LAYOUT_CAPACITY_MISMATCH: CanonicalFailureDomain.STYLE_DESIGN,
    CanonicalFailureCode.LAYOUT_MONOTONY: CanonicalFailureDomain.STYLE_DESIGN,
    CanonicalFailureCode.CARD_OVERLOAD: CanonicalFailureDomain.STYLE_DESIGN,
    CanonicalFailureCode.VISUAL_HIERARCHY_FAILURE: CanonicalFailureDomain.STYLE_DESIGN,
    CanonicalFailureCode.DUPLICATE_COMPOSITION: CanonicalFailureDomain.STYLE_DESIGN,
    CanonicalFailureCode.REPETITION_STREAK: CanonicalFailureDomain.STYLE_DESIGN,

    # 7. SCIENTIFIC_RIGOR
    CanonicalFailureCode.SCIENTIFIC_HIERARCHY_FAILURE: CanonicalFailureDomain.SCIENTIFIC_RIGOR,
    CanonicalFailureCode.SCIENTIFIC_EVIDENCE_VISIBILITY_FAILURE: CanonicalFailureDomain.SCIENTIFIC_RIGOR,
    CanonicalFailureCode.SCIENTIFIC_EVIDENCE_DETACHED: CanonicalFailureDomain.SCIENTIFIC_RIGOR,
    CanonicalFailureCode.SCIENTIFIC_CITATION_INVISIBLE: CanonicalFailureDomain.SCIENTIFIC_RIGOR,
    CanonicalFailureCode.SCIENTIFIC_ARGUMENT_IMBALANCE: CanonicalFailureDomain.SCIENTIFIC_RIGOR,
    CanonicalFailureCode.SCIENTIFIC_CHAPTER_IMBALANCE: CanonicalFailureDomain.SCIENTIFIC_RIGOR,
    CanonicalFailureCode.ARGUMENT_STRUCTURE_BREAK: CanonicalFailureDomain.SCIENTIFIC_RIGOR,

    # 8. ACCESSIBILITY
    CanonicalFailureCode.CONTRAST_DEFICIT: CanonicalFailureDomain.ACCESSIBILITY,
    CanonicalFailureCode.FONT_LEGIBILITY_FAILURE: CanonicalFailureDomain.ACCESSIBILITY,
    CanonicalFailureCode.UNTAGGED_STRUCTURE: CanonicalFailureDomain.ACCESSIBILITY,
    CanonicalFailureCode.TARGET_SIZE_DEFICIT: CanonicalFailureDomain.ACCESSIBILITY,

    # 9. EXECUTION_CONTRACT
    CanonicalFailureCode.EXECUTION_TIMEOUT: CanonicalFailureDomain.EXECUTION_CONTRACT,
    CanonicalFailureCode.ASSET_MISSING: CanonicalFailureDomain.EXECUTION_CONTRACT,
    CanonicalFailureCode.ADAPTER_PAYLOAD_MISMATCH: CanonicalFailureDomain.EXECUTION_CONTRACT,
    CanonicalFailureCode.RENDER_CRASH: CanonicalFailureDomain.EXECUTION_CONTRACT,

    # 10. EXPORT_PACKAGING
    CanonicalFailureCode.METADATA_CORRUPTION: CanonicalFailureDomain.EXPORT_PACKAGING,
    CanonicalFailureCode.PDF_CONFORMANCE_VIOLATION: CanonicalFailureDomain.EXPORT_PACKAGING,
    CanonicalFailureCode.PAGE_COUNT_DISCREPANCY: CanonicalFailureDomain.EXPORT_PACKAGING,
    CanonicalFailureCode.BUNDLE_PACKAGING_FAILURE: CanonicalFailureDomain.EXPORT_PACKAGING,
}

# Runtime extensible registry
_CUSTOM_CODE_DOMAIN_REGISTRY: Dict[str, CanonicalFailureDomain] = {}


def register_canonical_code(code_name: str, domain: CanonicalFailureDomain) -> str:
    """Registers a dynamic or extended failure code into the registry."""
    _CUSTOM_CODE_DOMAIN_REGISTRY[code_name] = domain
    return code_name


def get_domain_for_code(code: CanonicalFailureCode | str) -> CanonicalFailureDomain:
    """Retrieves the CanonicalFailureDomain for a failure code."""
    if isinstance(code, CanonicalFailureCode):
        if code in _DEFAULT_CODE_DOMAIN_MAP:
            return _DEFAULT_CODE_DOMAIN_MAP[code]
    
    code_str = code.value if hasattr(code, "value") else str(code)
    
    # Try custom registry
    if code_str in _CUSTOM_CODE_DOMAIN_REGISTRY:
        return _CUSTOM_CODE_DOMAIN_REGISTRY[code_str]

    # Try matching by enum value
    for k, v in _DEFAULT_CODE_DOMAIN_MAP.items():
        if k.value == code_str:
            return v

    # Fallback heuristic based on prefix/terms
    if any(k in code_str for k in ("RENDER", "CLIPPING", "COLLISION", "OVERFLOW", "BLANK", "TOO_SMALL")):
        return CanonicalFailureDomain.PHYSICAL_RENDER
    if any(k in code_str for k in ("SCIENTIFIC", "CITATION", "EVIDENCE")):
        return CanonicalFailureDomain.SCIENTIFIC_RIGOR
    if any(k in code_str for k in ("WORKSHEET", "HANDOUT", "PRESENTATION", "PEDAGOGICAL", "INQUIRY")):
        return CanonicalFailureDomain.PEDAGOGICAL_STRUCTURE
    if any(k in code_str for k in ("DENSITY", "COGNITIVE", "WALL_OF_TEXT")):
        return CanonicalFailureDomain.COGNITIVE_LOAD
    if any(k in code_str for k in ("LAYOUT", "MONOTONY", "HIERARCHY", "CARD")):
        return CanonicalFailureDomain.STYLE_DESIGN
    if any(k in code_str for k in ("BLUEPRINT", "SLOT")):
        return CanonicalFailureDomain.BLUEPRINT_INTEGRITY
    if any(k in code_str for k in ("SOURCE", "GROUNDING", "UNSUPPORTED", "TRACEABILITY")):
        return CanonicalFailureDomain.SEMANTIC_TRACEABILITY
    if any(k in code_str for k in ("CONTRAST", "LEGIBILITY", "ACCESSIBILITY")):
        return CanonicalFailureDomain.ACCESSIBILITY
    if any(k in code_str for k in ("TIMEOUT", "ASSET", "CRASH", "ADAPTER")):
        return CanonicalFailureDomain.EXECUTION_CONTRACT
    if any(k in code_str for k in ("PDF", "METADATA", "PACKAGING", "CONFORMANCE")):
        return CanonicalFailureDomain.EXPORT_PACKAGING

    return CanonicalFailureDomain.PHYSICAL_RENDER


def get_codes_for_domain(domain: CanonicalFailureDomain | str) -> List[CanonicalFailureCode]:
    """Returns all standard CanonicalFailureCodes associated with a domain."""
    dom = domain if isinstance(domain, CanonicalFailureDomain) else CanonicalFailureDomain(str(domain))
    return [c for c, d in _DEFAULT_CODE_DOMAIN_MAP.items() if d == dom]
