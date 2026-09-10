"""
Content Manifest & Slide Count Estimator.

Builds an authoritative manifest of document concepts, prioritizes them into
CRITICAL, IMPORTANT, and SUPPORTING tiers, and computes target slide counts.
"""

from __future__ import annotations

import math
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field

from app.intelligence.markdown_tree_parser import (
    ContentBlock,
    ContentSection,
    ContentTree,
    SemanticBlockType,
)


class ContentPriority(str, Enum):
    CRITICAL = "critical"      # Must appear explicitly; failure to include fails gate
    IMPORTANT = "important"    # Must appear unless logically merged into an act
    SUPPORTING = "supporting"  # Contextual; may be compressed or combined


class ManifestConcept(BaseModel):
    id: str
    name: str
    category: str  # "theory", "formula", "mechanism", "procedure", "data", "safety", "discussion"
    priority: ContentPriority
    source_section_id: str
    source_block_ids: list[str] = Field(default_factory=list)
    suggested_visual: str = "concept_explainer"
    summary: str = ""


class ContentManifest(BaseModel):
    """Authoritative semantic manifest of the document's content."""
    document_title: str
    total_sections: int
    total_blocks: int

    # Extracted Concept Items
    critical_concepts: list[ManifestConcept] = Field(default_factory=list)
    important_concepts: list[ManifestConcept] = Field(default_factory=list)
    supporting_concepts: list[ManifestConcept] = Field(default_factory=list)

    # Specific Block Groups
    formulas: list[ContentBlock] = Field(default_factory=list)
    comparisons: list[ContentBlock] = Field(default_factory=list)
    procedures: list[ContentBlock] = Field(default_factory=list)
    tables: list[ContentBlock] = Field(default_factory=list)
    warnings: list[ContentBlock] = Field(default_factory=list)
    questions: list[ContentBlock] = Field(default_factory=list)
    diagrams: list[ContentBlock] = Field(default_factory=list)

    # Slide Count Bounds
    min_slides: int
    target_slides: int
    max_slides: int

    def get_all_concepts(self) -> list[ManifestConcept]:
        return self.critical_concepts + self.important_concepts + self.supporting_concepts

    def get_concept(self, concept_id: str) -> ManifestConcept | None:
        for c in self.get_all_concepts():
            if c.id == concept_id:
                return c
        return None


