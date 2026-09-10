"""
Universal Document Intelligence System V5 — Causal Taxonomy & Layer Architecture.

Phase 3B: Controlled, typed taxonomy for architectural origin layers, root cause categories,
causal confidence tiers, and authoritative causal decision states.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional


class CausalArchitecturalLayer(str, Enum):
    """The 9 distinct architectural pipeline layers of defect origin."""
    SOURCE_CONTENT = "SOURCE_CONTENT"
    KNOWLEDGE_MODEL = "KNOWLEDGE_MODEL"
    TRANSFORMATION = "TRANSFORMATION"
    BLUEPRINT = "BLUEPRINT"
    SEMANTIC_LAYOUT = "SEMANTIC_LAYOUT"
    COMPOSITION = "COMPOSITION"
    RENDERING = "RENDERING"
    VALIDATION = "VALIDATION"
    EXTERNAL_DEPENDENCY = "EXTERNAL_DEPENDENCY"

    @property
    def stage_order(self) -> int:
        """Pipeline execution order for lineage direction validation."""
        ordering = {
            CausalArchitecturalLayer.SOURCE_CONTENT: 1,
            CausalArchitecturalLayer.KNOWLEDGE_MODEL: 2,
            CausalArchitecturalLayer.TRANSFORMATION: 3,
            CausalArchitecturalLayer.BLUEPRINT: 4,
            CausalArchitecturalLayer.SEMANTIC_LAYOUT: 5,
            CausalArchitecturalLayer.COMPOSITION: 6,
            CausalArchitecturalLayer.RENDERING: 7,
            CausalArchitecturalLayer.VALIDATION: 8,
            CausalArchitecturalLayer.EXTERNAL_DEPENDENCY: 0,
        }
        return ordering.get(self, 99)


class RootCauseCategory(str, Enum):
    """Controlled, typed taxonomy of root cause defect categories."""
    CONTENT_OVERDENSITY = "CONTENT_OVERDENSITY"
    CONCEPT_FRAGMENTATION = "CONCEPT_FRAGMENTATION"
    EXCESSIVE_COMPRESSION = "EXCESSIVE_COMPRESSION"
    INVALID_GROUPING = "INVALID_GROUPING"
    NARRATIVE_DISCONTINUITY = "NARRATIVE_DISCONTINUITY"
    COGNITIVE_OVERLOAD = "COGNITIVE_OVERLOAD"
    SEMANTIC_LAYOUT_MISMATCH = "SEMANTIC_LAYOUT_MISMATCH"
    LAYOUT_CAPACITY_EXCEEDED = "LAYOUT_CAPACITY_EXCEEDED"
    TYPOGRAPHY_SCALE_FAILURE = "TYPOGRAPHY_SCALE_FAILURE"
    VISUAL_HIERARCHY_FAILURE = "VISUAL_HIERARCHY_FAILURE"
    GRID_COMPOSITION_FAILURE = "GRID_COMPOSITION_FAILURE"
    RENDERING_ENGINE_ANOMALY = "RENDERING_ENGINE_ANOMALY"
    SOURCE_GROUNDING_FAILURE = "SOURCE_GROUNDING_FAILURE"
    EVIDENCE_LINKAGE_FAILURE = "EVIDENCE_LINKAGE_FAILURE"
    CITATION_STRUCTURE_FAILURE = "CITATION_STRUCTURE_FAILURE"
    WORKSHEET_ANTI_INQUIRY_FAILURE = "WORKSHEET_ANTI_INQUIRY_FAILURE"
    WORKSHEET_ANSWER_LEAKAGE = "WORKSHEET_ANSWER_LEAKAGE"
    SCIENTIFIC_ARGUMENT_FAILURE = "SCIENTIFIC_ARGUMENT_FAILURE"
    DOCUMENT_STRUCTURE_FAILURE = "DOCUMENT_STRUCTURE_FAILURE"
    STYLE_SYSTEM_FAILURE = "STYLE_SYSTEM_FAILURE"
    GLOBAL_CONFIGURATION_FAILURE = "GLOBAL_CONFIGURATION_FAILURE"
    QUALITY_THRESHOLD_MISCONFIGURATION = "QUALITY_THRESHOLD_MISCONFIGURATION"
    VALIDATOR_FALSE_POSITIVE = "VALIDATOR_FALSE_POSITIVE"
    UNKNOWN_CAUSE = "UNKNOWN_CAUSE"


class CausalConfidenceLevel(str, Enum):
    """Categorical confidence tiers in root cause attribution."""
    VERY_HIGH = "VERY_HIGH"  # Score >= 0.90 (Requires lineage consistency, no major contradiction)
    HIGH = "HIGH"            # Score >= 0.75
    MEDIUM = "MEDIUM"        # Score >= 0.55
    LOW = "LOW"              # Score >= 0.35
    VERY_LOW = "VERY_LOW"    # Score < 0.35

    @classmethod
    def from_score(cls, score: float) -> CausalConfidenceLevel:
        if score >= 0.90:
            return cls.VERY_HIGH
        if score >= 0.75:
            return cls.HIGH
        if score >= 0.55:
            return cls.MEDIUM
        if score >= 0.35:
            return cls.LOW
        return cls.VERY_LOW


class CausalDecision(str, Enum):
    """Authoritative causal decision state concluding cluster analysis."""
    ROOT_CAUSE_CONFIRMED = "ROOT_CAUSE_CONFIRMED"
    ROOT_CAUSE_LIKELY = "ROOT_CAUSE_LIKELY"
    MULTIPLE_PLAUSIBLE_CAUSES = "MULTIPLE_PLAUSIBLE_CAUSES"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    NO_CAUSAL_LINK = "NO_CAUSAL_LINK"
    VALIDATOR_ANOMALY_SUSPECTED = "VALIDATOR_ANOMALY_SUSPECTED"
    UNKNOWN = "UNKNOWN"


class HypothesisStatus(str, Enum):
    """Lifecycle status of a generated root cause hypothesis."""
    CANDIDATE = "CANDIDATE"
    LIKELY = "LIKELY"
    STRONG = "STRONG"
    REJECTED = "REJECTED"
    UNKNOWN = "UNKNOWN"


class CausalPathEdgeRelationship(str, Enum):
    """Directional relationship between nodes in an explainable causal path."""
    CAUSES = "CAUSES"
    CONTRIBUTES_TO = "CONTRIBUTES_TO"
    AMPLIFIES = "AMPLIFIES"
    PRECEDES = "PRECEDES"
    EXPLAINS = "EXPLAINS"
    CONSTRAINS = "CONSTRAINS"
