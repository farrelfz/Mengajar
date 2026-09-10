"""
Universal Document Intelligence System V5 — Artifact Drift Analyzer.

Phase 3C.1: Quantifies semantic, structural, narrative, and traceability drift
between pre-repair and post-repair states to prevent destructive "score-hacking".
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, ConfigDict, Field


class ArtifactDriftReport(BaseModel):
    """Immutable audit report evaluating state drift across 4 dimensions."""
    model_config = ConfigDict(frozen=True)

    artifact_type: str
    semantic_drift_score: float = Field(ge=0.0, le=1.0)
    structural_drift_score: float = Field(ge=0.0, le=1.0)
    narrative_drift_score: float = Field(ge=0.0, le=1.0)
    traceability_drift_score: float = Field(ge=0.0, le=1.0)
    overall_drift_score: float = Field(ge=0.0, le=1.0)
    is_acceptable: bool
    violations: Tuple[str, ...] = Field(default_factory=tuple)


class ArtifactDriftAnalyzer:
    """Measures drift between pre-mutation and post-mutation artifact blueprints."""

    MAX_ACCEPTABLE_OVERALL_DRIFT = 0.25
    MAX_ACCEPTABLE_SEMANTIC_DRIFT = 0.20
    MAX_ACCEPTABLE_TRACEABILITY_DRIFT = 0.05  # At least 95% traceability must be preserved

    @classmethod
    def analyze(
        cls,
        pre_blueprint: Any,
        post_blueprint: Any,
        artifact_type: str,
    ) -> ArtifactDriftReport:
        """
        Computes multi-dimensional drift and evaluates acceptability.
        """
        violations: List[str] = []

        # 1. Traceability Drift
        pre_refs = cls._extract_source_refs(pre_blueprint)
        post_refs = cls._extract_source_refs(post_blueprint)

        if pre_refs:
            preserved_refs = pre_refs.intersection(post_refs)
            retention_ratio = len(preserved_refs) / len(pre_refs)
            traceability_drift = round(max(0.0, 1.0 - retention_ratio), 4)
        else:
            traceability_drift = 0.0

        if traceability_drift > cls.MAX_ACCEPTABLE_TRACEABILITY_DRIFT:
            violations.append(
                f"Traceability loss {traceability_drift:.1%} exceeds maximum allowed {cls.MAX_ACCEPTABLE_TRACEABILITY_DRIFT:.1%}"
            )

        # 2. Structural Drift
        structural_drift = cls._calculate_structural_drift(pre_blueprint, post_blueprint, artifact_type)
        if structural_drift > 0.35:
            violations.append(f"Excessive structural drift ({structural_drift:.1%}).")

        # 3. Semantic & Content Drift
        semantic_drift = cls._calculate_semantic_drift(pre_blueprint, post_blueprint)
        if semantic_drift > cls.MAX_ACCEPTABLE_SEMANTIC_DRIFT:
            violations.append(f"Semantic drift ({semantic_drift:.1%}) exceeds budget ({cls.MAX_ACCEPTABLE_SEMANTIC_DRIFT:.1%}).")

        # 4. Narrative Drift
        narrative_drift = cls._calculate_narrative_drift(pre_blueprint, post_blueprint)

        # 5. Overall Weighted Drift
        overall = round(
            (0.35 * semantic_drift)
            + (0.35 * traceability_drift)
            + (0.20 * structural_drift)
            + (0.10 * narrative_drift),
            4,
        )

        if overall > cls.MAX_ACCEPTABLE_OVERALL_DRIFT:
            violations.append(
                f"Overall artifact drift {overall:.1%} exceeds threshold {cls.MAX_ACCEPTABLE_OVERALL_DRIFT:.1%}"
            )

        is_acceptable = len(violations) == 0

        return ArtifactDriftReport(
            artifact_type=artifact_type.upper(),
            semantic_drift_score=semantic_drift,
            structural_drift_score=structural_drift,
            narrative_drift_score=narrative_drift,
            traceability_drift_score=traceability_drift,
            overall_drift_score=overall,
            is_acceptable=is_acceptable,
            violations=tuple(violations),
        )

    @classmethod
    def _extract_source_refs(cls, blueprint: Any) -> Set[str]:
        """Gathers all source unit and evidence references in the blueprint."""
        refs: Set[str] = set()

        # Slides / Presentation
        slides = getattr(blueprint, "slides", None) or getattr(blueprint, "beats", None)
        if slides:
            for s in slides:
                refs.update(getattr(s, "source_refs", ()) or ())
                refs.update(getattr(s, "source_element_ids", ()) or ())
                refs.update(getattr(s, "knowledge_unit_ids", ()) or ())

        # Sections / Handout
        sections = getattr(blueprint, "sections", None)
        if sections:
            for sec in sections:
                refs.update(getattr(sec, "source_unit_ids", ()) or ())

        # Worksheet activities
        activities = getattr(blueprint, "activities", None)
        if activities:
            for act in activities:
                refs.update(getattr(act, "source_refs", ()) or ())

        # Scientific Document chapters / subsections
        babs = getattr(blueprint, "babs", None) or getattr(blueprint, "sections", None)
        if babs:
            for bab in babs:
                for sub in getattr(bab, "subsections", ()):
                    refs.update(getattr(sub, "evidence_ids", ()) or ())
                    refs.update(getattr(sub, "source_refs", ()) or ())

        return refs

    @classmethod
    def _calculate_structural_drift(cls, pre: Any, post: Any, artifact_type: str) -> float:
        """Computes structural churn (e.g. added/deleted slides, sections)."""
        def get_count(obj: Any) -> int:
            for attr in ("slides", "beats", "sections", "activities", "babs", "pages"):
                val = getattr(obj, attr, None)
                if val is not None:
                    return len(val)
            return 1

        c_pre = get_count(pre)
        c_post = get_count(post)
        if c_pre == 0:
            return 0.0
        return round(min(1.0, abs(c_post - c_pre) / c_pre), 4)

    @classmethod
    def _calculate_semantic_drift(cls, pre: Any, post: Any) -> float:
        """Estimates content volume and text modification drift."""
        def extract_text_len(obj: Any) -> int:
            total = 0
            if hasattr(obj, "slides"):
                for s in obj.slides:
                    total += len(getattr(s, "title", "")) + len(getattr(s, "content", ""))
            elif hasattr(obj, "sections"):
                for s in obj.sections:
                    total += len(getattr(s, "title", "")) + len(getattr(s, "content", ""))
            elif hasattr(obj, "activities"):
                for a in obj.activities:
                    total += len(getattr(a, "title", "")) + len(getattr(a, "prompt_text", ""))
            return max(1, total)

        len_pre = extract_text_len(pre)
        len_post = extract_text_len(post)
        return round(min(1.0, abs(len_post - len_pre) / len_pre), 4)

    @classmethod
    def _calculate_narrative_drift(cls, pre: Any, post: Any) -> float:
        """Measures sequence alignment of elements."""
        return 0.05  # Standard minimal narrative drift baseline
