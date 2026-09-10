"""
Universal Document Intelligence System V5 — Cross-Artifact Divergence Benchmark.

Phase 5: Quantifies semantic and structural divergence across all four artifact outputs
generated from the same source knowledge. Enforces:
HIGH KNOWLEDGE OVERLAP != LOW ARTIFACT DIVERGENCE.
Detects and flags artifact collapse modes (Presentation->Handout, Worksheet->Quiz, etc.).
"""

from __future__ import annotations

import difflib
from typing import Any, Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, ConfigDict, Field


class CrossArtifactDivergenceReport(BaseModel):
    """Evaluation report measuring structural and pedagogical divergence across artifact types."""
    model_config = ConfigDict(frozen=True)

    case_id: str
    overall_divergence_score: float = Field(ge=0.0, le=1.0)
    is_sufficiently_divergent: bool
    pairwise_divergences: Dict[str, float] = Field(default_factory=dict)
    detected_collapses: List[str] = Field(default_factory=list)
    collapse_warnings: List[str] = Field(default_factory=list)
    structural_metrics: Dict[str, Any] = Field(default_factory=dict)


class CrossArtifactDivergenceBenchmark:
    """Benchmark engine evaluating artifact divergence and preventing cross-format homogenization."""

    DIVERGENCE_PASS_THRESHOLD: float = 0.50

    @classmethod
    def evaluate(
        cls,
        case_id: str,
        artifacts: Dict[str, Any],  # Mapping artifact_type -> artifact object or dict
    ) -> CrossArtifactDivergenceReport:
        """
        Evaluates cross-artifact divergence among generated outputs for a single case.
        Supports inputs as dictionaries, blueprints, or domain objects.
        """
        detected_collapses: List[str] = []
        collapse_warnings: List[str] = []
        pairwise: Dict[str, float] = {}

        types_present = list(artifacts.keys())

        # 1. Evaluate Individual Artifact Collapse Signals
        # A. PRESENTATION -> HANDOUT COLLAPSE
        if "PRESENTATION" in artifacts:
            pres = artifacts["PRESENTATION"]
            slides = cls._extract_slides(pres)
            if slides:
                dense_slides = 0
                for s in slides:
                    text = str(s.get("content", "") or s.get("CORE_MESSAGE", ""))
                    if len(text.split()) > 75:  # > 75 words on a slide
                        dense_slides += 1
                if len(slides) > 0 and (dense_slides / len(slides)) > 0.4:
                    detected_collapses.append(
                        "PRESENTATION_TO_HANDOUT_COLLAPSE: Excessive text density across "
                        f"{dense_slides}/{len(slides)} slides."
                    )

        # B. HANDOUT -> PRESENTATION FRAGMENTATION
        if "HANDOUT" in artifacts:
            handout = artifacts["HANDOUT"]
            sections = cls._extract_sections(handout)
            if sections:
                short_sections = 0
                for sec in sections:
                    content = str(sec.get("content", "") or sec.get("EXPLANATIONS", ""))
                    if len(content.split()) < 20 and not sec.get("definitions"):
                        short_sections += 1
                if len(sections) > 4 and (short_sections / len(sections)) > 0.6:
                    detected_collapses.append(
                        "HANDOUT_TO_PRESENTATION_FRAGMENTATION: Handout sections fragmented "
                        f"into micro-bullets without explanatory depth ({short_sections}/{len(sections)} sections)."
                    )

        # C. WORKSHEET -> QUIZ COLLAPSE & ANSWER LEAK
        if "WORKSHEET" in artifacts:
            ws = artifacts["WORKSHEET"]
            activities = cls._extract_activities(ws)
            if activities:
                leaks = 0
                for act in activities:
                    prompt = str(act.get("prompt_text", "") or act.get("PROMPT", ""))
                    withhold = act.get("withhold_explanation", True)
                    leak_flag = act.get("ANSWER_LEAK_RISK", False)
                    if not withhold or leak_flag or any(w in prompt.lower() for w in ["kunci jawaban:", "answer:", "jawaban yang benar:"]):
                        leaks += 1
                if leaks > 0:
                    detected_collapses.append(
                        f"WORKSHEET_TO_ANSWER_LEAK: {leaks} activities leak discovery answers to students."
                    )

                stages = [str(act.get("activity_type", "") or act.get("INQUIRY_STAGE", "")).upper() for act in activities]
                has_investigation = any(s in {"INVESTIGATION", "OBSERVATION", "PHENOMENON", "DATA_COLLECTION"} for s in stages)
                if not has_investigation and len(activities) >= 3:
                    detected_collapses.append(
                        "WORKSHEET_TO_QUIZ_COLLAPSE: Worksheet contains no inquiry or observation stages "
                        "— purely verbal recall."
                    )

        # D. SCIENTIFIC -> GENERIC ESSAY COLLAPSE
        if "SCIENTIFIC_DOCUMENT" in artifacts:
            kti = artifacts["SCIENTIFIC_DOCUMENT"]
            arguments = cls._extract_arguments(kti)
            if arguments:
                unsupported = 0
                for arg in arguments:
                    ev = arg.get("supporting_evidence_unit_ids") or arg.get("EVIDENCE") or arg.get("evidence_ids")
                    if not ev:
                        unsupported += 1
                if len(arguments) > 0 and (unsupported / len(arguments)) > 0.4:
                    detected_collapses.append(
                        "SCIENTIFIC_TO_GENERIC_ESSAY_COLLAPSE: Substantive claims lack empirical/literature evidence "
                        f"({unsupported}/{len(arguments)} claims unsupported)."
                    )

        # 2. Pairwise Structural Divergence Calculation
        for i in range(len(types_present)):
            for j in range(i + 1, len(types_present)):
                t1, t2 = types_present[i], types_present[j]
                pair_key = f"{t1}_vs_{t2}"
                div = cls._compute_pairwise_divergence(artifacts[t1], artifacts[t2])
                pairwise[pair_key] = round(div, 3)

                if div < 0.20:
                    detected_collapses.append(
                        f"CROSS_ARTIFACT_HOMOGENIZATION: {t1} and {t2} show dangerously low divergence ({div:.2f}) "
                        "— possible cosmetic-only reformatting of same output."
                    )

        avg_pair_div = sum(pairwise.values()) / len(pairwise) if pairwise else 1.0
        penalty = len(detected_collapses) * 0.25
        overall_score = max(0.0, min(1.0, avg_pair_div - penalty))
        is_sufficient = overall_score >= cls.DIVERGENCE_PASS_THRESHOLD and len(detected_collapses) == 0

        return CrossArtifactDivergenceReport(
            case_id=case_id,
            overall_divergence_score=round(overall_score, 3),
            is_sufficiently_divergent=is_sufficient,
            pairwise_divergences=pairwise,
            detected_collapses=detected_collapses,
            collapse_warnings=collapse_warnings,
            structural_metrics={
                "artifact_types_count": len(types_present),
                "pairwise_comparisons_count": len(pairwise),
                "collapses_count": len(detected_collapses)
            }
        )

    @classmethod
    def _extract_slides(cls, pres: Any) -> list[dict]:
        if isinstance(pres, dict):
            return pres.get("slides", [])
        if hasattr(pres, "slides"):
            return [s if isinstance(s, dict) else s.model_dump() for s in getattr(pres, "slides", [])]
        if hasattr(pres, "beats"):
            return [b if isinstance(b, dict) else b.model_dump() for b in getattr(pres, "beats", [])]
        return []

    @classmethod
    def _extract_sections(cls, handout: Any) -> list[dict]:
        if isinstance(handout, dict):
            return handout.get("sections", [])
        if hasattr(handout, "sections"):
            return [s if isinstance(s, dict) else s.model_dump() for s in getattr(handout, "sections", [])]
        return []

    @classmethod
    def _extract_activities(cls, ws: Any) -> list[dict]:
        if isinstance(ws, dict):
            return ws.get("activities", [])
        if hasattr(ws, "activities"):
            return [a if isinstance(a, dict) else a.model_dump() for a in getattr(ws, "activities", [])]
        return []

    @classmethod
    def _extract_arguments(cls, kti: Any) -> list[dict]:
        if isinstance(kti, dict):
            return kti.get("arguments", []) or kti.get("claims", [])
        if hasattr(kti, "arguments"):
            return [a if isinstance(a, dict) else a.model_dump() for a in getattr(kti, "arguments", [])]
        return []

    @classmethod
    def _compute_pairwise_divergence(cls, art1: Any, art2: Any) -> float:
        """Calculates structural divergence between two artifact representations."""
        str1 = cls._to_structural_fingerprint(art1)
        str2 = cls._to_structural_fingerprint(art2)
        ratio = difflib.SequenceMatcher(None, str1, str2).ratio()
        return 1.0 - ratio

    @classmethod
    def _to_structural_fingerprint(cls, art: Any) -> str:
        """Extracts native primary structural signature from artifact."""
        if hasattr(art, "model_dump"):
            art = art.model_dump()
            
        if isinstance(art, dict):
            # Prioritize native structural content keys
            if "slides" in art or "beats" in art:
                units = art.get("slides") or art.get("beats") or []
                roles = [u.get("SEMANTIC_ROLE", u.get("narrative_function", "SLIDE")) for u in units]
                return f"PRES_DECK(count={len(units)},roles={','.join(roles)})"
            elif "sections" in art:
                sections = art.get("sections") or []
                depths = [str(s.get("heading_level", s.get("level", 1))) for s in sections]
                return f"HANDOUT_DOC(count={len(sections)},depths={','.join(depths)})"
            elif "activities" in art:
                acts = art.get("activities") or []
                stages = [str(a.get("INQUIRY_STAGE", a.get("activity_type", "ACT"))) for a in acts]
                return f"WORKSHEET_LKS(count={len(acts)},stages={','.join(stages)})"
            elif "arguments" in art or "babs" in art:
                args = art.get("arguments") or art.get("babs") or []
                types = [str(a.get("EVIDENCE_TYPE", a.get("claim_type", "ARG"))) for a in args]
                return f"SCIENTIFIC_KTI(count={len(args)},ev_types={','.join(types)})"
            else:
                # Generic fallback
                keys = sorted(art.keys())
                return f"GENERIC({','.join(keys)})"
                
        return str(type(art).__name__)
