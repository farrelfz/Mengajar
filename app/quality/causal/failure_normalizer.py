"""
Universal Document Intelligence System V5 — Canonical Failure Normalizer.

Phase 3A.1: Aggregates, deduplicates, and classifies QualitySignal objects
into structured CanonicalFailure models with deterministic severity resolution.
"""

from __future__ import annotations

from typing import Dict, List, Tuple
from collections import defaultdict

from app.quality.causal.contracts import CanonicalFailure, QualitySignal
from app.quality.causal.taxonomy import (
    CanonicalFailureCategory,
    CanonicalFailureCode,
    CanonicalFailureSeverity,
    FailureScope,
)


class FailureNormalizer:
    """Normalizes raw signals into canonical failures with resolved severities and scopes."""

    # Map raw string metric names / codes to CanonicalFailureCode
    CODE_MAPPING: Dict[str, CanonicalFailureCode] = {
        # Geometry & Render
        "TEXT_CLIPPING": CanonicalFailureCode.TEXT_CLIPPING,
        "TEXT_TOO_SMALL": CanonicalFailureCode.TEXT_TOO_SMALL,
        "ELEMENT_COLLISION": CanonicalFailureCode.ELEMENT_COLLISION,
        "BLANK_PAGE": CanonicalFailureCode.BLANK_PAGE,
        "PAGE_BOUNDARY_VIOLATION": CanonicalFailureCode.PAGE_BOUNDARY_VIOLATION,
        "MARGIN_INCONSISTENCY": CanonicalFailureCode.MARGIN_INCONSISTENCY,
        "RENDER_SCALE_FAILURE": CanonicalFailureCode.RENDER_SCALE_FAILURE,

        # Density & Whitespace
        "DENSITY_OVERLOAD": CanonicalFailureCode.DENSITY_OVERLOAD,
        "DENSITY_UNDERFLOW": CanonicalFailureCode.DENSITY_UNDERFLOW,
        "SUSPICIOUS_VOID": CanonicalFailureCode.SUSPICIOUS_VOID,
        "WALL_OF_TEXT": CanonicalFailureCode.WALL_OF_TEXT,
        "HANDOUT_WALL_OF_TEXT": CanonicalFailureCode.WALL_OF_TEXT,
        "DENSITY_IMBALANCE": CanonicalFailureCode.DENSITY_IMBALANCE,

        # Composition & Layout
        "LAYOUT_MONOTONY": CanonicalFailureCode.LAYOUT_MONOTONY,
        "DUPLICATE_COMPOSITION": CanonicalFailureCode.DUPLICATE_COMPOSITION,
        "REPETITION_STREAK": CanonicalFailureCode.REPETITION_STREAK,
        "CARD_OVERLOAD": CanonicalFailureCode.CARD_OVERLOAD,
        "VISUAL_HIERARCHY_FAILURE": CanonicalFailureCode.VISUAL_HIERARCHY_FAILURE,

        # Handout
        "HANDOUT_READING_FLOW_FAILURE": CanonicalFailureCode.HANDOUT_READING_FLOW_FAILURE,
        "HANDOUT_FRAGMENTATION": CanonicalFailureCode.HANDOUT_FRAGMENTATION,
        "ORPHAN_HEADING": CanonicalFailureCode.ORPHAN_HEADING,

        # Worksheet
        "WORKSHEET_QUIZ_COLLAPSE": CanonicalFailureCode.WORKSHEET_QUIZ_COLLAPSE,
        "WORKSHEET_WORKSPACE_FAILURE": CanonicalFailureCode.WORKSHEET_WORKSPACE_FAILURE,
        "WORKSHEET_WORKSPACE_INSUFFICIENT": CanonicalFailureCode.WORKSHEET_WORKSPACE_INSUFFICIENT,
        "WORKSHEET_SPOILING_FAILURE": CanonicalFailureCode.WORKSHEET_SPOILING_FAILURE,
        "WORKSHEET_INQUIRY_DEGRADED": CanonicalFailureCode.WORKSHEET_INQUIRY_FLOW_FAILURE,
        "WORKSHEET_INQUIRY_FLOW_FAILURE": CanonicalFailureCode.WORKSHEET_INQUIRY_FLOW_FAILURE,

        # Scientific
        "SCIENTIFIC_HIERARCHY_FAILURE": CanonicalFailureCode.SCIENTIFIC_HIERARCHY_FAILURE,
        "SCIENTIFIC_CITATION_INVISIBLE": CanonicalFailureCode.SCIENTIFIC_CITATION_INVISIBLE,
        "SCIENTIFIC_EVIDENCE_DETACHED": CanonicalFailureCode.SCIENTIFIC_EVIDENCE_DETACHED,
        "SCIENTIFIC_ARGUMENT_SPARSITY": CanonicalFailureCode.SCIENTIFIC_ARGUMENT_IMBALANCE,
        "SCIENTIFIC_CHAPTER_IMBALANCE": CanonicalFailureCode.SCIENTIFIC_CHAPTER_IMBALANCE,

        # Semantic / Source
        "UNSUPPORTED_CLAIM": CanonicalFailureCode.UNSUPPORTED_CLAIM,
        "SOURCE_GROUNDING_FAILURE": CanonicalFailureCode.SOURCE_GROUNDING_FAILURE,
        "TRACEABILITY_BREAK": CanonicalFailureCode.TRACEABILITY_BREAK,
        "TRACEABILITY_FAILURE": CanonicalFailureCode.TRACEABILITY_BREAK,
        "EVIDENCE_DISCIPLINE_FAILURE": CanonicalFailureCode.EVIDENCE_DISCIPLINE_FAILURE,
        "fidelity_violation": CanonicalFailureCode.TRACEABILITY_BREAK,
        "fidelity_warning": CanonicalFailureCode.TRACEABILITY_BREAK,
    }

    # Category Mapping
    CATEGORY_MAPPING: Dict[CanonicalFailureCode, CanonicalFailureCategory] = {
        CanonicalFailureCode.SOURCE_GROUNDING_FAILURE: CanonicalFailureCategory.SOURCE_SEMANTIC,
        CanonicalFailureCode.UNSUPPORTED_CLAIM: CanonicalFailureCategory.SOURCE_SEMANTIC,
        CanonicalFailureCode.TRACEABILITY_BREAK: CanonicalFailureCategory.SOURCE_SEMANTIC,
        CanonicalFailureCode.EVIDENCE_DISCIPLINE_FAILURE: CanonicalFailureCategory.SOURCE_SEMANTIC,

        CanonicalFailureCode.CONTENT_SELECTION_FAILURE: CanonicalFailureCategory.TRANSFORMATION,
        CanonicalFailureCode.SEMANTIC_GROUPING_FAILURE: CanonicalFailureCategory.TRANSFORMATION,
        CanonicalFailureCode.ARTIFACT_DIFFERENTIATION_FAILURE: CanonicalFailureCategory.TRANSFORMATION,
        CanonicalFailureCode.COMPRESSION_FAILURE: CanonicalFailureCategory.TRANSFORMATION,
        CanonicalFailureCode.SEQUENCING_FAILURE: CanonicalFailureCategory.TRANSFORMATION,

        CanonicalFailureCode.BLUEPRINT_CAPACITY_MISMATCH: CanonicalFailureCategory.BLUEPRINT,
        CanonicalFailureCode.COGNITIVE_LOAD_OVERFLOW: CanonicalFailureCategory.BLUEPRINT,
        CanonicalFailureCode.NARRATIVE_FRAGMENTATION: CanonicalFailureCategory.BLUEPRINT,
        CanonicalFailureCode.INQUIRY_FLOW_BREAK: CanonicalFailureCategory.BLUEPRINT,
        CanonicalFailureCode.ARGUMENT_STRUCTURE_BREAK: CanonicalFailureCategory.BLUEPRINT,

        CanonicalFailureCode.LAYOUT_SEMANTIC_MISMATCH: CanonicalFailureCategory.LAYOUT,
        CanonicalFailureCode.LAYOUT_CAPACITY_MISMATCH: CanonicalFailureCategory.LAYOUT,
        CanonicalFailureCode.LAYOUT_MONOTONY: CanonicalFailureCategory.LAYOUT,
        CanonicalFailureCode.CARD_OVERLOAD: CanonicalFailureCategory.LAYOUT,
        CanonicalFailureCode.VISUAL_HIERARCHY_FAILURE: CanonicalFailureCategory.LAYOUT,
        CanonicalFailureCode.DUPLICATE_COMPOSITION: CanonicalFailureCategory.LAYOUT,
        CanonicalFailureCode.REPETITION_STREAK: CanonicalFailureCategory.LAYOUT,

        CanonicalFailureCode.TEXT_CLIPPING: CanonicalFailureCategory.RENDER,
        CanonicalFailureCode.ELEMENT_COLLISION: CanonicalFailureCategory.RENDER,
        CanonicalFailureCode.TEXT_TOO_SMALL: CanonicalFailureCategory.RENDER,
        CanonicalFailureCode.PAGE_BOUNDARY_VIOLATION: CanonicalFailureCategory.RENDER,
        CanonicalFailureCode.RENDER_SCALE_FAILURE: CanonicalFailureCategory.RENDER,
        CanonicalFailureCode.BLANK_PAGE: CanonicalFailureCategory.RENDER,
        CanonicalFailureCode.MARGIN_INCONSISTENCY: CanonicalFailureCategory.RENDER,

        CanonicalFailureCode.DENSITY_OVERLOAD: CanonicalFailureCategory.DENSITY,
        CanonicalFailureCode.DENSITY_UNDERFLOW: CanonicalFailureCategory.DENSITY,
        CanonicalFailureCode.WALL_OF_TEXT: CanonicalFailureCategory.DENSITY,
        CanonicalFailureCode.SUSPICIOUS_VOID: CanonicalFailureCategory.DENSITY,
        CanonicalFailureCode.DENSITY_IMBALANCE: CanonicalFailureCategory.DENSITY,

        CanonicalFailureCode.PRESENTATION_HANDOUT_COLLAPSE: CanonicalFailureCategory.ARTIFACT_SPECIFIC,
        CanonicalFailureCode.PRESENTATION_RHYTHM_FAILURE: CanonicalFailureCategory.ARTIFACT_SPECIFIC,
        CanonicalFailureCode.PRESENTATION_DUPLICATE_SEQUENCE: CanonicalFailureCategory.ARTIFACT_SPECIFIC,
        CanonicalFailureCode.HANDOUT_READING_FLOW_FAILURE: CanonicalFailureCategory.ARTIFACT_SPECIFIC,
        CanonicalFailureCode.HANDOUT_FRAGMENTATION: CanonicalFailureCategory.ARTIFACT_SPECIFIC,
        CanonicalFailureCode.HANDOUT_PAGE_BALANCE_FAILURE: CanonicalFailureCategory.ARTIFACT_SPECIFIC,
        CanonicalFailureCode.ORPHAN_HEADING: CanonicalFailureCategory.ARTIFACT_SPECIFIC,
        CanonicalFailureCode.WORKSHEET_QUIZ_COLLAPSE: CanonicalFailureCategory.ARTIFACT_SPECIFIC,
        CanonicalFailureCode.WORKSHEET_WORKSPACE_FAILURE: CanonicalFailureCategory.ARTIFACT_SPECIFIC,
        CanonicalFailureCode.WORKSHEET_WORKSPACE_INSUFFICIENT: CanonicalFailureCategory.ARTIFACT_SPECIFIC,
        CanonicalFailureCode.WORKSHEET_INQUIRY_FLOW_FAILURE: CanonicalFailureCategory.ARTIFACT_SPECIFIC,
        CanonicalFailureCode.WORKSHEET_SPOILING_FAILURE: CanonicalFailureCategory.ARTIFACT_SPECIFIC,
        CanonicalFailureCode.SCIENTIFIC_HIERARCHY_FAILURE: CanonicalFailureCategory.ARTIFACT_SPECIFIC,
        CanonicalFailureCode.SCIENTIFIC_EVIDENCE_VISIBILITY_FAILURE: CanonicalFailureCategory.ARTIFACT_SPECIFIC,
        CanonicalFailureCode.SCIENTIFIC_EVIDENCE_DETACHED: CanonicalFailureCategory.ARTIFACT_SPECIFIC,
        CanonicalFailureCode.SCIENTIFIC_CITATION_INVISIBLE: CanonicalFailureCategory.ARTIFACT_SPECIFIC,
        CanonicalFailureCode.SCIENTIFIC_ARGUMENT_IMBALANCE: CanonicalFailureCategory.ARTIFACT_SPECIFIC,
        CanonicalFailureCode.SCIENTIFIC_CHAPTER_IMBALANCE: CanonicalFailureCategory.ARTIFACT_SPECIFIC,
    }

    SEVERITY_ORDER = {
        CanonicalFailureSeverity.INFO: 0,
        CanonicalFailureSeverity.MINOR: 1,
        CanonicalFailureSeverity.MAJOR: 2,
        CanonicalFailureSeverity.CRITICAL: 3,
    }

    @classmethod
    def normalize_signals(
        cls,
        signals: List[QualitySignal],
        total_pages: int = 1,
    ) -> List[CanonicalFailure]:
        """Groups signals by canonical failure code and pages, resolving severities deterministically."""
        # Filter out purely informational metric signals with no failure
        defect_signals = [s for s in signals if s.severity != CanonicalFailureSeverity.INFO]
        if not defect_signals:
            return []

        # Group by mapped CanonicalFailureCode
        grouped_by_code: Dict[CanonicalFailureCode, List[QualitySignal]] = defaultdict(list)
        for sig in defect_signals:
            canon_code = cls._resolve_canonical_code(sig.metric_name, sig.description)
            if canon_code:
                grouped_by_code[canon_code].append(sig)

        failures: List[CanonicalFailure] = []
        artifact_type = signals[0].artifact_type if signals else "UNKNOWN"

        for code, sig_list in grouped_by_code.items():
            # Resolve highest severity
            max_sev = max(sig_list, key=lambda s: cls.SEVERITY_ORDER.get(s.severity, 0)).severity

            # Union of all affected pages
            all_pages: set[int] = set()
            for s in sig_list:
                all_pages.update(s.page_indices)
            affected_pages = tuple(sorted(all_pages))

            # Compute frequency
            freq = round(len(affected_pages) / max(1, total_pages), 3)

            # Determine scope
            scope = cls._determine_scope(affected_pages, total_pages, code)

            # Category
            category = cls.CATEGORY_MAPPING.get(code, CanonicalFailureCategory.RENDER)

            # Representative symptom summary
            symptom_desc = sig_list[0].description
            if len(sig_list) > 1:
                symptom_desc = f"{symptom_desc} (+{len(sig_list) - 1} similar signals)"

            failures.append(
                CanonicalFailure(
                    failure_code=code,
                    category=category,
                    artifact_type=artifact_type,
                    affected_pages=affected_pages,
                    severity=max_sev,
                    symptom=symptom_desc,
                    evidence_signals=tuple(sig_list),
                    quality_dimension=sig_list[0].dimension,
                    scope=scope,
                    frequency=freq,
                    impact=f"Affects {len(affected_pages)}/{total_pages} pages ({freq * 100:.1f}%)",
                    detected_by=sig_list[0].source_engine,
                )
            )

        return failures

    @classmethod
    def _resolve_canonical_code(cls, metric_name: str, description: str) -> CanonicalFailureCode | None:
        # Exact match
        if metric_name in cls.CODE_MAPPING:
            return cls.CODE_MAPPING[metric_name]
        
        # Substring search in metric name
        name_u = metric_name.upper()
        for k, v in cls.CODE_MAPPING.items():
            if k in name_u:
                return v

        # Substring search in description
        desc_u = description.upper()
        if "CLIPP" in desc_u:
            return CanonicalFailureCode.TEXT_CLIPPING
        elif "COLLISION" in desc_u:
            return CanonicalFailureCode.ELEMENT_COLLISION
        elif "TOO SMALL" in desc_u or "FONT" in desc_u:
            return CanonicalFailureCode.TEXT_TOO_SMALL
        elif "BLANK" in desc_u:
            return CanonicalFailureCode.BLANK_PAGE
        elif "SPOIL" in desc_u or "KUNCI JAWABAN" in desc_u:
            return CanonicalFailureCode.WORKSHEET_SPOILING_FAILURE
        elif "CITATION" in desc_u:
            return CanonicalFailureCode.SCIENTIFIC_CITATION_INVISIBLE
        elif "BAB" in desc_u and "INVERT" in desc_u:
            return CanonicalFailureCode.SCIENTIFIC_HIERARCHY_FAILURE
        elif "QUIZ" in desc_u:
            return CanonicalFailureCode.WORKSHEET_QUIZ_COLLAPSE

        return None

    @classmethod
    def _determine_scope(
        cls,
        affected_pages: Tuple[int, ...],
        total_pages: int,
        code: CanonicalFailureCode,
    ) -> FailureScope:
        # Inherent artifact-wide failures
        if code in (
            CanonicalFailureCode.SCIENTIFIC_CITATION_INVISIBLE,
            CanonicalFailureCode.SCIENTIFIC_HIERARCHY_FAILURE,
            CanonicalFailureCode.WORKSHEET_QUIZ_COLLAPSE,
            CanonicalFailureCode.TRACEABILITY_BREAK,
        ):
            return FailureScope.ARTIFACT_WIDE

        count = len(affected_pages)
        ratio = count / max(1, total_pages)

        if ratio > 0.50 or count >= (total_pages - 1) and total_pages > 2:
            return FailureScope.SYSTEMIC

        # Check for consecutive streak (CLUSTER)
        if count >= 3:
            sorted_pages = sorted(affected_pages)
            is_streak = all(sorted_pages[i + 1] == sorted_pages[i] + 1 for i in range(len(sorted_pages) - 1))
            if is_streak:
                return FailureScope.CLUSTER

        return FailureScope.LOCAL
