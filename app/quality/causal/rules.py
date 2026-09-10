"""
Universal Document Intelligence System V5 — Causal Rule Base.

Phase 3B: Structured, deterministic causal rules defining pattern matching,
architectural layers, base confidence, and causal path templates across all 4 artifact formats.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Set, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.quality.causal.causal_taxonomy import (
    CausalArchitecturalLayer,
    RootCauseCategory,
)
from app.quality.causal.contracts import FailureCluster, QualitySignal


class CausalRule(BaseModel):
    """Structured rule definition defining prerequisites for proposing a root cause hypothesis."""
    model_config = ConfigDict(frozen=True)

    rule_id: str
    name: str
    target_artifact_types: Tuple[str, ...] = Field(default_factory=tuple)  # Empty = all
    required_signal_patterns: Tuple[str, ...]
    optional_signal_patterns: Tuple[str, ...] = Field(default_factory=tuple)
    forbidden_signal_patterns: Tuple[str, ...] = Field(default_factory=tuple)
    candidate_root_cause: RootCauseCategory
    architectural_layer: CausalArchitecturalLayer
    base_confidence: float = Field(default=0.70, ge=0.0, le=1.0)
    evidence_requirements: Tuple[str, ...] = Field(default_factory=tuple)
    priority: int = 10
    description_template: str = ""
    causal_path_template: Tuple[Tuple[CausalArchitecturalLayer, str], ...] = Field(default_factory=tuple)


class CausalRuleMatch(BaseModel):
    """Container recording a successful rule match against a failure cluster."""
    model_config = ConfigDict(frozen=True)

    rule: CausalRule
    matched_signal_ids: Tuple[str, ...]
    match_score: float = Field(ge=0.0, le=1.0)
    supporting_evidence: Tuple[str, ...] = Field(default_factory=tuple)


class CausalRuleCatalog:
    """Repository of calibrated, deterministic causal attribution rules."""

    DEFAULT_RULES: Tuple[CausalRule, ...] = (
        # =====================================================================
        # 1. PRESENTATION RULES
        # =====================================================================
        CausalRule(
            rule_id="RULE_PRES_DENSITY_CAPACITY",
            name="Presentation Layout Capacity Exceeded via Density",
            target_artifact_types=("PRESENTATION",),
            required_signal_patterns=("TEXT_TOO_SMALL", "DENSITY_OVERLOAD"),
            optional_signal_patterns=("TEXT_CLIPPING", "ELEMENT_COLLISION"),
            candidate_root_cause=RootCauseCategory.LAYOUT_CAPACITY_EXCEEDED,
            architectural_layer=CausalArchitecturalLayer.COMPOSITION,
            base_confidence=0.85,
            priority=20,
            description_template="Slide content token volume exceeds slot geometry capacity.",
            causal_path_template=(
                (CausalArchitecturalLayer.BLUEPRINT, "Dense knowledge allocation to single slide"),
                (CausalArchitecturalLayer.COMPOSITION, "Layout card capacity exceeded"),
                (CausalArchitecturalLayer.RENDERING, "Font scale reduced and text clipped"),
            ),
        ),
        CausalRule(
            rule_id="RULE_PRES_BLUEPRINT_OVERLOAD",
            name="Presentation Blueprint Overcompression",
            target_artifact_types=("PRESENTATION",),
            required_signal_patterns=("COGNITIVE_LOAD_OVERFLOW",),
            optional_signal_patterns=("TEXT_CLIPPING", "DENSITY_OVERLOAD"),
            candidate_root_cause=RootCauseCategory.EXCESSIVE_COMPRESSION,
            architectural_layer=CausalArchitecturalLayer.BLUEPRINT,
            base_confidence=0.82,
            priority=18,
            description_template="Too many discrete pedagogical beats compressed into a single slide blueprint.",
            causal_path_template=(
                (CausalArchitecturalLayer.TRANSFORMATION, "Excessive concept grouping into single beat"),
                (CausalArchitecturalLayer.BLUEPRINT, "Cognitive load capacity overflow"),
                (CausalArchitecturalLayer.COMPOSITION, "Container geometry overflow"),
            ),
        ),
        CausalRule(
            rule_id="RULE_PRES_TYPOGRAPHY_SCALE",
            name="Presentation Typography Scale Deficit",
            target_artifact_types=("PRESENTATION",),
            required_signal_patterns=("TEXT_TOO_SMALL",),
            forbidden_signal_patterns=("DENSITY_OVERLOAD", "COGNITIVE_LOAD_OVERFLOW"),
            candidate_root_cause=RootCauseCategory.TYPOGRAPHY_SCALE_FAILURE,
            architectural_layer=CausalArchitecturalLayer.COMPOSITION,
            base_confidence=0.78,
            priority=15,
            description_template="Font sizing scale below legibility threshold without content overload.",
            causal_path_template=(
                (CausalArchitecturalLayer.COMPOSITION, "Suboptimal typography hierarchy scale assigned"),
                (CausalArchitecturalLayer.RENDERING, "Text rendered below 8pt readability threshold"),
            ),
        ),
        CausalRule(
            rule_id="RULE_PRES_HANDOUT_COLLAPSE",
            name="Presentation Handout Transformation Collapse",
            target_artifact_types=("PRESENTATION",),
            required_signal_patterns=("PRESENTATION_HANDOUT_COLLAPSE",),
            candidate_root_cause=RootCauseCategory.SEMANTIC_LAYOUT_MISMATCH,
            architectural_layer=CausalArchitecturalLayer.TRANSFORMATION,
            base_confidence=0.88,
            priority=25,
            description_template="Slide deck structured as prose document rather than visual narrative.",
        ),
        CausalRule(
            rule_id="RULE_PRES_MONOTONY_STREAK",
            name="Presentation Narrative Repetition Streak",
            target_artifact_types=("PRESENTATION",),
            required_signal_patterns=("LAYOUT_MONOTONY", "REPETITION_STREAK"),
            candidate_root_cause=RootCauseCategory.INVALID_GROUPING,
            architectural_layer=CausalArchitecturalLayer.BLUEPRINT,
            base_confidence=0.80,
            priority=16,
            description_template="Repetitive card templates indicate failure to vary visual rhetoric across slides.",
        ),

        # =====================================================================
        # 2. HANDOUT RULES
        # =====================================================================
        CausalRule(
            rule_id="RULE_HAND_CONTENT_OVERDENSITY",
            name="Handout Excessive Paragraph Density",
            target_artifact_types=("HANDOUT",),
            required_signal_patterns=("WALL_OF_TEXT", "DENSITY_OVERLOAD"),
            candidate_root_cause=RootCauseCategory.CONTENT_OVERDENSITY,
            architectural_layer=CausalArchitecturalLayer.SOURCE_CONTENT,
            base_confidence=0.84,
            priority=20,
            description_template="Dense unstructured prose blocks degrade A4 reading flow.",
        ),
        CausalRule(
            rule_id="RULE_HAND_STRUCTURE_FRAGMENTATION",
            name="Handout Structural Fragmentation",
            target_artifact_types=("HANDOUT",),
            required_signal_patterns=("HANDOUT_FRAGMENTATION", "ORPHAN_HEADING"),
            candidate_root_cause=RootCauseCategory.DOCUMENT_STRUCTURE_FAILURE,
            architectural_layer=CausalArchitecturalLayer.BLUEPRINT,
            base_confidence=0.82,
            priority=18,
            description_template="Headings separated from content body across page break.",
        ),
        CausalRule(
            rule_id="RULE_HAND_LAYOUT_CAPACITY",
            name="Handout Layout Capacity Overflow",
            target_artifact_types=("HANDOUT",),
            required_signal_patterns=("PAGE_BOUNDARY_VIOLATION", "ELEMENT_COLLISION"),
            candidate_root_cause=RootCauseCategory.LAYOUT_CAPACITY_EXCEEDED,
            architectural_layer=CausalArchitecturalLayer.COMPOSITION,
            base_confidence=0.85,
            priority=22,
            description_template="Multi-column or table elements exceed A4 printable geometry.",
        ),
        CausalRule(
            rule_id="RULE_HAND_PAGE_BALANCE",
            name="Handout Page Density Imbalance",
            target_artifact_types=("HANDOUT",),
            required_signal_patterns=("HANDOUT_PAGE_BALANCE_FAILURE",),
            optional_signal_patterns=("SUSPICIOUS_VOID", "DENSITY_IMBALANCE"),
            candidate_root_cause=RootCauseCategory.LAYOUT_CAPACITY_EXCEEDED,
            architectural_layer=CausalArchitecturalLayer.COMPOSITION,
            base_confidence=0.80,
            priority=17,
            description_template="Uneven page fill ratios across handout pages.",
        ),

        # =====================================================================
        # 3. WORKSHEET RULES
        # =====================================================================
        CausalRule(
            rule_id="RULE_WORK_QUIZ_COLLAPSE",
            name="Worksheet Anti-Inquiry Quiz Collapse",
            target_artifact_types=("WORKSHEET",),
            required_signal_patterns=("WORKSHEET_QUIZ_COLLAPSE",),
            candidate_root_cause=RootCauseCategory.WORKSHEET_ANTI_INQUIRY_FAILURE,
            architectural_layer=CausalArchitecturalLayer.TRANSFORMATION,
            base_confidence=0.92,
            priority=30,
            description_template="Transformation collapsed inquiry progression into repetitive short questions.",
        ),
        CausalRule(
            rule_id="RULE_WORK_SPOILING",
            name="Worksheet Answer Leakage Invariant Breach",
            target_artifact_types=("WORKSHEET",),
            required_signal_patterns=("WORKSHEET_SPOILING_FAILURE",),
            candidate_root_cause=RootCauseCategory.WORKSHEET_ANSWER_LEAKAGE,
            architectural_layer=CausalArchitecturalLayer.TRANSFORMATION,
            base_confidence=0.95,
            priority=35,
            description_template="Answer or explanation was leaked before student prediction stage.",
        ),
        CausalRule(
            rule_id="RULE_WORK_WORKSPACE_DEFICIT",
            name="Worksheet Student Workspace Insufficient",
            target_artifact_types=("WORKSHEET",),
            required_signal_patterns=("WORKSHEET_WORKSPACE_INSUFFICIENT",),
            optional_signal_patterns=("ELEMENT_COLLISION", "WORKSHEET_WORKSPACE_FAILURE"),
            candidate_root_cause=RootCauseCategory.LAYOUT_CAPACITY_EXCEEDED,
            architectural_layer=CausalArchitecturalLayer.COMPOSITION,
            base_confidence=0.82,
            priority=18,
            description_template="Response box height insufficient for handwriting response.",
        ),

        # =====================================================================
        # 4. SCIENTIFIC DOCUMENT RULES
        # =====================================================================
        CausalRule(
            rule_id="RULE_SCI_UNSUPPORTED_CLAIM",
            name="Scientific Document Unsupported Assertion",
            target_artifact_types=("SCIENTIFIC_DOCUMENT",),
            required_signal_patterns=("UNSUPPORTED_CLAIM",),
            optional_signal_patterns=("SOURCE_GROUNDING_FAILURE",),
            candidate_root_cause=RootCauseCategory.SOURCE_GROUNDING_FAILURE,
            architectural_layer=CausalArchitecturalLayer.SOURCE_CONTENT,
            base_confidence=0.92,
            priority=30,
            description_template="Scientific factual claim has no grounding in source knowledge units.",
        ),
        CausalRule(
            rule_id="RULE_SCI_CITATION_INVISIBLE",
            name="Scientific Document Citation Structure Detached",
            target_artifact_types=("SCIENTIFIC_DOCUMENT",),
            required_signal_patterns=("SCIENTIFIC_CITATION_INVISIBLE",),
            optional_signal_patterns=("EVIDENCE_DISCIPLINE_FAILURE",),
            candidate_root_cause=RootCauseCategory.CITATION_STRUCTURE_FAILURE,
            architectural_layer=CausalArchitecturalLayer.KNOWLEDGE_MODEL,
            base_confidence=0.90,
            priority=28,
            description_template="Citation marker in text has no corresponding entry in references graph.",
        ),
        CausalRule(
            rule_id="RULE_SCI_BAB_INVERSION",
            name="Scientific Document Chapter Hierarchy Inversion",
            target_artifact_types=("SCIENTIFIC_DOCUMENT",),
            required_signal_patterns=("SCIENTIFIC_HIERARCHY_FAILURE",),
            candidate_root_cause=RootCauseCategory.DOCUMENT_STRUCTURE_FAILURE,
            architectural_layer=CausalArchitecturalLayer.TRANSFORMATION,
            base_confidence=0.92,
            priority=30,
            description_template="Formal Indonesian KTI chapter order inverted (e.g. BAB IV before BAB III).",
        ),

        # =====================================================================
        # 5. UNIVERSAL / CROSS-ARTIFACT RULES
        # =====================================================================
        CausalRule(
            rule_id="RULE_UNI_GRID_COLLISION",
            name="Universal Grid Collision Overflow",
            required_signal_patterns=("ELEMENT_COLLISION", "CARD_OVERLOAD"),
            candidate_root_cause=RootCauseCategory.GRID_COMPOSITION_FAILURE,
            architectural_layer=CausalArchitecturalLayer.COMPOSITION,
            base_confidence=0.86,
            priority=22,
            description_template="Grid placement rules allowed bounding boxes to intersect.",
        ),
        CausalRule(
            rule_id="RULE_UNI_RENDER_CRASH",
            name="Universal Renderer Engine Anomaly",
            required_signal_patterns=("RENDER_CRASH",),
            optional_signal_patterns=("BLANK_PAGE", "RENDER_SCALE_FAILURE"),
            candidate_root_cause=RootCauseCategory.RENDERING_ENGINE_ANOMALY,
            architectural_layer=CausalArchitecturalLayer.RENDERING,
            base_confidence=0.94,
            priority=40,
            description_template="Headless browser or PyMuPDF encountered rendering crash.",
        ),
        CausalRule(
            rule_id="RULE_UNI_STYLE_SYSTEM",
            name="Universal Global Style System Failure",
            required_signal_patterns=("MARGIN_INCONSISTENCY",),
            optional_signal_patterns=("FONT_LEGIBILITY_FAILURE",),
            candidate_root_cause=RootCauseCategory.STYLE_SYSTEM_FAILURE,
            architectural_layer=CausalArchitecturalLayer.COMPOSITION,
            base_confidence=0.76,
            priority=14,
            description_template="Document stylesheet failed to standardize margin parameters.",
        ),
    )

    @classmethod
    def match_rules(
        cls,
        cluster: FailureCluster,
        artifact_type: str = "UNKNOWN",
    ) -> List[CausalRuleMatch]:
        """Matches cluster symptoms and context against causal rules deterministically."""
        matches: List[CausalRuleMatch] = []
        cluster_codes = {s.failure_code.value for s in cluster.signals}
        if not cluster_codes and cluster.symptoms:
            cluster_codes = {c.value for c in cluster.symptoms}

        for rule in cls.DEFAULT_RULES:
            # Check artifact type constraints
            if rule.target_artifact_types and artifact_type != "UNKNOWN":
                if artifact_type.upper() not in rule.target_artifact_types:
                    continue

            # Check required patterns
            req_met = all(pat in cluster_codes for pat in rule.required_signal_patterns)
            if not req_met:
                continue

            # Check forbidden patterns
            forbid_triggered = any(pat in cluster_codes for pat in rule.forbidden_signal_patterns)
            if forbid_triggered:
                continue

            # Match score computation: base + bonus for optional patterns
            matched_sids: List[str] = []
            for s in cluster.signals:
                if s.failure_code.value in rule.required_signal_patterns or s.failure_code.value in rule.optional_signal_patterns:
                    matched_sids.append(s.signal_id)

            bonus = 0.0
            for opt in rule.optional_signal_patterns:
                if opt in cluster_codes:
                    bonus += 0.05

            match_score = min(1.0, rule.base_confidence + bonus)
            support_ev = (
                f"Rule '{rule.name}' matched required patterns: {list(rule.required_signal_patterns)}",
            )

            matches.append(
                CausalRuleMatch(
                    rule=rule,
                    matched_signal_ids=tuple(sorted(matched_sids)),
                    match_score=round(match_score, 4),
                    supporting_evidence=support_ev,
                )
            )

        # Sort matches by priority descending, then match_score descending
        matches.sort(key=lambda m: (m.rule.priority, m.match_score), reverse=True)
        return matches

    match = match_rules
