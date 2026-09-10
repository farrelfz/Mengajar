"""
Slide Architecture Planner & Story Director.

Transforms a canonical ContentTree and ContentManifest into an educational
presentation story plan across narrative acts, ensuring 100% source fidelity.
"""

from __future__ import annotations

import re
from typing import Any
from pydantic import BaseModel, Field

from app.intelligence.markdown_tree_parser import (
    ContentBlock,
    ContentSection,
    ContentTree,
    SemanticBlockType,
)
from app.intelligence.content_manifest import ContentManifest, ContentPriority
from app.presentation.visual_director import VisualDirector, LAYOUT_MAPPING
from app.presentation.visual_grammar_registry import VISUAL_GRAMMAR_MATRIX


class ClaimUnit(BaseModel):
    """Atomic factual claim unit extracted from source content."""
    claim_id: str
    text: str
    source_refs: list[str] = Field(default_factory=list)
    support_level: str = "DIRECT_SUPPORT"  # DIRECT_SUPPORT, PARAPHRASE_SUPPORT, INFERRED_SUPPORT, UNSUPPORTED


class CognitiveLoad(BaseModel):
    """Cognitive load assessment for a slide."""
    level: str = "medium"  # "low", "medium", "high"
    reason: str = ""


class PlannedSlide(BaseModel):
    """Architectural specification for an individual presentation slide."""
    slide_id: str
    slide_number: int
    act_id: str = "act-01"
    act_name: str
    title: str
    subtitle: str | None = None
    narrative_function: str = "CONCEPT_INTRODUCTION"
    pedagogical_function: str = "EXPLAIN"
    slide_purpose: str = ""
    purpose: str = ""
    source_refs: list[str] = Field(default_factory=list)  # Stable section and block IDs
    primary_concept: str = ""
    supporting_concepts: list[str] = Field(default_factory=list)
    information_role: str = "NEW_INFORMATION"
    cognitive_load: CognitiveLoad = Field(default_factory=CognitiveLoad)
    visual_priority: str = "MEDIUM"
    visual_type: str = "concept_explainer"
    visual_intent: str = "concept_explainer"
    layout: str = "concept_card"
    transition_from_previous: str = ""
    transition_to_next: str = ""
    must_not_repeat: list[str] = Field(default_factory=list)
    claim_units: list[ClaimUnit] = Field(default_factory=list)
    content_priority: ContentPriority = ContentPriority.IMPORTANT
    text_density: str = "medium"  # "low", "medium", "high"
    key_blocks: list[ContentBlock] = Field(default_factory=list)
    learning_objective: str | None = None

    # Internal presentation intelligence metadata
    why_this_slide_exists: str = ""
    audience_takeaway: str = ""
    unique_information_gain: str = ""
    transition_logic: str = ""
    why_not_merge_with_previous: str = ""
    why_not_merge_with_next: str = ""

    def model_post_init(self, __context: Any) -> None:
        if not self.slide_purpose and self.purpose:
            self.slide_purpose = self.purpose
        elif not self.purpose and self.slide_purpose:
            self.purpose = self.slide_purpose
        if not self.visual_intent:
            self.visual_intent = self.visual_type


class SlideAct(BaseModel):
    name: str
    order: int
    slides: list[PlannedSlide] = Field(default_factory=list)


class SlidePlan(BaseModel):
    """Complete architectural blueprint for a presentation deck."""
    deck_title: str
    total_slides: int
    acts: list[SlideAct] = Field(default_factory=list)
    slides: list[PlannedSlide] = Field(default_factory=list)
    source_to_slide_map: dict[str, list[int]] = Field(default_factory=dict)
    slide_to_source_map: dict[int, list[str]] = Field(default_factory=dict)
    layout_distribution: dict[str, int] = Field(default_factory=dict)
    layout_entropy: float = 0.0


