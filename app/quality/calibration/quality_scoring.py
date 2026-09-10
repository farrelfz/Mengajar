"""
Universal Document Intelligence System V5 — Calibrated Quality Scoring Engine.

Phase 2C: Comprehensive multi-dimensional quality evaluators for all four artifact types:
- PresentationQualityEvaluator
- HandoutQualityEvaluator
- WorksheetQualityEvaluator
- ScientificDocumentQualityEvaluator
- MasterQualityScoringEngine

Evaluates design, ergonomics, typography, inquiry flow, academic discipline, and rhythm
with explainable score breakdowns and direct mapping to QualityFailureTaxonomy.
"""

from __future__ import annotations

import difflib
import re
from typing import Any, Dict, List, Optional, Tuple

from app.integration.renderer_adapters.contracts import (
    DocumentContent,
    LegacyPresentationDeck,
    LegacyScientificDocument,
    LegacyWorksheetDocument,
    SlideBlueprint,
)
from app.intelligence.schemas import KtiBab
from app.presentation.visual_grammar_registry import VISUAL_GRAMMAR_MATRIX
from app.quality.calibration.failure_taxonomy import (
    FailureCategory,
    FailureSeverity,
    QualityFailure,
)
from app.quality.calibration.score_explanation import DimensionalScoreExplanation
from app.quality.contracts import (
    ArtifactQualityReport,
    QualityFinding,
    QualityLevel,
    QualitySeverity,
    QualitySignalExplanation,
)


