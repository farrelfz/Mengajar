"""
Universal Document Intelligence System V5 — Worksheet Adversary.

Phase 2C: Generates deterministic bad Worksheet artifacts across:
- Category A: Pedagogical Flow (reflection before observation, data analysis before collection, etc.)
- Category B: Anti-Spoiling (explanation leaked before prediction, answer leaked in prompt, etc.)
- Category C: Interaction Design (workspace too small, workspace detached, no recording table, etc.)
- Category D: Quiz Collapse (10 consecutive recall questions, multiple-choice dominance)
- Category E: Visual (excessive density, invisible activity hierarchy, overlapping workspace)
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from app.integration.renderer_adapters.contracts import (
    LegacyWorksheetActivity,
    LegacyWorksheetDocument,
    LegacyWorksheetSection,
)
from app.quality.adversarial.base import BaseArtifactAdversary
from app.quality.adversarial.mutation_contract import ArtifactMutation
from app.quality.calibration.failure_taxonomy import FailureCategory, FailureSeverity


class WorksheetAdversary(BaseArtifactAdversary):
    """Adversarial mutation engine for active learning worksheets."""

    @property
    def supported_artifact_type(self) -> str:
        return "WORKSHEET"

    def list_mutations(self) -> List[ArtifactMutation]:
        return [
            # CATEGORY A — PEDAGOGICAL FLOW
            ArtifactMutation.create(
                mutation_id="worksheet_question_sequence_no_inquiry",
                artifact_type="WORKSHEET",
                failure_category=FailureCategory.PEDAGOGICAL_FAILURE,
                target_element_ids=["activity_01", "activity_02"],
                mutation_description="Questions repeated without inquiry flow or scaffolded reasoning.",
                expected_quality_signal="inquiry_integrity",
                expected_severity=FailureSeverity.WARNING,
            ),
            ArtifactMutation.create(
                mutation_id="worksheet_reflection_before_observation",
                artifact_type="WORKSHEET",
                failure_category=FailureCategory.PEDAGOGICAL_FAILURE,
                target_element_ids=["activity_reflection", "activity_observation"],
                mutation_description="REFLECTION activity placed before student makes OBSERVATION.",
                expected_quality_signal="inquiry_sequence",
                expected_severity=FailureSeverity.ERROR,
            ),
            ArtifactMutation.create(
                mutation_id="worksheet_data_analysis_before_collection",
                artifact_type="WORKSHEET",
                failure_category=FailureCategory.PEDAGOGICAL_FAILURE,
                target_element_ids=["activity_analysis", "activity_observation"],
                mutation_description="DATA_ANALYSIS activity placed before data collection observation.",
                expected_quality_signal="inquiry_sequence",
                expected_severity=FailureSeverity.ERROR,
            ),
            ArtifactMutation.create(
                mutation_id="worksheet_prediction_after_explanation",
                artifact_type="WORKSHEET",
                failure_category=FailureCategory.PEDAGOGICAL_FAILURE,
                target_element_ids=["activity_prediction"],
                mutation_description="PREDICTION requested after theoretical mechanism is already explained.",
                expected_quality_signal="inquiry_sequence",
                expected_severity=FailureSeverity.ERROR,
            ),
            # CATEGORY B — ANTI-SPOILING
            ArtifactMutation.create(
                mutation_id="worksheet_explanation_leaked_before_prediction",
                artifact_type="WORKSHEET",
                failure_category=FailureCategory.PEDAGOGICAL_FAILURE,
                target_element_ids=["activity_leaked_exp"],
                mutation_description="Explanation of fluid hardening leaked before student makes prediction.",
                expected_quality_signal="anti_spoiling_leak",
                expected_severity=FailureSeverity.CRITICAL,
            ),
            ArtifactMutation.create(
                mutation_id="worksheet_answer_leaked_inside_question",
                artifact_type="WORKSHEET",
                failure_category=FailureCategory.PEDAGOGICAL_FAILURE,
                target_element_ids=["activity_answer_in_prompt"],
                mutation_description="Prompt contains the exact answer ('Karena oobleck mengeras saat dipukul, apa yang terjadi?').",
                expected_quality_signal="anti_spoiling_leak",
                expected_severity=FailureSeverity.CRITICAL,
            ),
            ArtifactMutation.create(
                mutation_id="worksheet_observation_conclusion_prefilled",
                artifact_type="WORKSHEET",
                failure_category=FailureCategory.PEDAGOGICAL_FAILURE,
                target_element_ids=["activity_prefilled_obs"],
                mutation_description="Observation workspace pre-filled with the expected experimental result.",
                expected_quality_signal="anti_spoiling_leak",
                expected_severity=FailureSeverity.CRITICAL,
            ),
            # CATEGORY C — INTERACTION DESIGN
            ArtifactMutation.create(
                mutation_id="worksheet_workspace_too_small",
                artifact_type="WORKSHEET",
                failure_category=FailureCategory.ARTIFACT_SPECIFIC_FAILURE,
                target_element_ids=["activity_small_ws"],
                mutation_description="Student response workspace allocated only 15pt height (unusable for handwriting).",
                expected_quality_signal="workspace_adequacy",
                expected_severity=FailureSeverity.WARNING,
            ),
            ArtifactMutation.create(
                mutation_id="worksheet_workspace_detached_from_activity",
                artifact_type="WORKSHEET",
                failure_category=FailureCategory.ARTIFACT_SPECIFIC_FAILURE,
                target_element_ids=["activity_detached_ws"],
                mutation_description="Response workspace rendered 2 pages away from the question prompt.",
                expected_quality_signal="workspace_proximity",
                expected_severity=FailureSeverity.WARNING,
            ),
            ArtifactMutation.create(
                mutation_id="worksheet_no_observation_recording_structure",
                artifact_type="WORKSHEET",
                failure_category=FailureCategory.ARTIFACT_SPECIFIC_FAILURE,
                target_element_ids=["activity_no_obs_structure"],
                mutation_description="Observation activity requests multi-step data but provides no recording table or lines.",
                expected_quality_signal="interaction_affordance",
                expected_severity=FailureSeverity.ERROR,
            ),
            ArtifactMutation.create(
                mutation_id="worksheet_no_data_analysis_space",
                artifact_type="WORKSHEET",
                failure_category=FailureCategory.ARTIFACT_SPECIFIC_FAILURE,
                target_element_ids=["activity_no_calc_space"],
                mutation_description="Complex quantitative calculation requested without scratch or calculation space.",
                expected_quality_signal="interaction_affordance",
                expected_severity=FailureSeverity.ERROR,
            ),
            # CATEGORY D — QUIZ COLLAPSE
            ArtifactMutation.create(
                mutation_id="worksheet_ten_consecutive_short_answer",
                artifact_type="WORKSHEET",
                failure_category=FailureCategory.PEDAGOGICAL_FAILURE,
                target_element_ids=["all_activities"],
                mutation_description="Worksheet collapses into 10 consecutive factual recall questions without inquiry.",
                expected_quality_signal="quiz_collapse_ratio",
                expected_severity=FailureSeverity.ERROR,
            ),
            ArtifactMutation.create(
                mutation_id="worksheet_dominated_by_multiple_choice",
                artifact_type="WORKSHEET",
                failure_category=FailureCategory.PEDAGOGICAL_FAILURE,
                target_element_ids=["all_activities"],
                mutation_description="85% of activities formatted as multiple-choice trivia questions.",
                expected_quality_signal="quiz_collapse_ratio",
                expected_severity=FailureSeverity.ERROR,
            ),
            # CATEGORY E — VISUAL
            ArtifactMutation.create(
                mutation_id="worksheet_excessive_density",
                artifact_type="WORKSHEET",
                failure_category=FailureCategory.DENSITY_FAILURE,
                target_element_ids=["section_01"],
                mutation_description="Section text contains 3800 characters leaving no physical room for student work.",
                expected_quality_signal="worksheet_density",
                expected_severity=FailureSeverity.ERROR,
            ),
            ArtifactMutation.create(
                mutation_id="worksheet_activity_hierarchy_invisible",
                artifact_type="WORKSHEET",
                failure_category=FailureCategory.READABILITY_FAILURE,
                target_element_ids=["activity_01"],
                mutation_description="Activity headers and instructions rendered with identical typography.",
                expected_quality_signal="activity_hierarchy",
                expected_severity=FailureSeverity.WARNING,
            ),
            ArtifactMutation.create(
                mutation_id="worksheet_workspace_overlaps_content",
                artifact_type="WORKSHEET",
                failure_category=FailureCategory.COMPOSITION_FAILURE,
                target_element_ids=["activity_overlap"],
                mutation_description="Student response box overlaps prompt text visually.",
                expected_quality_signal="element_collision",
                expected_severity=FailureSeverity.CRITICAL,
            ),
            ArtifactMutation.create(
                mutation_id="worksheet_uneven_workspace_allocation",
                artifact_type="WORKSHEET",
                failure_category=FailureCategory.COMPOSITION_FAILURE,
                target_element_ids=["activity_uneven"],
                mutation_description="1-line binary question given 300pt box, 5-step derivation given 20pt box.",
                expected_quality_signal="workspace_balance",
                expected_severity=FailureSeverity.WARNING,
            ),
        ]

    def apply_mutation(
        self, doc: LegacyWorksheetDocument, mutation_id: str
    ) -> Tuple[LegacyWorksheetDocument, ArtifactMutation]:
        mutations_map = {m.mutation_id: m for m in self.list_mutations()}
        if mutation_id not in mutations_map:
            raise ValueError(f"Unknown mutation_id '{mutation_id}' for WorksheetAdversary")

        mutation = mutations_map[mutation_id]
        sections = list(doc.sections)

        if not sections:
            return doc, mutation

        first_sec = sections[0]
        activities = list(first_sec.activities)

        if mutation_id == "worksheet_question_sequence_no_inquiry":
            # Replace all activities with repetitive recall questions
            for i in range(len(activities)):
                activities[i] = activities[i].model_copy(
                    update={
                        "activity_type": "QUESTION",
                        "title": f"Pertanyaan Faktual {i+1}",
                        "prompt_text": f"Sebutkan definisi fluida poin ke-{i+1} dari ingatan Anda.",
                        "requires_student_workspace": False,
                    }
                )

        elif mutation_id == "worksheet_reflection_before_observation":
            if len(activities) >= 2:
                # Force REFLECTION at index 0 and OBSERVATION at index 1
                activities[0] = activities[0].model_copy(
                    update={"activity_type": "REFLECTION", "title": "Refleksi Hasil"}
                )
                activities[1] = activities[1].model_copy(
                    update={"activity_type": "OBSERVATION", "title": "Observasi Awal"}
                )

        elif mutation_id == "worksheet_data_analysis_before_collection":
            if len(activities) >= 2:
                activities[0] = activities[0].model_copy(
                    update={"activity_type": "DATA_ANALYSIS", "title": "Analisis Grafik Data"}
                )
                activities[1] = activities[1].model_copy(
                    update={"activity_type": "OBSERVATION", "title": "Pengambilan Data"}
                )

        elif mutation_id == "worksheet_prediction_after_explanation":
            if len(activities) >= 2:
                activities[0] = activities[0].model_copy(
                    update={
                        "activity_type": "EXPLANATION",
                        "title": "Penjelasan Teori",
                        "prompt_text": "Molekul maizena mengunci saat diberi gaya geser cepat.",
                        "withhold_explanation": False,
                    }
                )
                activities[1] = activities[1].model_copy(
                    update={"activity_type": "PREDICTION", "title": "Prediksi Anda"}
                )

        elif mutation_id == "worksheet_explanation_leaked_before_prediction":
            meta = dict(activities[0].metadata)
            meta["leaked_explanation"] = True
            activities[0] = activities[0].model_copy(
                update={
                    "activity_type": "PREDICTION",
                    "prompt_text": "Fluida ini mengeras karena ikatan antarmolekul mengunci (jawaban: mengeras). Apa prediksi Anda?",
                    "withhold_explanation": False,  # VIOLATION: withholding breached!
                    "metadata": meta,
                }
            )

        elif mutation_id == "worksheet_answer_leaked_inside_question":
            meta = dict(activities[0].metadata)
            meta["answer_leak"] = True
            activities[0] = activities[0].model_copy(
                update={
                    "prompt_text": "Karena oobleck berubah menjadi padat saat dipukul cepat, apa yang terjadi pada wujudnya saat dipukul?",
                    "withhold_explanation": False,
                    "metadata": meta,
                }
            )

        elif mutation_id == "worksheet_observation_conclusion_prefilled":
            meta = dict(activities[0].metadata)
            meta["conclusion_prefilled"] = True
            activities[0] = activities[0].model_copy(
                update={
                    "activity_type": "OBSERVATION",
                    "prompt_text": "Catat pengamatan Anda (Kesimpulan sudah terbukti: viskositas naik secara eksponensial).",
                    "metadata": meta,
                }
            )

        elif mutation_id == "worksheet_workspace_too_small":
            meta = dict(activities[0].metadata)
            meta["workspace_height_pt"] = 15.0  # severely cramped
            activities[0] = activities[0].model_copy(update={"metadata": meta})

        elif mutation_id == "worksheet_workspace_detached_from_activity":
            meta = dict(activities[0].metadata)
            meta["workspace_page_distance"] = 2
            activities[0] = activities[0].model_copy(update={"metadata": meta})

        elif mutation_id == "worksheet_no_observation_recording_structure":
            meta = dict(activities[0].metadata)
            meta["has_recording_structure"] = False
            activities[0] = activities[0].model_copy(
                update={
                    "activity_type": "OBSERVATION",
                    "prompt_text": "Lakukan 10 kali pengujian pada kecepatan berbeda dan catat semua waktu dan tegangan geser.",
                    "requires_student_workspace": False,
                    "metadata": meta,
                }
            )

        elif mutation_id == "worksheet_no_data_analysis_space":
            meta = dict(activities[0].metadata)
            meta["has_calculation_space"] = False
            activities[0] = activities[0].model_copy(
                update={
                    "activity_type": "DATA_ANALYSIS",
                    "prompt_text": "Hitung regresi linier viskositas dan tentukan koefisien k.",
                    "requires_student_workspace": False,
                    "metadata": meta,
                }
            )

        elif mutation_id == "worksheet_ten_consecutive_short_answer":
            new_acts = []
            for i in range(10):
                new_acts.append(
                    LegacyWorksheetActivity(
                        activity_id=f"act_recall_{i+1}",
                        activity_type="RECALL_QUESTION",
                        title=f"Soal Pilihan Singkat {i+1}",
                        prompt_text=f"Pertanyaan hapalan fakta ke-{i+1}: Apa rumus viskositas?",
                        scaffolding_level="LOW",
                        withhold_explanation=True,
                        requires_student_workspace=False,
                    )
                )
            sections = [first_sec.model_copy(update={"activities": tuple(new_acts)})]
            activities = new_acts

        elif mutation_id == "worksheet_dominated_by_multiple_choice":
            new_acts = []
            for i in range(10):
                new_acts.append(
                    LegacyWorksheetActivity(
                        activity_id=f"act_mcq_{i+1}",
                        activity_type="MULTIPLE_CHOICE",
                        title=f"Pilihan Ganda {i+1}",
                        prompt_text=f"Soal {i+1}: Pilih A, B, C, atau D.",
                        scaffolding_level="LOW",
                        withhold_explanation=True,
                        requires_student_workspace=False,
                    )
                )
            sections = [first_sec.model_copy(update={"activities": tuple(new_acts)})]
            activities = new_acts

        elif mutation_id == "worksheet_excessive_density":
            dense_prompt = "Instruksi pengerjaan laboratorium yang sangat panjang dan memadati seluruh halaman A4 tanpa menyisakan ruang interaksi aktif siswa. " * 35
            activities[0] = activities[0].model_copy(update={"prompt_text": dense_prompt})

        elif mutation_id == "worksheet_activity_hierarchy_invisible":
            meta = dict(activities[0].metadata)
            meta["activity_hierarchy_ratio"] = 1.0
            activities[0] = activities[0].model_copy(update={"metadata": meta})

        elif mutation_id == "worksheet_workspace_overlaps_content":
            meta = dict(activities[0].metadata)
            meta["workspace_collision"] = True
            activities[0] = activities[0].model_copy(update={"metadata": meta})

        elif mutation_id == "worksheet_uneven_workspace_allocation":
            meta = dict(activities[0].metadata)
            meta["workspace_allocation_imbalance"] = True
            activities[0] = activities[0].model_copy(update={"metadata": meta})

        # Update first section with modified activities
        sections[0] = first_sec.model_copy(
            update={
                "activities": tuple(activities),
            }
        )

        mutated_doc = doc.model_copy(
            update={
                "sections": tuple(sections),
                "total_activities": sum(len(s.activities) for s in sections),
            }
        )
        return mutated_doc, mutation