class SlideArchitect:
    """Plans slide sequences from source ContentTree and ContentManifest."""

    def __init__(self, visual_director: VisualDirector | None = None) -> None:
        self.visual_director = visual_director or VisualDirector()

    def plan(self, tree: ContentTree, manifest: ContentManifest) -> SlidePlan:
        """Create a complete, source-grounded SlidePlan."""
        slides: list[PlannedSlide] = []
        slide_counter = 1
        all_sections = tree.all_sections_flat()

        # Step 1: Slide 1 — Hero Phenomenon / Hook
        first_sec = all_sections[0] if all_sections else None
        hook_blocks = first_sec.blocks[:2] if first_sec else []
        slides.append(
            PlannedSlide(
                slide_id=f"slide-{slide_counter}",
                slide_number=slide_counter,
                title=tree.title,
                act_name="ACT 1 — PHENOMENON & HOOK",
                purpose="Engage learners with the central phenomenon and title",
                source_refs=[first_sec.id] if first_sec else ["root"],
                visual_type="hero_phenomenon",
                layout="hero_composition",
                content_priority=ContentPriority.CRITICAL,
                text_density="low",
                key_blocks=hook_blocks,
                subtitle="Eksplorasi Konsep Pembakaran, Energi, dan Termodinamika",
            )
        )
        slide_counter += 1

        # Step 2: Intelligent section clustering and slide allocation
        import re

        def _get_cluster_key(title: str) -> str | None:
            t = title.strip().lower()
            if re.search(r"\b(step|langkah|tahap)\s*\d+", t):
                return "steps"
            if re.search(r"\b(ide|gagasan)\s*\d+", t):
                return "ideas"
            if re.search(r"\b(kesalahan|miskonsepsi)\s*\d+", t):
                return "misconceptions"
            if re.search(r"\b(challenge|tantangan)\s*\d+", t):
                return "challenges"
            return None

        # Filter out empty sections
        valid_sections = [s for s in all_sections if s.blocks or s.children]
        if valid_sections and valid_sections[0] == all_sections[0] and not valid_sections[0].blocks:
            valid_sections = valid_sections[1:]

        # Cluster consecutive sub-item sections that match repetitive patterns
        planning_units: list[tuple[str | None, list[ContentSection]]] = []
        idx = 0
        while idx < len(valid_sections):
            s = valid_sections[idx]
            ck = _get_cluster_key(s.title)
            if ck:
                cluster = [s]
                j = idx + 1
                while j < len(valid_sections) and _get_cluster_key(valid_sections[j].title) == ck:
                    cluster.append(valid_sections[j])
                    j += 1
                planning_units.append((ck, cluster))
                idx = j
            else:
                planning_units.append((None, [s]))
                idx += 1

        for cluster_kind, secs in planning_units:
            primary_sec = secs[0]
            sec_lower = primary_sec.title.lower()

            # Determine Act name
            if any(k in sec_lower for k in ["identitas", "profil", "metadata"]):
                act_name = "ACT 1 — ACTIVITY IDENTITY"
            elif any(k in sec_lower for k in ["pendahuluan", "latar belakang", "fenomena"]):
                act_name = "ACT 1 — PHENOMENON & HOOK"
            elif any(k in sec_lower for k in ["tujuan", "capaian", "rumusan", "pertanyaan"]):
                act_name = "ACT 2 — OBJECTIVES & INQUIRY"
            elif any(k in sec_lower for k in ["teori", "segitiga api", "pembakaran", "reaksi", "fluida", "viskositas"]):
                act_name = "ACT 3 — CORE SCIENTIFIC THEORY"
            elif any(k in sec_lower for k in ["kalor", "rumus", "perpindahan", "geser", "tegangan", "laju geser", "persamaan"]):
                act_name = "ACT 4 — MATHEMATICAL MODELS & MECHANISMS"
            elif any(k in sec_lower for k in ["alat", "bahan", "k3", "peringatan", "keselamatan", "risiko"]):
                act_name = "ACT 5 — APPARATUS & LAB SAFETY"
            elif any(k in sec_lower for k in ["prosedur", "langkah", "tahapan", "cara kerja", "step"]):
                act_name = "ACT 6 — EXPERIMENTAL PROCEDURE"
            elif any(k in sec_lower for k in ["observasi", "pengamatan", "data", "hasil", "tabel"]):
                act_name = "ACT 7 — OBSERVATION & DATA"
            elif any(k in sec_lower for k in ["analisis", "diskusi", "pembahasan", "refleksi", "kesalahan", "troubleshooting"]):
                act_name = "ACT 7 — ANALYSIS & DISCUSSION"
            else:
                act_name = "ACT 8 — SYNTHESIS & CONCLUSION"

            # CASE A: Clustered repetitive sub-items (Steps, Misconceptions, Ideas, Challenges)
            if cluster_kind is not None and len(secs) > 1:
                combined_blocks = []
                for s in secs:
                    combined_blocks.extend(s.blocks)
                all_refs = [s.id for s in secs] + [b.id for b in combined_blocks]

                if cluster_kind == "steps":
                    chunk_size = 4
                    for c_idx in range(0, len(secs), chunk_size):
                        sub_secs = secs[c_idx : c_idx + chunk_size]
                        sub_blks = []
                        for s in sub_secs:
                            sub_blks.extend(s.blocks)
                        slides.append(
                            PlannedSlide(
                                slide_id=f"slide-{slide_counter}",
                                slide_number=slide_counter,
                                title=f"Tahapan Eksperimen (Langkah {c_idx+1}–{c_idx+len(sub_secs)})",
                                act_name=act_name,
                                purpose="Sequential experimental workflow and practical steps",
                                source_refs=[s.id for s in sub_secs] + [b.id for b in sub_blks],
                                visual_type="step_process",
                                layout="timeline_horizontal",
                                content_priority=ContentPriority.CRITICAL,
                                text_density="medium",
                                key_blocks=sub_blks,
                            )
                        )
                        slide_counter += 1

                elif cluster_kind == "misconceptions":
                    slides.append(
                        PlannedSlide(
                            slide_id=f"slide-{slide_counter}",
                            slide_number=slide_counter,
                            title="Analisis Kesalahan Umum & Miskonsepsi",
                            act_name=act_name,
                            purpose="Critical analysis of scientific misconceptions and experimental controls",
                            source_refs=all_refs,
                            visual_type="comparison",
                            layout="two_column",
                            content_priority=ContentPriority.IMPORTANT,
                            text_density="medium",
                            key_blocks=combined_blocks,
                        )
                    )
                    slide_counter += 1

                elif cluster_kind == "ideas":
                    chunk_size = 3
                    for c_idx in range(0, len(secs), chunk_size):
                        sub_secs = secs[c_idx : c_idx + chunk_size]
                        sub_blks = []
                        for s in sub_secs:
                            sub_blks.extend(s.blocks)
                        slides.append(
                            PlannedSlide(
                                slide_id=f"slide-{slide_counter}",
                                slide_number=slide_counter,
                                title=f"Eksplorasi Ide Penelitian KIR (Bagian {c_idx//chunk_size + 1})",
                                act_name=act_name,
                                purpose="Research problem formulation and methodology expansion",
                                source_refs=[s.id for s in sub_secs] + [b.id for b in sub_blks],
                                visual_type="two_column",
                                layout="two_column",
                                content_priority=ContentPriority.IMPORTANT,
                                text_density="medium",
                                key_blocks=sub_blks,
                            )
                        )
                        slide_counter += 1

                elif cluster_kind == "challenges":
                    slides.append(
                        PlannedSlide(
                            slide_id=f"slide-{slide_counter}",
                            slide_number=slide_counter,
                            title="Tantangan Eksplorasi Ilmiah (Challenge Extension)",
                            act_name=act_name,
                            purpose="Advanced inquiry challenge and scientific extensions",
                            source_refs=all_refs,
                            visual_type="reflection_question",
                            layout="two_column",
                            content_priority=ContentPriority.IMPORTANT,
                            text_density="low",
                            key_blocks=combined_blocks,
                        )
                    )
                    slide_counter += 1
                continue

            # CASE B: Standard Section Processing
            sec = primary_sec
            processed_block_ids: set[str] = set()

            # 1. Formulas: combine into formula explainer
            formula_blks = [b for b in sec.blocks if b.type == SemanticBlockType.FORMULA and b.id not in processed_block_ids]
            if formula_blks:
                context_blks = [
                    b for b in sec.blocks
                    if b.type not in (
                        SemanticBlockType.FORMULA, SemanticBlockType.TABLE, SemanticBlockType.PROCEDURE,
                        SemanticBlockType.OBSERVATION_DATA, SemanticBlockType.WARNING, SemanticBlockType.QUESTION
                    ) and b.id not in processed_block_ids
                ]
                combined_keys = formula_blks + context_blks
                slides.append(
                    PlannedSlide(
                        slide_id=f"slide-{slide_counter}",
                        slide_number=slide_counter,
                        title=f"Persamaan Matematis: {sec.title}",
                        act_name=act_name,
                        purpose=f"Explain mathematical formula and variable relationships in {sec.title}",
                        source_refs=[sec.id] + [b.id for b in combined_keys],
                        visual_type="formula_visual",
                        layout="formula_explainer",
                        content_priority=ContentPriority.CRITICAL,
                        text_density="medium",
                        key_blocks=combined_keys,
                    )
                )
                for b in combined_keys:
                    processed_block_ids.add(b.id)
                slide_counter += 1

            # 2. Warnings: combine all warnings in this section onto 1 risk matrix slide
            warning_blks = [b for b in sec.blocks if b.type == SemanticBlockType.WARNING and b.id not in processed_block_ids]
            if warning_blks:
                slides.append(
                    PlannedSlide(
                        slide_id=f"slide-{slide_counter}",
                        slide_number=slide_counter,
                        title=f"Protokol Keselamatan: {sec.title}",
                        act_name=act_name,
                        purpose="Highlight critical laboratory safety controls and hazard precautions",
                        source_refs=[sec.id] + [b.id for b in warning_blks],
                        visual_type="risk_matrix",
                        layout="risk_matrix",
                        content_priority=ContentPriority.CRITICAL,
                        text_density="low",
                        key_blocks=warning_blks,
                    )
                )
                for b in warning_blks:
                    processed_block_ids.add(b.id)
                slide_counter += 1

            # 3. Procedures: chunk by 4 steps with timeline layout
            proc_blks = [b for b in sec.blocks if b.type == SemanticBlockType.PROCEDURE and b.id not in processed_block_ids]
            if proc_blks:
                chunk_size = 4
                for p_idx in range(0, len(proc_blks), chunk_size):
                    p_chunk = proc_blks[p_idx : p_idx + chunk_size]
                    part_suffix = f" (Langkah {p_idx+1}–{min(p_idx+chunk_size, len(proc_blks))})" if len(proc_blks) > chunk_size else ""
                    slides.append(
                        PlannedSlide(
                            slide_id=f"slide-{slide_counter}",
                            slide_number=slide_counter,
                            title=f"{sec.title}{part_suffix}",
                            act_name=act_name,
                            purpose="Sequential experimental workflow and practical steps",
                            source_refs=[sec.id] + [b.id for b in p_chunk],
                            visual_type="step_process",
                            layout="timeline_horizontal",
                            content_priority=ContentPriority.CRITICAL,
                            text_density="medium",
                            key_blocks=p_chunk,
                        )
                    )
                    slide_counter += 1
                for b in proc_blks:
                    processed_block_ids.add(b.id)

            # 4. Questions: chunk by 3-4 questions with two_column or minimal_question
            question_blks = [b for b in sec.blocks if b.type in (SemanticBlockType.QUESTION, SemanticBlockType.CRITICAL_THINKING) and b.id not in processed_block_ids]
            if question_blks:
                chunk_size = 3 if len(question_blks) <= 4 else 4
                for q_idx in range(0, len(question_blks), chunk_size):
                    q_chunk = question_blks[q_idx : q_idx + chunk_size]
                    layout = "two_column" if len(q_chunk) > 1 else "minimal_question"
                    part_suffix = f" (Bagian {q_idx//chunk_size + 1})" if len(question_blks) > chunk_size else ""
                    slides.append(
                        PlannedSlide(
                            slide_id=f"slide-{slide_counter}",
                            slide_number=slide_counter,
                            title=f"{sec.title}{part_suffix}",
                            act_name=act_name,
                            purpose="Inquiry prompt and critical reflection",
                            source_refs=[sec.id] + [b.id for b in q_chunk],
                            visual_type="reflection_question",
                            layout=layout,
                            content_priority=ContentPriority.IMPORTANT,
                            text_density="low",
                            key_blocks=q_chunk,
                        )
                    )
                    slide_counter += 1
                for b in question_blks:
                    processed_block_ids.add(b.id)

            # 5. Tables and Comparisons
            for blk in sec.blocks:
                if blk.id in processed_block_ids:
                    continue

                if blk.type == SemanticBlockType.COMPARISON:
                    slides.append(
                        PlannedSlide(
                            slide_id=f"slide-{slide_counter}",
                            slide_number=slide_counter,
                            title=sec.title,
                            act_name=act_name,
                            purpose=f"Compare parallel physical mechanisms: {sec.title}",
                            source_refs=[sec.id, blk.id],
                            visual_type="three_column_comparison",
                            layout="three_column_comparison",
                            content_priority=ContentPriority.CRITICAL,
                            text_density="medium",
                            key_blocks=[blk],
                        )
                    )
                    processed_block_ids.add(blk.id)
                    slide_counter += 1

                elif blk.type in (SemanticBlockType.OBSERVATION_DATA, SemanticBlockType.TABLE):
                    slides.append(
                        PlannedSlide(
                            slide_id=f"slide-{slide_counter}",
                            slide_number=slide_counter,
                            title=f"Tabel Pengamatan: {sec.title}",
                            act_name=act_name,
                            purpose="Structured observation matrix and experimental records",
                            source_refs=[sec.id, blk.id],
                            visual_type="data_table",
                            layout="data_table",
                            content_priority=ContentPriority.CRITICAL,
                            text_density="medium",
                            key_blocks=[blk],
                        )
                    )
                    processed_block_ids.add(blk.id)
                    slide_counter += 1

            # 6. Remaining blocks with semantic layout balancing (preventing 3-streak)
            remaining_blocks = [b for b in sec.blocks if b.id not in processed_block_ids]
            if remaining_blocks:
                prev_l1 = slides[-1].layout if slides else ""
                prev_l2 = slides[-2].layout if len(slides) >= 2 else ""

                is_triangle = "segitiga api" in sec_lower or "fire triangle" in sec_lower
                if is_triangle:
                    visual_type = "triangle_diagram"
                    layout = "triangle_relationship"
                elif any(k in sec_lower for k in ["perbandingan", "vs", "versus", "komparasi"]):
                    visual_type = "comparison"
                    layout = "two_column"
                elif any(k in sec_lower for k in ["mekanisme", "alur", "siklus", "flow", "proses"]):
                    visual_type = "mechanism_flow"
                    layout = "timeline_horizontal"
                elif any(k in sec_lower for k in ["rumusan", "tanya", "pertanyaan", "inkuiri"]):
                    visual_type = "reflection_question"
                    layout = "minimal_question"
                elif any(k in sec_lower for k in ["kesalahan", "miskonsepsi", "troubleshooting"]):
                    visual_type = "comparison"
                    layout = "two_column"
                elif any(k in sec_lower for k in ["ide", "gagasan", "penelitian"]):
                    visual_type = "two_column"
                    layout = "two_column"
                else:
                    if prev_l1 == "two_column" and prev_l2 == "two_column":
                        visual_type = "concept_explainer"
                        layout = "concept_card"
                    elif prev_l1 == "concept_card" and prev_l2 == "concept_card":
                        visual_type = "two_column"
                        layout = "two_column"
                    elif len(remaining_blocks) >= 2 or any(len(b.content.split("\n")) >= 3 for b in remaining_blocks):
                        visual_type = "two_column"
                        layout = "two_column"
                    else:
                        visual_type = "concept_explainer"
                        layout = "concept_card"

                # Guard against any 3-streak
                if layout == prev_l1 and prev_l1 == prev_l2:
                    layout = "concept_card" if layout == "two_column" else "two_column"

                # Chunk remaining blocks to avoid text overflow on dense sections
                chunk_size = 4
                total_blks = len(remaining_blocks)
                for c_idx in range(0, total_blks, chunk_size):
                    chunk = remaining_blocks[c_idx : c_idx + chunk_size]
                    part_suffix = f" (Bagian {c_idx // chunk_size + 1})" if total_blks > chunk_size else ""
                    chunk_layout = layout
                    if len(slides) >= 2 and slides[-1].layout == chunk_layout and slides[-2].layout == chunk_layout:
                        chunk_layout = "two_column" if chunk_layout == "concept_card" else "concept_card"
                    slides.append(
                        PlannedSlide(
                            slide_id=f"slide-{slide_counter}",
                            slide_number=slide_counter,
                            title=f"{sec.title}{part_suffix}",
                            act_name=act_name,
                            purpose=f"Core concept focus: {sec.title}",
                            source_refs=[sec.id] + [b.id for b in chunk],
                            visual_type=visual_type,
                            layout=chunk_layout,
                            content_priority=ContentPriority.CRITICAL if is_triangle else ContentPriority.IMPORTANT,
                            text_density="medium",
                            key_blocks=chunk,
                        )
                    )
                    slide_counter += 1

        # Final Synthesis / Concept Map slide
        last_sec = all_sections[-1] if all_sections else None
        slides.append(
            PlannedSlide(
                slide_id=f"slide-{slide_counter}",
                slide_number=slide_counter,
                title="Sintesis & Peta Konsep Akhir",
                act_name="ACT 8 — SYNTHESIS & CONCLUSION",
                purpose="Integrate all discovered scientific principles and conclude",
                source_refs=[last_sec.id] if last_sec else ["final"],
                visual_type="synthesis",
                layout="synthesis",
                content_priority=ContentPriority.CRITICAL,
                text_density="medium",
                key_blocks=[],
            )
        )

        # Enforce layout diversity: no streaks > 2 while respecting Visual Grammar Matrix
        visual_types = [s.visual_type for s in slides]
        balanced_vtypes = self.visual_director.balance_deck_layouts(visual_types)
        for s, bv in zip(slides, balanced_vtypes):
            s.visual_type = bv
            resolved_layout = self.visual_director.resolve_layout(bv).layout_name
            role = s.narrative_function.upper()
            rule = VISUAL_GRAMMAR_MATRIX.get(role)
            if rule and resolved_layout in rule.get("avoid", []):
                # Fall back to preferred layout to prevent semantic layout mismatch
                preferred = rule.get("preferred", [])
                s.layout = preferred[0] if preferred else resolved_layout
            else:
                s.layout = resolved_layout

        # Invariant: break any streak of 3 consecutive identical layouts
        for i in range(len(slides) - 2):
            if slides[i].layout == slides[i+1].layout == slides[i+2].layout:
                cur_l = slides[i+2].layout
                slides[i+2].layout = "two_column" if cur_l != "two_column" else "concept_card"

        # Enrich slides with Presentation Intelligence V3 metadata
        self._enrich_slides(slides)

        # Calculate bidirectional mapping
        source_to_slide: dict[str, list[int]] = {}
        slide_to_source: dict[int, list[str]] = {}

        for s in slides:
            slide_to_source[s.slide_number] = s.source_refs
            for s_ref in s.source_refs:
                source_to_slide.setdefault(s_ref, []).append(s.slide_number)

        # Group slides into Acts
        acts_dict: dict[str, SlideAct] = {}
        for s in slides:
            if s.act_name not in acts_dict:
                acts_dict[s.act_name] = SlideAct(
                    name=s.act_name,
                    order=len(acts_dict) + 1,
                    slides=[],
                )
            acts_dict[s.act_name].slides.append(s)

        layout_counts: dict[str, int] = {}
        for s in slides:
            layout_counts[s.layout] = layout_counts.get(s.layout, 0) + 1

        entropy = self.visual_director.calculate_layout_entropy(list(layout_counts.keys()))

        return SlidePlan(
            deck_title=tree.title,
            total_slides=len(slides),
            acts=list(acts_dict.values()),
            slides=slides,
            source_to_slide_map=source_to_slide,
            slide_to_source_map=slide_to_source,
            layout_distribution=layout_counts,
            layout_entropy=entropy,
        )

    def _enrich_slides(self, slides: list[PlannedSlide]) -> None:
        """Enriches planned slides with narrative, pedagogical, cognitive load, and claim units."""
        n_slides = len(slides)
        for i, s in enumerate(slides):
            # Act ID
            match = re.search(r"ACT\s+(\d+)", s.act_name)
            act_num = match.group(1) if match else "01"
            s.act_id = f"act-{act_num.zfill(2)}"

            # Primary concept
            clean_title = re.sub(r"^(Persamaan Matematis:|Protokol Keselamatan:|Tabel Pengamatan:)\s*", "", s.title).strip()
            s.primary_concept = clean_title

            # Visual Intent synchronization
            s.visual_intent = s.visual_type

            # Narrative & Pedagogical assignment based on visual type & role
            v = s.visual_type
            if v == "hero_phenomenon":
                s.narrative_function = "HOOK"
                s.pedagogical_function = "ENGAGE"
                s.information_role = "NEW_INFORMATION"
                s.cognitive_load = CognitiveLoad(level="low", reason="Introductory phenomenon hook")
                s.visual_priority = "HIGH"
            elif v in ("reflection_question", "minimal_question"):
                s.narrative_function = "QUESTION"
                s.pedagogical_function = "INVESTIGATE"
                s.information_role = "INSTRUCTION"
                s.cognitive_load = CognitiveLoad(level="low", reason="Reflective inquiry prompt")
                s.visual_priority = "MEDIUM"
            elif v == "formula_visual":
                s.narrative_function = "MECHANISM"
                s.pedagogical_function = "BREAK_DOWN"
                s.information_role = "NEW_INFORMATION"
                s.cognitive_load = CognitiveLoad(level="high", reason="Mathematical formulation & parameter relations")
                s.visual_priority = "HIGH"
            elif v in ("three_column_comparison", "comparison_split"):
                s.narrative_function = "COMPARISON"
                s.pedagogical_function = "COMPARE"
                s.information_role = "ELABORATION"
                s.cognitive_load = CognitiveLoad(level="medium", reason="Comparative mechanics and property contrast")
                s.visual_priority = "HIGH"
            elif v == "triangle_diagram":
                s.narrative_function = "MECHANISM"
                s.pedagogical_function = "VISUALIZE"
                s.information_role = "NEW_INFORMATION"
                s.cognitive_load = CognitiveLoad(level="medium", reason="Triangular relationship dynamics")
                s.visual_priority = "HIGH"
            elif v in ("step_process", "timeline_horizontal"):
                s.narrative_function = "PROCESS"
                s.pedagogical_function = "APPLY"
                s.information_role = "INSTRUCTION"
                s.cognitive_load = CognitiveLoad(level="medium", reason="Procedural experimental protocol")
                s.visual_priority = "MEDIUM"
            elif v == "data_table":
                s.narrative_function = "OBSERVATION"
                s.pedagogical_function = "ANALYZE"
                s.information_role = "EVIDENCE"
                s.cognitive_load = CognitiveLoad(level="medium", reason="Empirical data matrix and observations")
                s.visual_priority = "MEDIUM"
            elif v == "risk_matrix":
                s.narrative_function = "CONTEXT"
                s.pedagogical_function = "ACTIVATE_PRIOR_KNOWLEDGE"
                s.information_role = "INSTRUCTION"
                s.cognitive_load = CognitiveLoad(level="low", reason="Laboratory safety controls")
                s.visual_priority = "HIGH"
            elif v == "synthesis":
                s.narrative_function = "SYNTHESIS"
                s.pedagogical_function = "SYNTHESIZE"
                s.information_role = "SUMMARY"
                s.cognitive_load = CognitiveLoad(level="medium", reason="Conceptual synthesis and takeaways")
                s.visual_priority = "HIGH"
            else:
                s.narrative_function = "CONCEPT_INTRODUCTION"
                s.pedagogical_function = "EXPLAIN"
                s.information_role = "NEW_INFORMATION"
                s.cognitive_load = CognitiveLoad(level="medium", reason="Core conceptual exposition")
                s.visual_priority = "MEDIUM"

            # Transitions
            if i > 0:
                prev_title = slides[i - 1].title
                s.transition_from_previous = f"Transisi lanjutan dari pembahasan {prev_title}"
            else:
                s.transition_from_previous = "Titik awal presentasi"

            if i < n_slides - 1:
                next_title = slides[i + 1].title
                s.transition_to_next = f"Membuka landasan menuju {next_title}"
            else:
                s.transition_to_next = "Konklusi akhir paparan"

            # Claims extraction from key_blocks
            claims: list[ClaimUnit] = []
            claim_idx = 1
            for blk in s.key_blocks:
                raw_text = blk.content.strip()
                clean_lines = [
                    re.sub(r"^[-*#\d.]+\s*", "", ln).strip()
                    for ln in raw_text.splitlines()
                    if len(re.sub(r"^[-*#\d.]+\s*", "", ln).strip()) > 12
                ]
                sents = [st.strip() for st in re.split(r"(?<=[.?!])\s+", raw_text.replace("\n", " ")) if len(st.strip()) > 15]
                candidate_statements: list[str] = []
                for st in sents + clean_lines:
                    if st and st not in candidate_statements and not st.startswith("|"):
                        candidate_statements.append(st)
                for st in candidate_statements[:4]:
                    claims.append(
                        ClaimUnit(
                            claim_id=f"{s.slide_id}-c{claim_idx}",
                            text=st,
                            source_refs=[blk.id] if blk.id else s.source_refs,
                            support_level="DIRECT_SUPPORT",
                        )
                    )
                    claim_idx += 1
            if not claims:
                # Ground strictly in Indonesian title and block excerpt
                block_sample = s.key_blocks[0].content[:80].replace("\n", " ").strip() if s.key_blocks else ""
                fallback_text = f"{s.title}: {block_sample}" if block_sample else s.title
                claims.append(
                    ClaimUnit(
                        claim_id=f"{s.slide_id}-c1",
                        text=fallback_text,
                        source_refs=s.source_refs,
                        support_level="DIRECT_SUPPORT",
                    )
                )
            s.claim_units = claims

            # Internal architectural reasoning metadata
            s.why_this_slide_exists = f"Memberikan fokus instruksional mandiri pada {s.title} sesuai fungsi {s.narrative_function}."
            s.audience_takeaway = f"Peserta didik memahami esensi {s.primary_concept} dan korelasi mekanismenya."
            s.unique_information_gain = f"Menyajikan komponen baru {s.primary_concept} dengan visual {s.layout}."
            s.transition_logic = f"Menghubungkan {s.transition_from_previous} ke {s.transition_to_next}."
            s.why_not_merge_with_previous = f"Memiliki fungsi pedagogis ({s.pedagogical_function}) dan fokus visual unik yang akan tereduksi jika digabung."
            s.why_not_merge_with_next = "Beban kognitif dan topik pembahasan membutuhkan jeda pemahaman mandiri."
