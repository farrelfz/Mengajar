"""
Universal Document Intelligence System V5 — Presentation Adversary.

Phase 2C: Generates deterministic bad Presentation decks across:
- Category A: Duplication (exact, near, 5 consecutive identical, repeated generic card)
- Category B: Visual Hierarchy (ratio too small, visually equal, competing primary elements)
- Category C: Density (excessive density, extreme whitespace, >6 generic cards)
- Category D: Semantic Visual Mismatch (PROCESS as cards, COMPARISON as paragraph, etc.)
- Category E: Readability (tiny text, text clipping, overlapping content)
- Category F: Rhythm (streak of same composition, streak of high density, abrupt collapse)
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Tuple

from app.integration.renderer_adapters.contracts import (
    LegacyPresentationDeck,
    SlideBlueprint,
)
from app.quality.adversarial.base import BaseArtifactAdversary
from app.quality.adversarial.mutation_contract import ArtifactMutation
from app.quality.calibration.failure_taxonomy import FailureCategory, FailureSeverity


class PresentationAdversary(BaseArtifactAdversary):
    """Adversarial mutation engine for presentation slide decks."""

    @property
    def supported_artifact_type(self) -> str:
        return "PRESENTATION"

    def list_mutations(self) -> List[ArtifactMutation]:
        return [
            # CATEGORY A — DUPLICATION
            ArtifactMutation.create(
                mutation_id="presentation_exact_duplicate_slides",
                artifact_type="PRESENTATION",
                failure_category=FailureCategory.REPETITION_FAILURE,
                target_element_ids=["slide_01", "slide_02"],
                mutation_description="Duplicates slide 1 verbatim into slide 2.",
                expected_quality_signal="text_similarity",
                expected_severity=FailureSeverity.CRITICAL,
            ),
            ArtifactMutation.create(
                mutation_id="presentation_near_duplicate_composition",
                artifact_type="PRESENTATION",
                failure_category=FailureCategory.REPETITION_FAILURE,
                target_element_ids=["slide_02", "slide_03"],
                mutation_description="Slide 3 is 95% textually identical to slide 2 with only minor word changes.",
                expected_quality_signal="text_similarity",
                expected_severity=FailureSeverity.WARNING,
            ),
            ArtifactMutation.create(
                mutation_id="presentation_five_consecutive_identical_layout",
                artifact_type="PRESENTATION",
                failure_category=FailureCategory.REPETITION_FAILURE,
                target_element_ids=["slide_01", "slide_02", "slide_03", "slide_04", "slide_05"],
                mutation_description="Forces 5 consecutive slides to use identical 'concept_card' layout.",
                expected_quality_signal="layout_diversity",
                expected_severity=FailureSeverity.WARNING,
            ),
            ArtifactMutation.create(
                mutation_id="presentation_repeated_generic_card",
                artifact_type="PRESENTATION",
                failure_category=FailureCategory.COMPOSITION_FAILURE,
                target_element_ids=["all_slides"],
                mutation_description="Replaces all specialized layouts with generic rectangular cards.",
                expected_quality_signal="composition_diversity",
                expected_severity=FailureSeverity.WARNING,
            ),
            # CATEGORY B — VISUAL HIERARCHY
            ArtifactMutation.create(
                mutation_id="presentation_headline_body_ratio_small",
                artifact_type="PRESENTATION",
                failure_category=FailureCategory.READABILITY_FAILURE,
                target_element_ids=["slide_02"],
                mutation_description="Headline font size set to 12pt with 11pt body text (ratio 1.09 < 1.30).",
                expected_quality_signal="visual_hierarchy_ratio",
                expected_severity=FailureSeverity.WARNING,
            ),
            ArtifactMutation.create(
                mutation_id="presentation_all_text_visually_equal",
                artifact_type="PRESENTATION",
                failure_category=FailureCategory.READABILITY_FAILURE,
                target_element_ids=["slide_03"],
                mutation_description="Headline, body, and caption all use identical 12pt font and regular weight.",
                expected_quality_signal="visual_hierarchy_ratio",
                expected_severity=FailureSeverity.WARNING,
            ),
            ArtifactMutation.create(
                mutation_id="presentation_competing_primary_elements",
                artifact_type="PRESENTATION",
                failure_category=FailureCategory.COMPOSITION_FAILURE,
                target_element_ids=["slide_02"],
                mutation_description="Four separate primary hero titles competing on one slide.",
                expected_quality_signal="primary_element_competition",
                expected_severity=FailureSeverity.WARNING,
            ),
            # CATEGORY C — DENSITY
            ArtifactMutation.create(
                mutation_id="presentation_excessive_density",
                artifact_type="PRESENTATION",
                failure_category=FailureCategory.DENSITY_FAILURE,
                target_element_ids=["slide_02"],
                mutation_description="Injects 1900 characters of dense prose into a single slide.",
                expected_quality_signal="slide_character_density",
                expected_severity=FailureSeverity.ERROR,
            ),
            ArtifactMutation.create(
                mutation_id="presentation_extreme_whitespace",
                artifact_type="PRESENTATION",
                failure_category=FailureCategory.DENSITY_FAILURE,
                target_element_ids=["slide_03"],
                mutation_description="Slide contains only 1 word, leaving 98% empty accidental whitespace.",
                expected_quality_signal="whitespace_occupancy",
                expected_severity=FailureSeverity.WARNING,
            ),
            ArtifactMutation.create(
                mutation_id="presentation_more_than_six_cards",
                artifact_type="PRESENTATION",
                failure_category=FailureCategory.COMPOSITION_FAILURE,
                target_element_ids=["slide_02"],
                mutation_description="Slide contains 9 rectangular card components causing card overload.",
                expected_quality_signal="card_overload",
                expected_severity=FailureSeverity.WARNING,
            ),
            # CATEGORY D — SEMANTIC VISUAL MISMATCH
            ArtifactMutation.create(
                mutation_id="presentation_process_as_cards",
                artifact_type="PRESENTATION",
                failure_category=FailureCategory.SEMANTIC_LAYOUT_FAILURE,
                target_element_ids=["slide_04"],
                mutation_description="Sequential PROCESS narrative rendered as unrelated static generic cards.",
                expected_quality_signal="visual_grammar_alignment",
                expected_severity=FailureSeverity.ERROR,
            ),
            ArtifactMutation.create(
                mutation_id="presentation_comparison_as_paragraph",
                artifact_type="PRESENTATION",
                failure_category=FailureCategory.SEMANTIC_LAYOUT_FAILURE,
                target_element_ids=["slide_05"],
                mutation_description="Comparative dual-entity data rendered as an unstructured single paragraph.",
                expected_quality_signal="visual_grammar_alignment",
                expected_severity=FailureSeverity.WARNING,
            ),
            ArtifactMutation.create(
                mutation_id="presentation_question_as_dense_explanation",
                artifact_type="PRESENTATION",
                failure_category=FailureCategory.SEMANTIC_LAYOUT_FAILURE,
                target_element_ids=["slide_01"],
                mutation_description="HOOK/QUESTION narrative filled with dense explanatory paragraphs.",
                expected_quality_signal="visual_grammar_alignment",
                expected_severity=FailureSeverity.WARNING,
            ),
            ArtifactMutation.create(
                mutation_id="presentation_cause_effect_unrelated",
                artifact_type="PRESENTATION",
                failure_category=FailureCategory.SEMANTIC_LAYOUT_FAILURE,
                target_element_ids=["slide_06"],
                mutation_description="CAUSE_EFFECT relationship rendered without directional connection.",
                expected_quality_signal="visual_grammar_alignment",
                expected_severity=FailureSeverity.WARNING,
            ),
            # CATEGORY E — READABILITY
            ArtifactMutation.create(
                mutation_id="presentation_tiny_text",
                artifact_type="PRESENTATION",
                failure_category=FailureCategory.READABILITY_FAILURE,
                target_element_ids=["slide_02"],
                mutation_description="Body text font size forced to 6.0pt below readable threshold.",
                expected_quality_signal="minimum_body_font_size",
                expected_severity=FailureSeverity.CRITICAL,
            ),
            ArtifactMutation.create(
                mutation_id="presentation_text_clipping",
                artifact_type="PRESENTATION",
                failure_category=FailureCategory.READABILITY_FAILURE,
                target_element_ids=["slide_02"],
                mutation_description="Content bounding box extends beyond viewport dimensions causing text clipping.",
                expected_quality_signal="text_overflow",
                expected_severity=FailureSeverity.CRITICAL,
            ),
            ArtifactMutation.create(
                mutation_id="presentation_overlapping_content",
                artifact_type="PRESENTATION",
                failure_category=FailureCategory.COMPOSITION_FAILURE,
                target_element_ids=["slide_02"],
                mutation_description="Two text blocks overlap at the exact same coordinates.",
                expected_quality_signal="element_collision",
                expected_severity=FailureSeverity.CRITICAL,
            ),
            # CATEGORY F — RHYTHM
            ArtifactMutation.create(
                mutation_id="presentation_long_streak_same_composition",
                artifact_type="PRESENTATION",
                failure_category=FailureCategory.FLOW_FAILURE,
                target_element_ids=["slide_01", "slide_02", "slide_03", "slide_04"],
                mutation_description="4 consecutive slides share identical spatial distribution.",
                expected_quality_signal="composition_repetition_streak",
                expected_severity=FailureSeverity.WARNING,
            ),
            ArtifactMutation.create(
                mutation_id="presentation_long_streak_high_density",
                artifact_type="PRESENTATION",
                failure_category=FailureCategory.FLOW_FAILURE,
                target_element_ids=["slide_02", "slide_03", "slide_04"],
                mutation_description="3 consecutive slides with cognitive load > 1.8.",
                expected_quality_signal="high_cognitive_load_streak",
                expected_severity=FailureSeverity.WARNING,
            ),
            ArtifactMutation.create(
                mutation_id="presentation_abrupt_rhythm_collapse",
                artifact_type="PRESENTATION",
                failure_category=FailureCategory.FLOW_FAILURE,
                target_element_ids=["slide_03", "slide_04"],
                mutation_description="Extreme cognitive overload slide followed immediately by an empty slide.",
                expected_quality_signal="rhythm_dynamism",
                expected_severity=FailureSeverity.WARNING,
            ),
        ]

    def apply_mutation(
        self, deck: LegacyPresentationDeck, mutation_id: str
    ) -> Tuple[LegacyPresentationDeck, ArtifactMutation]:
        mutations_map = {m.mutation_id: m for m in self.list_mutations()}
        if mutation_id not in mutations_map:
            raise ValueError(f"Unknown mutation_id '{mutation_id}' for PresentationAdversary")

        mutation = mutations_map[mutation_id]
        new_slides: List[SlideBlueprint] = list(deck.slides)

        if not new_slides:
            return deck, mutation

        if mutation_id == "presentation_exact_duplicate_slides":
            if len(new_slides) >= 2:
                s0 = new_slides[0]
                dup_slide = s0.model_copy(
                    update={
                        "slide_id": f"{s0.slide_id}_exact_dup",
                        "slide_number": 2,
                    }
                )
                new_slides[1] = dup_slide

        elif mutation_id == "presentation_near_duplicate_composition":
            if len(new_slides) >= 2:
                s0 = new_slides[0]
                near_dup = s0.model_copy(
                    update={
                        "slide_id": f"{s0.slide_id}_near_dup",
                        "slide_number": 2,
                        "content": s0.content + " sedikit catatan.",
                    }
                )
                new_slides[1] = near_dup

        elif mutation_id == "presentation_five_consecutive_identical_layout":
            for idx in range(min(5, len(new_slides))):
                new_slides[idx] = new_slides[idx].model_copy(
                    update={"layout": "concept_card"}
                )

        elif mutation_id == "presentation_repeated_generic_card":
            for idx in range(len(new_slides)):
                new_slides[idx] = new_slides[idx].model_copy(
                    update={"layout": "concept_card"}
                )

        elif mutation_id == "presentation_headline_body_ratio_small":
            meta = dict(new_slides[0].metadata)
            meta["title_font_size"] = 12.0
            meta["body_font_size"] = 11.0
            new_slides[0] = new_slides[0].model_copy(
                update={"metadata": meta}
            )

        elif mutation_id == "presentation_all_text_visually_equal":
            meta = dict(new_slides[0].metadata)
            meta["title_font_size"] = 12.0
            meta["body_font_size"] = 12.0
            new_slides[0] = new_slides[0].model_copy(
                update={"metadata": meta}
            )

        elif mutation_id == "presentation_competing_primary_elements":
            meta = dict(new_slides[0].metadata)
            meta["competing_primary_elements_count"] = 4
            new_slides[0] = new_slides[0].model_copy(
                update={"metadata": meta}
            )

        elif mutation_id == "presentation_excessive_density":
            dense_text = "Eksperimen viskositas non-Newtonian fluida oobleck. " * 45  # ~1900 chars
            new_slides[0] = new_slides[0].model_copy(
                update={
                    "content": dense_text,
                    "cognitive_load": 2.5,
                }
            )

        elif mutation_id == "presentation_extreme_whitespace":
            new_slides[0] = new_slides[0].model_copy(
                update={
                    "title": ".",
                    "content": "Halo",
                    "bullet_points": tuple(),
                    "cognitive_load": 0.05,
                }
            )

        elif mutation_id == "presentation_more_than_six_cards":
            meta = dict(new_slides[0].metadata)
            meta["card_count"] = 9
            new_slides[0] = new_slides[0].model_copy(
                update={
                    "bullet_points": tuple(f"Card {i}" for i in range(1, 10)),
                    "metadata": meta,
                }
            )

        elif mutation_id == "presentation_process_as_cards":
            # PROCESS narrative function in concept_card layout
            new_slides[0] = new_slides[0].model_copy(
                update={
                    "narrative_function": "PROCESS",
                    "layout": "concept_card",
                    "title": "Prosedur Pembuatan Oobleck",
                }
            )

        elif mutation_id == "presentation_comparison_as_paragraph":
            new_slides[0] = new_slides[0].model_copy(
                update={
                    "narrative_function": "COMPARISON",
                    "layout": "concept_card",
                    "content": "Fluida Newtonian vs Non-Newtonian ditulis dalam satu paragraf panjang tanpa tabel atau split perbandingan.",
                }
            )

        elif mutation_id == "presentation_question_as_dense_explanation":
            dense_expl = "Jawaban lengkap penjelasan sebelum siswa berpikir: " + ("penjelasan detail " * 50)
            new_slides[0] = new_slides[0].model_copy(
                update={
                    "narrative_function": "QUESTION",
                    "content": dense_expl,
                }
            )

        elif mutation_id == "presentation_cause_effect_unrelated":
            new_slides[0] = new_slides[0].model_copy(
                update={
                    "narrative_function": "CAUSE_EFFECT",
                    "layout": "concept_card",
                    "content": "Pemberian tekanan dan pengerasan terjadi begitu saja tanpa visualisasi relasi kausal.",
                }
            )

        elif mutation_id == "presentation_tiny_text":
            meta = dict(new_slides[0].metadata)
            meta["min_body_font"] = 6.0
            new_slides[0] = new_slides[0].model_copy(
                update={"metadata": meta}
            )

        elif mutation_id == "presentation_text_clipping":
            meta = dict(new_slides[0].metadata)
            meta["text_overflow"] = True
            meta["clipping_error"] = "Bbox [10, 800, 1950, 1100] exceeds viewport height [1080]"
            new_slides[0] = new_slides[0].model_copy(
                update={"metadata": meta}
            )

        elif mutation_id == "presentation_overlapping_content":
            meta = dict(new_slides[0].metadata)
            meta["element_collision"] = True
            new_slides[0] = new_slides[0].model_copy(
                update={"metadata": meta}
            )

        elif mutation_id == "presentation_long_streak_same_composition":
            for i in range(min(4, len(new_slides))):
                meta = dict(new_slides[i].metadata)
                meta["composition_fingerprint"] = [0.25, 0.25, 0.25, 0.25]
                new_slides[i] = new_slides[i].model_copy(
                    update={"layout": "concept_card", "metadata": meta}
                )

        elif mutation_id == "presentation_long_streak_high_density":
            for i in range(min(3, len(new_slides))):
                new_slides[i] = new_slides[i].model_copy(
                    update={"cognitive_load": 2.2, "content": "Teks berdensitas tinggi " * 40}
                )

        elif mutation_id == "presentation_abrupt_rhythm_collapse":
            if len(new_slides) >= 2:
                new_slides[0] = new_slides[0].model_copy(update={"cognitive_load": 2.5})
                new_slides[1] = new_slides[1].model_copy(update={"cognitive_load": 0.05, "content": " "})

        mutated_deck = deck.model_copy(
            update={
                "slides": tuple(new_slides),
                "total_slides": len(new_slides),
            }
        )
        return mutated_deck, mutation