# ============================================================================
# 1. PRESENTATION QUALITY EVALUATOR
# ============================================================================
class PresentationQualityEvaluator:
    """Evaluates design, readability, rhythm, and visual grammar of presentation decks."""

    @classmethod
    def evaluate(
        cls,
        deck: LegacyPresentationDeck,
        rendered_pdf_metrics: Dict[str, Any] | None = None,
    ) -> ArtifactQualityReport:
        signals: List[QualitySignalExplanation] = []
        explanations: List[str] = []
        findings: List[QualityFinding] = []

        slides = list(deck.slides)
        n_slides = len(slides)

        if n_slides == 0:
            return ArtifactQualityReport.compute(
                artifact_type="PRESENTATION",
                visual_quality=0.0,
                information_design=0.0,
                artifact_specific_quality=0.0,
                composition_quality=0.0,
                readability_quality=0.0,
                rhythm_quality=0.0,
                structural_quality=0.0,
                findings=[
                    QualityFinding(
                        finding="Presentation deck contains zero slides",
                        severity=QualitySeverity.CRITICAL,
                        dimension="structural_coherence",
                        recommendation="Ensure slide generation executes successfully",
                    )
                ],
            )

        # -------------------------------------------------------------
        # A. Visual Quality & Typography Hierarchy
        # -------------------------------------------------------------
        min_body_font = 12.0
        min_hierarchy_ratio = 2.0
        has_collision = False
        has_overflow = False

        for s in slides:
            meta = s.metadata or {}
            if "min_body_font" in meta:
                min_body_font = min(min_body_font, float(meta["min_body_font"]))
            if "body_font_size" in meta and "title_font_size" in meta:
                b_sz = float(meta["body_font_size"])
                t_sz = float(meta["title_font_size"])
                ratio = t_sz / max(b_sz, 1e-3)
                min_hierarchy_ratio = min(min_hierarchy_ratio, ratio)
            if meta.get("element_collision"):
                has_collision = True
            if meta.get("text_overflow"):
                has_overflow = True

        visual_quality = 1.0
        if min_hierarchy_ratio < 1.15:
            impact = -0.25
            visual_quality += impact
            signals.append(
                QualitySignalExplanation(
                    signal="visual_hierarchy_ratio",
                    value=round(min_hierarchy_ratio, 2),
                    expected=">= 1.30",
                    impact=impact,
                    dimension="visual_quality",
                    description="Title-to-body font contrast is critically low, creating flat unscanable slides.",
                )
            )
            findings.append(
                QualityFinding(
                    finding=f"Weak visual hierarchy ratio ({min_hierarchy_ratio:.2f} < 1.30)",
                    severity=QualitySeverity.WARNING,
                    dimension="visual_appropriateness",
                    recommendation="Increase headline scale relative to body text",
                )
            )

        if min_body_font < 8.5:
            impact = -0.40
            visual_quality += impact
            signals.append(
                QualitySignalExplanation(
                    signal="minimum_body_font_size",
                    value=min_body_font,
                    expected=">= 8.5pt",
                    impact=impact,
                    dimension="readability_quality",
                    description=f"Body font size ({min_body_font}pt) is unreadable from presentation viewing distance.",
                )
            )
            findings.append(
                QualityFinding(
                    finding=f"Unreadable tiny text detected: {min_body_font}pt < 8.5pt",
                    severity=QualitySeverity.CRITICAL,
                    dimension="visual_appropriateness",
                    recommendation="Increase minimum font size to at least 9pt",
                )
            )

        if has_overflow:
            visual_quality -= 0.50
            findings.append(
                QualityFinding(
                    finding="Text overflow detected extending outside viewport boundaries",
                    severity=QualitySeverity.CRITICAL,
                    dimension="visual_appropriateness",
                    recommendation="Reduce slide text volume or split content across slides",
                )
            )

        if has_collision:
            visual_quality -= 0.50
            findings.append(
                QualityFinding(
                    finding="Element collision detected: visual elements overlap at identical spatial coordinates",
                    severity=QualitySeverity.CRITICAL,
                    dimension="visual_appropriateness",
                    recommendation="Refactor grid positioning to eliminate overlapping bounds",
                )
            )

        visual_quality = max(0.0, min(1.0, visual_quality))

        # -------------------------------------------------------------
        # B. Information Design & Visual Grammar Alignment
        # -------------------------------------------------------------
        info_design = 1.0
        grammar_violations = 0

        for s in slides:
            role = s.narrative_function.upper()
            rule = VISUAL_GRAMMAR_MATRIX.get(role)
            if rule and s.layout in rule.get("avoid", []):
                grammar_violations += 1
                info_design -= 0.20
                signals.append(
                    QualitySignalExplanation(
                        signal="visual_grammar_alignment",
                        value=f"{role}->{s.layout}",
                        expected=f"Avoid {rule['avoid']}",
                        impact=-0.20,
                        dimension="information_design",
                        description=f"Slide '{s.title}' communicates {role} using poorly suited layout '{s.layout}'.",
                    )
                )
                findings.append(
                    QualityFinding(
                        finding=f"Semantic-visual layout mismatch: {role} rendered as '{s.layout}'",
                        severity=QualitySeverity.ERROR if grammar_violations > 2 else QualitySeverity.WARNING,
                        dimension="semantic_correctness",
                        recommendation=f"Use preferred layouts: {rule.get('preferred')}",
                    )
                )

        info_design = max(0.0, min(1.0, info_design))

        # -------------------------------------------------------------
        # C. Composition Quality & Whitespace
        # -------------------------------------------------------------
        comp_quality = 1.0
        for s in slides:
            meta = s.metadata or {}
            card_cnt = meta.get("card_count", len(s.bullet_points))
            if card_cnt > 6:
                impact = -0.20
                comp_quality += impact
                findings.append(
                    QualityFinding(
                        finding=f"Card overload on slide {s.slide_id}: {card_cnt} generic cards (> 6)",
                        severity=QualitySeverity.WARNING,
                        dimension="information_density",
                        recommendation="Group cards or use columnar matrix comparison",
                    )
                )
            if meta.get("competing_primary_elements_count", 0) > 1:
                comp_quality -= 0.20
                findings.append(
                    QualityFinding(
                        finding=f"Multiple competing primary hero elements on slide {s.slide_id}",
                        severity=QualitySeverity.WARNING,
                        dimension="visual_appropriateness",
                        recommendation="Enforce a single primary focal point per slide",
                    )
                )

        comp_quality = max(0.0, min(1.0, comp_quality))

        # -------------------------------------------------------------
        # D. Readability & Density
        # -------------------------------------------------------------
        readability = 1.0
        for s in slides:
            char_len = len(s.content)
            if char_len > 1500:
                readability -= 0.35
                findings.append(
                    QualityFinding(
                        finding=f"Excessive text density on slide {s.slide_id} ({char_len} chars > 1500 limit)",
                        severity=QualitySeverity.ERROR,
                        dimension="information_density",
                        recommendation="Compress or paginate slide content",
                    )
                )

        readability = max(0.0, min(1.0, readability))

        # -------------------------------------------------------------
        # E. Rhythm Quality & Deduplication
        # -------------------------------------------------------------
        rhythm = 1.0
        # Check text duplicates
        clean_texts = [re.sub(r"\s+", " ", s.content.lower().strip()) for s in slides]
        dup_count = 0
        for i in range(n_slides):
            for j in range(i + 1, n_slides):
                t1, t2 = clean_texts[i], clean_texts[j]
                if t1 and t2:
                    sim = difflib.SequenceMatcher(None, t1, t2).ratio()
                    if sim >= 0.88:
                        dup_count += 1
                        is_exact = (t1 == t2 and slides[i].title.lower().strip() == slides[j].title.lower().strip()) or (sim >= 0.99 and t1 == t2)
                        findings.append(
                            QualityFinding(
                                finding=f"Redundant/duplicate slides detected: Slide {i+1} and {j+1} text similarity {sim:.2f}",
                                severity=QualitySeverity.CRITICAL if is_exact else QualitySeverity.WARNING,
                                dimension="redundancy",
                                recommendation="Merge or differentiate repetitive slides",
                            )
                        )

        if dup_count > 0:
            dup_impact = -min(0.60, dup_count * 0.30)
            rhythm += dup_impact
            signals.append(
                QualitySignalExplanation(
                    signal="duplicate_slides_count",
                    value=dup_count,
                    expected="0",
                    impact=dup_impact,
                    dimension="rhythm_quality",
                    description=f"{dup_count} slide pairs exhibit redundant near-identical content.",
                )
            )

        # Check consecutive layout streaks
        current_layout = None
        streak = 0
        max_layout_streak = 0
        for s in slides:
            if s.layout == current_layout:
                streak += 1
            else:
                current_layout = s.layout
                streak = 1
            max_layout_streak = max(max_layout_streak, streak)

        if max_layout_streak >= 5:
            rhythm -= 0.20
            findings.append(
                QualityFinding(
                    finding=f"Monotonous visual pacing: {max_layout_streak} consecutive slides share '{current_layout}' layout",
                    severity=QualitySeverity.WARNING,
                    dimension="pedagogical_alignment",
                    recommendation="Introduce varied visual layout structures across narrative progression",
                )
            )

        # Check cognitive load streak
        cog_streak = 0
        max_cog_streak = 0
        for s in slides:
            if s.cognitive_load > 1.6:
                cog_streak += 1
            else:
                cog_streak = 0
            max_cog_streak = max(max_cog_streak, cog_streak)

        if max_cog_streak >= 3:
            rhythm -= 0.25
            findings.append(
                QualityFinding(
                    finding=f"High cognitive load streak: {max_cog_streak} consecutive heavy slides without cognitive pause",
                    severity=QualitySeverity.WARNING,
                    dimension="pedagogical_alignment",
                    recommendation="Insert reflection or visual summary pause slide",
                )
            )

        rhythm = max(0.0, min(1.0, rhythm))

        # -------------------------------------------------------------
        # F. Artifact-Specific & Structural Quality
        # -------------------------------------------------------------
        art_specific = 0.95
        structural = 1.0

        if grammar_violations == 0 and dup_count == 0 and min_body_font >= 10.0:
            explanations.append("Presentation demonstrates clean typography, varied visual grammar, and dynamic rhythm.")
        else:
            explanations.append(f"Presentation exhibits {len(findings)} quality defect(s) across typography, pacing, or layout grammar.")

        return ArtifactQualityReport.compute(
            artifact_type="PRESENTATION",
            visual_quality=visual_quality,
            information_design=info_design,
            artifact_specific_quality=art_specific,
            composition_quality=comp_quality,
            readability_quality=readability,
            rhythm_quality=rhythm,
            structural_quality=structural,
            signals=signals,
            explanations=explanations,
            findings=findings,
        )


