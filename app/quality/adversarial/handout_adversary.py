"""
Universal Document Intelligence System V5 — Handout Adversary.

Phase 2C: Generates deterministic bad Handout documents across:
- Category A: Document Structure (orphan heading, empty section, hierarchy inversion, etc.)
- Category B: Page Composition (extreme density, accidental empty page, whitespace imbalance)
- Category C: Reading Flow (paragraph fragmentation, abrupt transition, duplicate block)
- Category D: Typography (tiny body text, weak hierarchy, excessive line length)
- Category E: Content Structure (critical concept buried, excessive bullet nesting, merged concepts)
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from app.integration.renderer_adapters.contracts import (
    DocumentContent,
    DocumentContentSection,
    DocumentOutline,
    DocumentOutlineItem,
)
from app.quality.adversarial.base import BaseArtifactAdversary
from app.quality.adversarial.mutation_contract import ArtifactMutation
from app.quality.calibration.failure_taxonomy import FailureCategory, FailureSeverity


class HandoutAdversary(BaseArtifactAdversary):
    """Adversarial mutation engine for continuous reading handouts."""

    @property
    def supported_artifact_type(self) -> str:
        return "HANDOUT"

    def list_mutations(self) -> List[ArtifactMutation]:
        return [
            # CATEGORY A — DOCUMENT STRUCTURE
            ArtifactMutation.create(
                mutation_id="handout_orphan_heading_at_bottom",
                artifact_type="HANDOUT",
                failure_category=FailureCategory.STRUCTURAL_FAILURE,
                target_element_ids=["section_orphan"],
                mutation_description="Heading positioned at the very bottom of a page with content split onto the next.",
                expected_quality_signal="orphan_heading",
                expected_severity=FailureSeverity.WARNING,
            ),
            ArtifactMutation.create(
                mutation_id="handout_empty_heading_section",
                artifact_type="HANDOUT",
                failure_category=FailureCategory.STRUCTURAL_FAILURE,
                target_element_ids=["section_empty"],
                mutation_description="Heading section contains no body prose, definitions, or examples.",
                expected_quality_signal="empty_section",
                expected_severity=FailureSeverity.ERROR,
            ),
            ArtifactMutation.create(
                mutation_id="handout_heading_hierarchy_inversion",
                artifact_type="HANDOUT",
                failure_category=FailureCategory.STRUCTURAL_FAILURE,
                target_element_ids=["section_inverted"],
                mutation_description="Level 3 subsection appears directly under Level 1 document title without Level 2 parent.",
                expected_quality_signal="hierarchy_inversion",
                expected_severity=FailureSeverity.WARNING,
            ),
            ArtifactMutation.create(
                mutation_id="handout_definition_separated_from_concept",
                artifact_type="HANDOUT",
                failure_category=FailureCategory.FLOW_FAILURE,
                target_element_ids=["section_def_separated"],
                mutation_description="Formal definition placed 3 sections after concept is first utilized.",
                expected_quality_signal="definition_concept_coupling",
                expected_severity=FailureSeverity.WARNING,
            ),
            ArtifactMutation.create(
                mutation_id="handout_example_before_concept",
                artifact_type="HANDOUT",
                failure_category=FailureCategory.PEDAGOGICAL_FAILURE,
                target_element_ids=["section_example_early"],
                mutation_description="Concrete example given before any underlying theoretical definition.",
                expected_quality_signal="pedagogical_ordering",
                expected_severity=FailureSeverity.WARNING,
            ),
            # CATEGORY B — PAGE COMPOSITION
            ArtifactMutation.create(
                mutation_id="handout_extreme_dense_page",
                artifact_type="HANDOUT",
                failure_category=FailureCategory.DENSITY_FAILURE,
                target_element_ids=["section_dense"],
                mutation_description="Section text contains 4500 characters causing severe typographical clutter on A4.",
                expected_quality_signal="page_character_density",
                expected_severity=FailureSeverity.ERROR,
            ),
            ArtifactMutation.create(
                mutation_id="handout_almost_empty_accidental_page",
                artifact_type="HANDOUT",
                failure_category=FailureCategory.COMPOSITION_FAILURE,
                target_element_ids=["section_spill"],
                mutation_description="A section has only 2 words pushed to an accidental solitary page.",
                expected_quality_signal="accidental_empty_page",
                expected_severity=FailureSeverity.WARNING,
            ),
            ArtifactMutation.create(
                mutation_id="handout_severe_whitespace_imbalance",
                artifact_type="HANDOUT",
                failure_category=FailureCategory.COMPOSITION_FAILURE,
                target_element_ids=["section_whitespace"],
                mutation_description="85% empty whitespace on a substantive page with negligible prose.",
                expected_quality_signal="page_whitespace_balance",
                expected_severity=FailureSeverity.WARNING,
            ),
            ArtifactMutation.create(
                mutation_id="handout_repeated_page_composition",
                artifact_type="HANDOUT",
                failure_category=FailureCategory.REPETITION_FAILURE,
                target_element_ids=["all_sections"],
                mutation_description="Every section uses identical paragraph length and formatting without variation.",
                expected_quality_signal="composition_diversity",
                expected_severity=FailureSeverity.INFO,
            ),
            # CATEGORY C — READING FLOW
            ArtifactMutation.create(
                mutation_id="handout_paragraph_fragmentation",
                artifact_type="HANDOUT",
                failure_category=FailureCategory.FLOW_FAILURE,
                target_element_ids=["section_frag"],
                mutation_description="Content split into 15 single-sentence micro-paragraphs destroying reading continuity.",
                expected_quality_signal="paragraph_fragmentation",
                expected_severity=FailureSeverity.WARNING,
            ),
            ArtifactMutation.create(
                mutation_id="handout_abrupt_section_transition",
                artifact_type="HANDOUT",
                failure_category=FailureCategory.FLOW_FAILURE,
                target_element_ids=["section_transition"],
                mutation_description="Section transitions abruptly without connective topic sentence or summary.",
                expected_quality_signal="reading_flow",
                expected_severity=FailureSeverity.WARNING,
            ),
            ArtifactMutation.create(
                mutation_id="handout_duplicate_explanatory_block",
                artifact_type="HANDOUT",
                failure_category=FailureCategory.REPETITION_FAILURE,
                target_element_ids=["section_dup"],
                mutation_description="Identical 120-word explanatory definition repeated verbatim across sections.",
                expected_quality_signal="text_duplication",
                expected_severity=FailureSeverity.CRITICAL,
            ),
            # CATEGORY D — TYPOGRAPHY
            ArtifactMutation.create(
                mutation_id="handout_tiny_body_text",
                artifact_type="HANDOUT",
                failure_category=FailureCategory.READABILITY_FAILURE,
                target_element_ids=["section_tiny"],
                mutation_description="Body text rendered at 6.0pt below readable threshold for print handouts.",
                expected_quality_signal="body_font_size",
                expected_severity=FailureSeverity.CRITICAL,
            ),
            ArtifactMutation.create(
                mutation_id="handout_weak_heading_hierarchy",
                artifact_type="HANDOUT",
                failure_category=FailureCategory.READABILITY_FAILURE,
                target_element_ids=["section_weak_heading"],
                mutation_description="Headings rendered at same font size and weight as body text (ratio 1.0).",
                expected_quality_signal="heading_hierarchy_contrast",
                expected_severity=FailureSeverity.WARNING,
            ),
            ArtifactMutation.create(
                mutation_id="handout_excessive_line_length",
                artifact_type="HANDOUT",
                failure_category=FailureCategory.READABILITY_FAILURE,
                target_element_ids=["section_wide"],
                mutation_description="Text rendered with line width exceeding 150 characters without margins.",
                expected_quality_signal="typographic_line_length",
                expected_severity=FailureSeverity.WARNING,
            ),
            # CATEGORY E — CONTENT STRUCTURE
            ArtifactMutation.create(
                mutation_id="handout_critical_concept_buried",
                artifact_type="HANDOUT",
                failure_category=FailureCategory.COMPOSITION_FAILURE,
                target_element_ids=["section_buried"],
                mutation_description="Core definition buried in middle of 900-word unbroken wall of text.",
                expected_quality_signal="concept_discoverability",
                expected_severity=FailureSeverity.WARNING,
            ),
            ArtifactMutation.create(
                mutation_id="handout_excessive_bullet_nesting",
                artifact_type="HANDOUT",
                failure_category=FailureCategory.STRUCTURAL_FAILURE,
                target_element_ids=["section_bullets"],
                mutation_description="5 levels of nested bullet lists causing cognitive strain.",
                expected_quality_signal="bullet_nesting_depth",
                expected_severity=FailureSeverity.WARNING,
            ),
            ArtifactMutation.create(
                mutation_id="handout_multiple_unrelated_concepts_merged",
                artifact_type="HANDOUT",
                failure_category=FailureCategory.STRUCTURAL_FAILURE,
                target_element_ids=["section_merged"],
                mutation_description="Four distinct theoretical concepts crammed into a single undivided section.",
                expected_quality_signal="conceptual_coherence",
                expected_severity=FailureSeverity.WARNING,
            ),
        ]

    def apply_mutation(
        self, doc: DocumentContent, mutation_id: str
    ) -> Tuple[DocumentContent, ArtifactMutation]:
        mutations_map = {m.mutation_id: m for m in self.list_mutations()}
        if mutation_id not in mutations_map:
            raise ValueError(f"Unknown mutation_id '{mutation_id}' for HandoutAdversary")

        mutation = mutations_map[mutation_id]
        sections = list(doc.sections)

        if not sections:
            return doc, mutation

        if mutation_id == "handout_orphan_heading_at_bottom":
            meta = dict(sections[0].metadata)
            meta["orphan_heading"] = True
            meta["page_position"] = "bottom_margin_overlap"
            sections[0] = sections[0].model_copy(update={"metadata": meta})

        elif mutation_id == "handout_empty_heading_section":
            empty_sec = DocumentContentSection(
                section_id="sec_empty_mutated",
                title="Bagian Kosong Tanpa Penjelasan",
                level=2,
                sequence_index=len(sections) + 1,
                content="",
                definitions=tuple(),
                examples=tuple(),
            )
            sections.append(empty_sec)

        elif mutation_id == "handout_heading_hierarchy_inversion":
            inverted = DocumentContentSection(
                section_id="sec_inverted_mutated",
                title="Sub-sub Bagian Terbalik",
                level=3,  # Inversion: Level 3 immediately following Level 1
                sequence_index=2,
                content="Konten sub-sub bagian yang melompati level 2.",
            )
            sections.insert(1, inverted)

        elif mutation_id == "handout_definition_separated_from_concept":
            meta = dict(sections[0].metadata)
            meta["definition_distance_sections"] = 4
            sections[0] = sections[0].model_copy(
                update={
                    "definitions": tuple(),
                    "metadata": meta,
                }
            )

        elif mutation_id == "handout_example_before_concept":
            if len(sections) >= 2:
                # Put example in section 0, concept explanation in section 1
                s0 = sections[0].model_copy(update={"content": "Contoh kasus penerapan:", "examples": ("Contoh bola memantul",)})
                s1 = sections[1].model_copy(update={"content": "Definisi konsep dasar fluida:"})
                sections[0] = s0
                sections[1] = s1

        elif mutation_id == "handout_extreme_dense_page":
            dense_content = "Penjelasan mendalam materi fisika fluida dan kinetika molekul oobleck. " * 80  # ~4800 chars
            sections[0] = sections[0].model_copy(update={"content": dense_content})

        elif mutation_id == "handout_almost_empty_accidental_page":
            spill_sec = DocumentContentSection(
                section_id="sec_spill_mutated",
                title="Catatan Tambahan",
                level=2,
                sequence_index=len(sections) + 1,
                content="Selesai.",  # Only 1 word on separate page
            )
            sections.append(spill_sec)

        elif mutation_id == "handout_severe_whitespace_imbalance":
            meta = dict(sections[0].metadata)
            meta["whitespace_ratio"] = 0.88
            sections[0] = sections[0].model_copy(update={"content": "Definisi singkat.", "metadata": meta})

        elif mutation_id == "handout_repeated_page_composition":
            for i in range(len(sections)):
                meta = dict(sections[i].metadata)
                meta["composition_template"] = "monotonous_single_column_block"
                sections[i] = sections[i].model_copy(update={"metadata": meta})

        elif mutation_id == "handout_paragraph_fragmentation":
            frag_content = "\n\n".join([f"Pernyataan poin ke-{i}." for i in range(1, 16)])
            sections[0] = sections[0].model_copy(update={"content": frag_content})

        elif mutation_id == "handout_abrupt_section_transition":
            meta = dict(sections[0].metadata)
            meta["transition_coherence"] = 0.1
            sections[0] = sections[0].model_copy(update={"metadata": meta})

        elif mutation_id == "handout_duplicate_explanatory_block":
            if len(sections) >= 2:
                dup_text = "Fluida non-Newtonian adalah fluida yang viskositasnya berubah terhadap gaya geser atau tegangan yang diberikan secara eksternal."
                s0 = sections[0].model_copy(update={"content": dup_text})
                s1 = sections[1].model_copy(update={"content": dup_text})
                sections[0] = s0
                sections[1] = s1

        elif mutation_id == "handout_tiny_body_text":
            meta = dict(sections[0].metadata)
            meta["body_font_size"] = 6.0
            sections[0] = sections[0].model_copy(update={"metadata": meta})

        elif mutation_id == "handout_weak_heading_hierarchy":
            meta = dict(sections[0].metadata)
            meta["heading_font_size"] = 10.0
            meta["body_font_size"] = 10.0
            sections[0] = sections[0].model_copy(update={"metadata": meta})

        elif mutation_id == "handout_excessive_line_length":
            meta = dict(sections[0].metadata)
            meta["characters_per_line"] = 165
            sections[0] = sections[0].model_copy(update={"metadata": meta})

        elif mutation_id == "handout_critical_concept_buried":
            wall = ("Teks pengantar latar belakang tanpa henti tentang sejarah laboratorium. " * 30) + \
                   " KATA KUNCI UTAMA: VISKOSITAS CRITICAL. " + \
                   ("Teks pengantar lanjutan tanpa pemisahan paragraf sama sekali. " * 30)
            sections[0] = sections[0].model_copy(update={"content": wall})

        elif mutation_id == "handout_excessive_bullet_nesting":
            meta = dict(sections[0].metadata)
            meta["max_bullet_nesting"] = 5
            sections[0] = sections[0].model_copy(update={"metadata": meta})

        elif mutation_id == "handout_multiple_unrelated_concepts_merged":
            merged = "KONSEP A: Viskositas fluida. KONSEP B: Termodinamika gas ideal. KONSEP C: Optika geometri gelombang. KONSEP D: Gaya gravitasi Newton."
            sections[0] = sections[0].model_copy(update={"content": merged})

        mutated_doc = doc.model_copy(
            update={
                "sections": tuple(sections),
                "total_sections": len(sections),
            }
        )
        return mutated_doc, mutation