class ContentManifestBuilder:
    """Constructs ContentManifest from ContentTree using domain heuristics."""

    def build(self, tree: ContentTree) -> ContentManifest:
        critical: list[ManifestConcept] = []
        important: list[ManifestConcept] = []
        supporting: list[ManifestConcept] = []

        formulas: list[ContentBlock] = []
        comparisons: list[ContentBlock] = []
        procedures: list[ContentBlock] = []
        tables: list[ContentBlock] = []
        warnings: list[ContentBlock] = []
        questions: list[ContentBlock] = []
        diagrams: list[ContentBlock] = []

        all_sections = tree.all_sections_flat()

        for sec in all_sections:
            sec_lower = sec.title.lower()

            # Identify section-level category
            is_intro = any(k in sec_lower for k in ["pendahuluan", "latar belakang", "intro"])
            is_identity = any(k in sec_lower for k in ["identitas", "profil", "metadata"])
            is_objectives = any(k in sec_lower for k in ["tujuan", "objective", "capaian", "rumusan"])
            is_theory = any(k in sec_lower for k in ["teori", "konsep", "segitiga api", "pembakaran", "kalor", "reaksi", "energi"])
            is_proc = any(k in sec_lower for k in ["prosedur", "langkah", "tahapan", "alat", "bahan", "cara kerja"])
            is_obs = any(k in sec_lower for k in ["observasi", "pengamatan", "data", "hasil", "lembar"])
            is_analysis = any(k in sec_lower for k in ["analisis", "pembahasan", "diskusi", "pertanyaan"])
            is_safety = any(k in sec_lower for k in ["peringatan", "keselamatan", "k3", "safety", "risiko", "bahaya"])
            is_conclusion = any(k in sec_lower for k in ["kesimpulan", "sintesis", "peta konsep", "summary"])

            for blk in sec.blocks:
                # Accumulate specific blocks
                if blk.type == SemanticBlockType.FORMULA:
                    formulas.append(blk)
                elif blk.type == SemanticBlockType.COMPARISON:
                    comparisons.append(blk)
                elif blk.type == SemanticBlockType.PROCEDURE:
                    procedures.append(blk)
                elif blk.type in (SemanticBlockType.TABLE, SemanticBlockType.OBSERVATION_DATA, SemanticBlockType.RISK_MATRIX):
                    tables.append(blk)
                elif blk.type == SemanticBlockType.WARNING or blk.metadata.get("is_warning"):
                    warnings.append(blk)
                elif blk.type in (SemanticBlockType.QUESTION, SemanticBlockType.CRITICAL_THINKING):
                    questions.append(blk)
                elif blk.type in (SemanticBlockType.DIAGRAM, SemanticBlockType.ASCII_DIAGRAM):
                    diagrams.append(blk)

                # Prioritize blocks into ManifestConcepts
                concept_id = f"c-{blk.id}"
                summary = blk.content[:100].replace("\n", " ")

                if blk.type == SemanticBlockType.FORMULA:
                    critical.append(ManifestConcept(
                        id=concept_id,
                        name=f"Formula: {blk.content.splitlines()[0][:30]}",
                        category="formula",
                        priority=ContentPriority.CRITICAL,
                        source_section_id=sec.id,
                        source_block_ids=[blk.id],
                        suggested_visual="formula_visual",
                        summary=summary,
                    ))
                elif blk.type == SemanticBlockType.WARNING:
                    critical.append(ManifestConcept(
                        id=concept_id,
                        name=f"Safety: {sec.title}",
                        category="safety",
                        priority=ContentPriority.CRITICAL,
                        source_section_id=sec.id,
                        source_block_ids=[blk.id],
                        suggested_visual="risk_matrix",
                        summary=summary,
                    ))
                elif blk.type == SemanticBlockType.COMPARISON:
                    critical.append(ManifestConcept(
                        id=concept_id,
                        name=f"Comparison: {sec.title}",
                        category="mechanism",
                        priority=ContentPriority.CRITICAL,
                        source_section_id=sec.id,
                        source_block_ids=[blk.id],
                        suggested_visual="three_column_comparison",
                        summary=summary,
                    ))
                elif blk.type == SemanticBlockType.PROCEDURE:
                    critical.append(ManifestConcept(
                        id=concept_id,
                        name=f"Procedure: {sec.title}",
                        category="procedure",
                        priority=ContentPriority.CRITICAL,
                        source_section_id=sec.id,
                        source_block_ids=[blk.id],
                        suggested_visual="step_process",
                        summary=summary,
                    ))
                elif blk.type == SemanticBlockType.OBSERVATION_DATA:
                    critical.append(ManifestConcept(
                        id=concept_id,
                        name=f"Observation Data: {sec.title}",
                        category="data",
                        priority=ContentPriority.CRITICAL,
                        source_section_id=sec.id,
                        source_block_ids=[blk.id],
                        suggested_visual="data_table",
                        summary=summary,
                    ))
                elif blk.type in (SemanticBlockType.DIAGRAM, SemanticBlockType.ASCII_DIAGRAM):
                    critical.append(ManifestConcept(
                        id=concept_id,
                        name=f"Diagram: {sec.title}",
                        category="theory",
                        priority=ContentPriority.CRITICAL,
                        source_section_id=sec.id,
                        source_block_ids=[blk.id],
                        suggested_visual="diagram_visual",
                        summary=summary,
                    ))
                elif is_theory:
                    # Core theory concept
                    priority = ContentPriority.CRITICAL if blk.type in (SemanticBlockType.DEFINITION, SemanticBlockType.NUMBERED_LIST) else ContentPriority.IMPORTANT
                    target_list = critical if priority == ContentPriority.CRITICAL else important
                    target_list.append(ManifestConcept(
                        id=concept_id,
                        name=f"Concept: {sec.title}",
                        category="theory",
                        priority=priority,
                        source_section_id=sec.id,
                        source_block_ids=[blk.id],
                        suggested_visual="concept_explainer",
                        summary=summary,
                    ))
                elif is_objectives or is_analysis or is_conclusion:
                    important.append(ManifestConcept(
                        id=concept_id,
                        name=f"Analysis: {sec.title}",
                        category="discussion" if is_analysis else ("conclusion" if is_conclusion else "objectives"),
                        priority=ContentPriority.IMPORTANT,
                        source_section_id=sec.id,
                        source_block_ids=[blk.id],
                        suggested_visual="reflection_question" if blk.type in (SemanticBlockType.QUESTION, SemanticBlockType.CRITICAL_THINKING) else "synthesis",
                        summary=summary,
                    ))
                elif is_identity or is_intro:
                    supporting.append(ManifestConcept(
                        id=concept_id,
                        name=f"Overview: {sec.title}",
                        category="intro",
                        priority=ContentPriority.SUPPORTING,
                        source_section_id=sec.id,
                        source_block_ids=[blk.id],
                        suggested_visual="hero_phenomenon" if is_intro else "concept_explainer",
                        summary=summary,
                    ))
                else:
                    important.append(ManifestConcept(
                        id=concept_id,
                        name=f"Topic: {sec.title}",
                        category="general",
                        priority=ContentPriority.IMPORTANT,
                        source_section_id=sec.id,
                        source_block_ids=[blk.id],
                        suggested_visual="concept_explainer",
                        summary=summary,
                    ))

        # Slide Count Heuristics (Phase 6):
        # 1 major concept = 1-2 slides
        # 1 complex diagram = 1 slide
        # 1 comparison = 1 slide
        # 1 formula = 1 slide
        # 1 process / procedure = 1-3 slides
        # 1 large table = 1 slide
        # 1 critical reflection/question = 1 slide
        n_crit_theory = sum(1 for c in critical if c.category == "theory")
        n_formulas = len(formulas)
        n_comparisons = len(comparisons)
        n_procedures = len(procedures)
        n_tables = len(tables)
        n_diagrams = len(diagrams)
        n_warnings = len(warnings)
        n_questions = len(questions)
        n_important = len(important)

        # Slide Count Bounds based on section density without double-counting
        sec_count = len(all_sections)
        # Structural minimum: at least ~75% of sections mapped to dedicated slides + intro/conclusion, capped by small inputs
        min_slides = min(sec_count + 2, max(3, math.ceil(sec_count * 0.75)))
        target_slides = max(min_slides + 1, math.ceil(sec_count * 1.10))
        max_slides = max(target_slides + 2, math.ceil(sec_count * 1.50))

        return ContentManifest(
            document_title=tree.title,
            total_sections=len(all_sections),
            total_blocks=len(tree.all_blocks_flat()),
            critical_concepts=critical,
            important_concepts=important,
            supporting_concepts=supporting,
            formulas=formulas,
            comparisons=comparisons,
            procedures=procedures,
            tables=tables,
            warnings=warnings,
            questions=questions,
            diagrams=diagrams,
            min_slides=min_slides,
            target_slides=target_slides,
            max_slides=max_slides,
        )