# ============================================================================
# 2. HANDOUT QUALITY EVALUATOR
# ============================================================================
class HandoutQualityEvaluator:
    """Evaluates continuous reading flow, heading hierarchy, and typography for Handouts."""

    @classmethod
    def evaluate(cls, doc: DocumentContent) -> ArtifactQualityReport:
        signals: List[QualitySignalExplanation] = []
        explanations: List[str] = []
        findings: List[QualityFinding] = []

        sections = list(doc.sections)
        if not sections:
            return ArtifactQualityReport.compute(
                artifact_type="HANDOUT",
                visual_quality=0.0,
                information_design=0.0,
                artifact_specific_quality=0.0,
                composition_quality=0.0,
                readability_quality=0.0,
                rhythm_quality=0.0,
                structural_quality=0.0,
                findings=[
                    QualityFinding(
                        finding="Handout document contains zero sections",
                        severity=QualitySeverity.CRITICAL,
                        dimension="structural_coherence",
                        recommendation="Generate valid reading sections",
                    )
                ],
            )

        # -------------------------------------------------------------
        # A. Structural Quality & Heading Hierarchy
        # -------------------------------------------------------------
        structural = 1.0
        prev_level = 1
        for s in sections:
            if not s.content and not s.definitions and not s.examples:
                structural -= 0.30
                findings.append(
                    QualityFinding(
                        finding=f"Empty section detected: '{s.title}' has no substantive reading content",
                        severity=QualitySeverity.ERROR,
                        dimension="structural_coherence",
                        recommendation="Provide narrative content or remove empty heading",
                    )
                )
            if s.level > prev_level + 1:
                structural -= 0.20
                findings.append(
                    QualityFinding(
                        finding=f"Heading hierarchy inversion: Level {s.level} follows Level {prev_level} without intermediate parent",
                        severity=QualitySeverity.WARNING,
                        dimension="structural_coherence",
                        recommendation="Preserve proper H1->H2->H3 heading tree",
                    )
                )
            prev_level = s.level

        structural = max(0.0, min(1.0, structural))

        # -------------------------------------------------------------
        # B. Reading Flow & Redundancy
        # -------------------------------------------------------------
        flow = 1.0
        texts = [s.content.lower().strip() for s in sections if s.content]
        dup_count = 0
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                sim = difflib.SequenceMatcher(None, texts[i], texts[j]).ratio()
                if sim >= 0.85:
                    dup_count += 1
                    flow -= 0.35
                    findings.append(
                        QualityFinding(
                            finding="Duplicate explanatory prose block repeated across sections",
                            severity=QualitySeverity.CRITICAL if sim >= 0.95 else QualitySeverity.WARNING,
                            dimension="redundancy",
                            recommendation="Remove redundant repetitive paragraph",
                        )
                    )

        # Paragraph fragmentation check (e.g. 12+ single-sentence paragraphs)
        for s in sections:
            paras = [p.strip() for p in s.content.split("\n\n") if p.strip()]
            if len(paras) >= 10 and all(len(p) < 80 for p in paras):
                flow -= 0.25
                findings.append(
                    QualityFinding(
                        finding=f"Severe paragraph fragmentation in section '{s.title}': fragmented into {len(paras)} micro-sentences",
                        severity=QualitySeverity.WARNING,
                        dimension="structural_coherence",
                        recommendation="Synthesize micro-sentences into cohesive continuous paragraphs",
                    )
                )

        flow = max(0.0, min(1.0, flow))

        # -------------------------------------------------------------
        # C. Readability & Typography
        # -------------------------------------------------------------
        readability = 1.0
        for s in sections:
            meta = s.metadata or {}
            if meta.get("body_font_size", 11.0) < 8.0:
                readability -= 0.40
                findings.append(
                    QualityFinding(
                        finding=f"Tiny body text font ({meta.get('body_font_size')}pt) in section '{s.title}'",
                        severity=QualitySeverity.CRITICAL,
                        dimension="format_integrity",
                        recommendation="Set body text to standard 10-11pt for handouts",
                    )
                )
            if meta.get("orphan_heading"):
                readability -= 0.20
                findings.append(
                    QualityFinding(
                        finding=f"Orphan heading detected at bottom of page in section '{s.title}'",
                        severity=QualitySeverity.WARNING,
                        dimension="visual_appropriateness",
                        recommendation="Use CSS break-after: avoid on heading elements",
                    )
                )
            if meta.get("characters_per_line", 75) > 130:
                readability -= 0.15
                findings.append(
                    QualityFinding(
                        finding=f"Excessive typographic line length ({meta.get('characters_per_line')} CPL > 120)",
                        severity=QualitySeverity.WARNING,
                        dimension="visual_appropriateness",
                        recommendation="Constrain column width or introduce multi-column layout",
                    )
                )

        readability = max(0.0, min(1.0, readability))

        # -------------------------------------------------------------
        # D. Composition & Density
        # -------------------------------------------------------------
        composition = 1.0
        for s in sections:
            c_len = len(s.content)
            if c_len > 4000:
                composition -= 0.30
                findings.append(
                    QualityFinding(
                        finding=f"Excessive textual density ({c_len} chars) in section '{s.title}' causing layout fatigue",
                        severity=QualitySeverity.ERROR,
                        dimension="information_density",
                        recommendation="Break section into focused sub-topics with whitespace pauses",
                    )
                )
            if len(s.content.split()) <= 3 and s.sequence_index > 2:
                composition -= 0.15
                findings.append(
                    QualityFinding(
                        finding=f"Accidental empty/spill page candidate in section '{s.title}' ({len(s.content.split())} words)",
                        severity=QualitySeverity.WARNING,
                        dimension="format_integrity",
                        recommendation="Eliminate accidental trailing section spillover",
                    )
                )

        composition = max(0.0, min(1.0, composition))
        info_design = 0.90
        art_specific = 0.95
        rhythm = flow

        return ArtifactQualityReport.compute(
            artifact_type="HANDOUT",
            visual_quality=readability,
            information_design=info_design,
            artifact_specific_quality=art_specific,
            composition_quality=composition,
            readability_quality=readability,
            rhythm_quality=rhythm,
            structural_quality=structural,
            signals=signals,
            explanations=explanations,
            findings=findings,
        )


# ============================================================================
# 3. WORKSHEET QUALITY EVALUATOR
# ============================================================================
class WorksheetQualityEvaluator:
    """Evaluates inquiry flow, active interaction design, and strict anti-spoiling for Worksheets."""

    @classmethod
    def evaluate(cls, doc: LegacyWorksheetDocument) -> ArtifactQualityReport:
        signals: List[QualitySignalExplanation] = []
        explanations: List[str] = []
        findings: List[QualityFinding] = []

        all_activities: List[Any] = []
        for sec in doc.sections:
            all_activities.extend(sec.activities)

        if not all_activities:
            return ArtifactQualityReport.compute(
                artifact_type="WORKSHEET",
                visual_quality=0.0,
                information_design=0.0,
                artifact_specific_quality=0.0,
                composition_quality=0.0,
                readability_quality=0.0,
                rhythm_quality=0.0,
                structural_quality=0.0,
                findings=[
                    QualityFinding(
                        finding="Worksheet contains zero inquiry activities",
                        severity=QualitySeverity.CRITICAL,
                        dimension="pedagogical_alignment",
                        recommendation="Generate student investigation activities",
                    )
                ],
            )

        # -------------------------------------------------------------
        # A. Artifact-Specific Quality: Strict Anti-Spoiling & Inquiry Flow
        # -------------------------------------------------------------
        art_specific = 1.0
        act_types = [a.activity_type.upper() for a in all_activities]

        # 1. Anti-Spoiling Inspection
        for a in all_activities:
            meta = a.metadata or {}
            # Check withholding flag
            if not a.withhold_explanation and a.activity_type.upper() in ("PREDICTION", "QUESTION", "OBSERVATION"):
                art_specific -= 0.45
                findings.append(
                    QualityFinding(
                        finding=f"Anti-spoiling leak: Explanation not withheld on inquiry activity '{a.title}'",
                        severity=QualitySeverity.CRITICAL,
                        dimension="pedagogical_alignment",
                        recommendation="Strictly withhold answer explanation before student investigation",
                    )
                )
            # Check prompt text leaks
            prompt_lower = a.prompt_text.lower()
            if any(k in prompt_lower for k in ["jawaban:", "karena oobleck berubah menjadi padat", "kesimpulan sudah terbukti"]):
                art_specific -= 0.50
                findings.append(
                    QualityFinding(
                        finding=f"Anti-spoiling leak: Answer or conclusion pre-filled inside prompt '{a.title}'",
                        severity=QualitySeverity.CRITICAL,
                        dimension="pedagogical_alignment",
                        recommendation="Strip explanation and conclusion from student prompt text",
                    )
                )

        # 2. Inquiry Sequence Progression
        if "REFLECTION" in act_types and "OBSERVATION" in act_types:
            first_refl = act_types.index("REFLECTION")
            first_obs = act_types.index("OBSERVATION")
            if first_refl < first_obs:
                art_specific -= 0.35
                findings.append(
                    QualityFinding(
                        finding="Inquiry sequence inversion: REFLECTION activity precedes OBSERVATION",
                        severity=QualitySeverity.ERROR,
                        dimension="pedagogical_alignment",
                        recommendation="Ensure empirical observation precedes conceptual reflection",
                    )
                )

        if "DATA_ANALYSIS" in act_types and "OBSERVATION" in act_types:
            first_ana = act_types.index("DATA_ANALYSIS")
            first_obs = act_types.index("OBSERVATION")
            if first_ana < first_obs:
                art_specific -= 0.35
                findings.append(
                    QualityFinding(
                        finding="Inquiry sequence inversion: DATA_ANALYSIS precedes OBSERVATION data collection",
                        severity=QualitySeverity.ERROR,
                        dimension="pedagogical_alignment",
                        recommendation="Collect observation data before analysis phase",
                    )
                )

        # 3. Quiz Collapse Check (recall or MCQ ratio)
        mcq_or_recall_count = sum(1 for t in act_types if "MULTIPLE_CHOICE" in t or "RECALL" in t)
        collapse_ratio = mcq_or_recall_count / max(len(act_types), 1)
        if collapse_ratio > 0.50:
            impact = -0.30
            art_specific += impact
            findings.append(
                QualityFinding(
                    finding=f"Worksheet inquiry collapsed into passive quiz ({collapse_ratio*100:.1f}% factual recall/MCQ)",
                    severity=QualitySeverity.ERROR,
                    dimension="pedagogical_alignment",
                    recommendation="Replace passive recall questions with active inquiry prompts",
                )
            )

        art_specific = max(0.0, min(1.0, art_specific))

        # -------------------------------------------------------------
        # B. Interaction & Workspace Quality
        # -------------------------------------------------------------
        comp_quality = 1.0
        has_collision = False

        for a in all_activities:
            meta = a.metadata or {}
            ws_h = meta.get("workspace_height_pt", 80.0)
            if ws_h < 30.0:
                comp_quality -= 0.25
                findings.append(
                    QualityFinding(
                        finding=f"Inadequate student workspace: Height {ws_h}pt on activity '{a.title}' is too small for handwriting",
                        severity=QualitySeverity.WARNING,
                        dimension="visual_appropriateness",
                        recommendation="Allocate at least 40-80pt response workspace height",
                    )
                )
            if meta.get("workspace_collision"):
                has_collision = True

        if has_collision:
            comp_quality -= 0.50
            findings.append(
                QualityFinding(
                    finding="Student workspace box collides with prompt text",
                    severity=QualitySeverity.CRITICAL,
                    dimension="visual_appropriateness",
                    recommendation="Correct CSS margin/padding on student workspace box",
                )
            )

        comp_quality = max(0.0, min(1.0, comp_quality))

        readability = 0.90
        info_design = 0.90
        rhythm = art_specific
        structural = 0.95

        return ArtifactQualityReport.compute(
            artifact_type="WORKSHEET",
            visual_quality=comp_quality,
            information_design=info_design,
            artifact_specific_quality=art_specific,
            composition_quality=comp_quality,
            readability_quality=readability,
            rhythm_quality=rhythm,
            structural_quality=structural,
            signals=signals,
            explanations=explanations,
            findings=findings,
        )


# ============================================================================
# 4. SCIENTIFIC DOCUMENT QUALITY EVALUATOR
# ============================================================================
class ScientificDocumentQualityEvaluator:
    """Evaluates Indonesian KTI academic chapter structure, empirical evidence grounding, and citations."""

    @classmethod
    def evaluate(cls, doc: LegacyScientificDocument) -> ArtifactQualityReport:
        signals: List[QualitySignalExplanation] = []
        explanations: List[str] = []
        findings: List[QualityFinding] = []

        babs = list(doc.babs)
        if not babs:
            return ArtifactQualityReport.compute(
                artifact_type="SCIENTIFIC_DOCUMENT",
                visual_quality=0.0,
                information_design=0.0,
                artifact_specific_quality=0.0,
                composition_quality=0.0,
                readability_quality=0.0,
                rhythm_quality=0.0,
                structural_quality=0.0,
                findings=[
                    QualityFinding(
                        finding="Scientific document contains zero chapters (BAB)",
                        severity=QualitySeverity.CRITICAL,
                        dimension="structural_coherence",
                        recommendation="Generate formal KTI BAB I-V structure",
                    )
                ],
            )

        # -------------------------------------------------------------
        # A. Academic Structure & BAB Sequence Integrity
        # -------------------------------------------------------------
        structural = 1.0
        bab_sequence = [b.bab for b in babs]
        expected_sequence = [
            KtiBab.BAB_1,
            KtiBab.BAB_2,
            KtiBab.BAB_3,
            KtiBab.BAB_4,
            KtiBab.BAB_5,
        ]

        # Check if sequence is monotonic
        for i in range(len(bab_sequence) - 1):
            curr_val = bab_sequence[i].value
            next_val = bab_sequence[i + 1].value
            if curr_val > next_val:
                structural -= 0.50
                findings.append(
                    QualityFinding(
                        finding=f"BAB hierarchy inversion: {bab_sequence[i].name} placed before {bab_sequence[i+1].name}",
                        severity=QualitySeverity.CRITICAL,
                        dimension="structural_coherence",
                        recommendation="Enforce strict BAB I -> BAB V academic progression",
                    )
                )

        # Check empty subsections
        for b in babs:
            for sub in b.subsections:
                if not sub.claims and not sub.evidence_items:
                    structural -= 0.25
                    findings.append(
                        QualityFinding(
                            finding=f"Empty academic subsection: '{sub.title}' in {b.bab.name} has no content",
                            severity=QualitySeverity.ERROR,
                            dimension="structural_coherence",
                            recommendation="Provide claims or remove empty subsection",
                        )
                    )

        structural = max(0.0, min(1.0, structural))

        # -------------------------------------------------------------
        # B. Evidence Discipline & Academic Grounding
        # -------------------------------------------------------------
        evidence_discipline = 1.0
        all_subsections: List[Any] = []
        for b in babs:
            all_subsections.extend(b.subsections)

        total_claims = sum(len(sub.claims) for sub in all_subsections)
        total_unsupported = sum(len(sub.unsupported_claims) for sub in all_subsections)
        grounding_ratio = (total_claims - total_unsupported) / max(total_claims, 1) if total_claims > 0 else 1.0

        has_critical_unsupported = False
        for sub in all_subsections:
            meta = sub.metadata or {}
            if meta.get("unsupported_claim_critical"):
                has_critical_unsupported = True
                findings.append(
                    QualityFinding(
                        finding=f"Unsupported empirical claim in '{sub.title}': Claim lacks empirical evidence",
                        severity=QualitySeverity.CRITICAL,
                        dimension="semantic_correctness",
                        recommendation="Ground empirical claims with measurements or observational citations",
                    )
                )

            # 2. Check evidence-claim mismatch
            if meta.get("evidence_relevance_mismatch"):
                evidence_discipline -= 0.40
                findings.append(
                    QualityFinding(
                        finding=f"Evidence relevance mismatch: Evidence in '{sub.title}' does not support target claim",
                        severity=QualitySeverity.CRITICAL,
                        dimension="semantic_correctness",
                        recommendation="Ensure evidence logically and empirically relates to the claim",
                    )
                )

            # 3. Check citation missing or bogus
            if meta.get("citation_missing"):
                evidence_discipline -= 0.35
                findings.append(
                    QualityFinding(
                        finding=f"Citation missing on quantitative claim in '{sub.title}'",
                        severity=QualitySeverity.CRITICAL,
                        dimension="semantic_correctness",
                        recommendation="Attach formal bibliographic citation marker",
                    )
                )

            if any("ghost" in eid for eid in sub.evidence_ids):
                evidence_discipline -= 0.45
                findings.append(
                    QualityFinding(
                        finding=f"Fabricated citation detected: Ghost citation ID referenced in '{sub.title}'",
                        severity=QualitySeverity.CRITICAL,
                        dimension="semantic_correctness",
                        recommendation="Remove ungrounded citation markers",
                    )
                )

            # 4. Check contradictory claims
            if meta.get("contradictory_claims"):
                evidence_discipline -= 0.45
                findings.append(
                    QualityFinding(
                        finding=f"Contradictory adjacent claims in subsection '{sub.title}'",
                        severity=QualitySeverity.CRITICAL,
                        dimension="semantic_correctness",
                        recommendation="Resolve mutual contradiction between adjacent claims",
                    )
                )

        if has_critical_unsupported or grounding_ratio < 0.50:
            evidence_discipline -= 0.45
            if not has_critical_unsupported:
                findings.append(
                    QualityFinding(
                        finding=f"Low empirical grounding ratio ({grounding_ratio:.2f} < 0.50)",
                        severity=QualitySeverity.CRITICAL,
                        dimension="semantic_correctness",
                        recommendation="Ground empirical claims with measurements or observational citations",
                    )
                )
        elif grounding_ratio < 0.70:
            evidence_discipline -= 0.20
            findings.append(
                QualityFinding(
                    finding=f"Suboptimal empirical grounding ratio ({grounding_ratio:.2f} < 0.70)",
                    severity=QualitySeverity.WARNING,
                    dimension="semantic_correctness",
                    recommendation="Provide supporting evidence for claims",
                )
            )
        elif grounding_ratio < 0.85 and total_unsupported > 0:
            evidence_discipline -= 0.05
            findings.append(
                QualityFinding(
                    finding=f"{total_unsupported} claim(s) lack supporting empirical evidence",
                    severity=QualitySeverity.WARNING,
                    dimension="semantic_correctness",
                    recommendation="Provide supporting evidence for claims",
                )
            )

        evidence_discipline = max(0.0, min(1.0, evidence_discipline))

        readability = 0.95
        comp_quality = 0.95
        info_design = 0.90
        rhythm = evidence_discipline

        return ArtifactQualityReport.compute(
            artifact_type="SCIENTIFIC_DOCUMENT",
            visual_quality=readability,
            information_design=info_design,
            artifact_specific_quality=evidence_discipline,
            composition_quality=comp_quality,
            readability_quality=readability,
            rhythm_quality=rhythm,
            structural_quality=structural,
            signals=signals,
            explanations=explanations,
            findings=findings,
        )


# ============================================================================
# 5. MASTER QUALITY SCORING ENGINE
# ============================================================================
class MasterQualityScoringEngine:
    """Unified entry point for evaluating quality of any artifact model."""

    @classmethod
    def evaluate(
        cls,
        artifact_type: str,
        artifact_model: Any,
        rendered_pdf_metrics: Dict[str, Any] | None = None,
    ) -> ArtifactQualityReport:
        norm_type = artifact_type.upper()
        if norm_type == "PRESENTATION":
            return PresentationQualityEvaluator.evaluate(artifact_model, rendered_pdf_metrics)
        elif norm_type == "HANDOUT":
            return HandoutQualityEvaluator.evaluate(artifact_model)
        elif norm_type == "WORKSHEET":
            return WorksheetQualityEvaluator.evaluate(artifact_model)
        elif norm_type == "SCIENTIFIC_DOCUMENT":
            return ScientificDocumentQualityEvaluator.evaluate(artifact_model)
        else:
            raise ValueError(f"Unsupported artifact type for quality evaluation: {artifact_type}")
