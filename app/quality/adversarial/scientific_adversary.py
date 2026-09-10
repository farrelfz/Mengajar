"""
Universal Document Intelligence System V5 — Scientific Document Adversary.

Phase 2C: Generates deterministic bad Scientific Documents (KTI) across:
- Category A: Scientific Structure (BAB inversion, results before methodology, etc.)
- Category B: Evidence Discipline (unsupported claim, wrong evidence link, ungrounded fact)
- Category C: Academic Integrity (missing citation, detached citation, fabricated citation)
- Category D: Document Composition (orphan subsection, empty subsection, split table)
- Category E: Argument Quality (duplicate argument, contradictory claims, stripped limitation)
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from app.integration.renderer_adapters.contracts import (
    LegacyKtiBabSection,
    LegacyScientificDocument,
    LegacyScientificEvidence,
    LegacyScientificSubsection,
)
from app.intelligence.schemas import KtiBab
from app.quality.adversarial.base import BaseArtifactAdversary
from app.quality.adversarial.mutation_contract import ArtifactMutation
from app.quality.calibration.failure_taxonomy import FailureCategory, FailureSeverity


class ScientificDocumentAdversary(BaseArtifactAdversary):
    """Adversarial mutation engine for scientific KTI documents."""

    @property
    def supported_artifact_type(self) -> str:
        return "SCIENTIFIC_DOCUMENT"

    def list_mutations(self) -> List[ArtifactMutation]:
        return [
            # CATEGORY A — SCIENTIFIC STRUCTURE
            ArtifactMutation.create(
                mutation_id="scientific_bab_hierarchy_inversion",
                artifact_type="SCIENTIFIC_DOCUMENT",
                failure_category=FailureCategory.STRUCTURAL_FAILURE,
                target_element_ids=["bab_04", "bab_03"],
                mutation_description="BAB IV (Hasil & Pembahasan) placed before BAB III (Metodologi Penelitian).",
                expected_quality_signal="bab_order_integrity",
                expected_severity=FailureSeverity.CRITICAL,
            ),
            ArtifactMutation.create(
                mutation_id="scientific_results_before_methodology",
                artifact_type="SCIENTIFIC_DOCUMENT",
                failure_category=FailureCategory.STRUCTURAL_FAILURE,
                target_element_ids=["bab_04", "bab_03"],
                mutation_description="Quantitative results presented before experimental procedure is defined.",
                expected_quality_signal="academic_flow",
                expected_severity=FailureSeverity.ERROR,
            ),
            ArtifactMutation.create(
                mutation_id="scientific_conclusion_before_discussion",
                artifact_type="SCIENTIFIC_DOCUMENT",
                failure_category=FailureCategory.STRUCTURAL_FAILURE,
                target_element_ids=["bab_05", "bab_04"],
                mutation_description="BAB V (Kesimpulan) placed before BAB IV (Pembahasan).",
                expected_quality_signal="bab_order_integrity",
                expected_severity=FailureSeverity.CRITICAL,
            ),
            ArtifactMutation.create(
                mutation_id="scientific_missing_argument_transition",
                artifact_type="SCIENTIFIC_DOCUMENT",
                failure_category=FailureCategory.FLOW_FAILURE,
                target_element_ids=["subsec_01", "subsec_02"],
                mutation_description="Subsections jump between disjoint domains without connecting argument.",
                expected_quality_signal="argument_continuity",
                expected_severity=FailureSeverity.WARNING,
            ),
            # CATEGORY B — EVIDENCE DISCIPLINE
            ArtifactMutation.create(
                mutation_id="scientific_claim_without_evidence",
                artifact_type="SCIENTIFIC_DOCUMENT",
                failure_category=FailureCategory.SCIENTIFIC_INTEGRITY_FAILURE,
                target_element_ids=["subsec_unsupported"],
                mutation_description="Broad empirical assertion made with 0 supporting evidence citations.",
                expected_quality_signal="evidence_discipline",
                expected_severity=FailureSeverity.CRITICAL,
            ),
            ArtifactMutation.create(
                mutation_id="scientific_evidence_attached_to_wrong_claim",
                artifact_type="SCIENTIFIC_DOCUMENT",
                failure_category=FailureCategory.SCIENTIFIC_INTEGRITY_FAILURE,
                target_element_ids=["subsec_mismatched_evidence"],
                mutation_description="Empirical viscosity data attached to safety hazard claim.",
                expected_quality_signal="evidence_claim_relevance",
                expected_severity=FailureSeverity.CRITICAL,
            ),
            ArtifactMutation.create(
                mutation_id="scientific_unsupported_claim_as_fact",
                artifact_type="SCIENTIFIC_DOCUMENT",
                failure_category=FailureCategory.SCIENTIFIC_INTEGRITY_FAILURE,
                target_element_ids=["subsec_unsupported_fact"],
                mutation_description="Speculative hypothesis presented as established physical law.",
                expected_quality_signal="epistemic_modality",
                expected_severity=FailureSeverity.CRITICAL,
            ),
            ArtifactMutation.create(
                mutation_id="scientific_evidence_relationship_silently_removed",
                artifact_type="SCIENTIFIC_DOCUMENT",
                failure_category=FailureCategory.TRACEABILITY_FAILURE,
                target_element_ids=["subsec_broken_rel"],
                mutation_description="Evidence text retained but explicit relationship metadata stripped.",
                expected_quality_signal="evidence_relationship_completeness",
                expected_severity=FailureSeverity.ERROR,
            ),
            # CATEGORY C — ACADEMIC INTEGRITY
            ArtifactMutation.create(
                mutation_id="scientific_citation_missing",
                artifact_type="SCIENTIFIC_DOCUMENT",
                failure_category=FailureCategory.SCIENTIFIC_INTEGRITY_FAILURE,
                target_element_ids=["claim_uncited"],
                mutation_description="Empirical quantitative finding lacks mandatory bibliographic citation.",
                expected_quality_signal="citation_integrity",
                expected_severity=FailureSeverity.CRITICAL,
            ),
            ArtifactMutation.create(
                mutation_id="scientific_citation_detached_from_claim",
                artifact_type="SCIENTIFIC_DOCUMENT",
                failure_category=FailureCategory.SCIENTIFIC_INTEGRITY_FAILURE,
                target_element_ids=["claim_detached_cite"],
                mutation_description="Citation marker separated from source claim by intervening unrelated paragraphs.",
                expected_quality_signal="citation_proximity",
                expected_severity=FailureSeverity.WARNING,
            ),
            ArtifactMutation.create(
                mutation_id="scientific_fabricated_citation_marker",
                artifact_type="SCIENTIFIC_DOCUMENT",
                failure_category=FailureCategory.SCIENTIFIC_INTEGRITY_FAILURE,
                target_element_ids=["claim_bogus_cite"],
                mutation_description="Citation references non-existent source identifier [BUKTI: ghost_ref_99].",
                expected_quality_signal="citation_integrity",
                expected_severity=FailureSeverity.CRITICAL,
            ),
            # CATEGORY D — DOCUMENT COMPOSITION
            ArtifactMutation.create(
                mutation_id="scientific_orphan_subsection",
                artifact_type="SCIENTIFIC_DOCUMENT",
                failure_category=FailureCategory.COMPOSITION_FAILURE,
                target_element_ids=["subsec_orphan"],
                mutation_description="Academic subsection consists of only a single 8-word sentence.",
                expected_quality_signal="subsection_depth",
                expected_severity=FailureSeverity.WARNING,
            ),
            ArtifactMutation.create(
                mutation_id="scientific_empty_academic_subsection",
                artifact_type="SCIENTIFIC_DOCUMENT",
                failure_category=FailureCategory.STRUCTURAL_FAILURE,
                target_element_ids=["subsec_empty"],
                mutation_description="Subsection heading declared with zero claims, evidence, or text.",
                expected_quality_signal="empty_subsection",
                expected_severity=FailureSeverity.ERROR,
            ),
            ArtifactMutation.create(
                mutation_id="scientific_table_split_incorrectly",
                artifact_type="SCIENTIFIC_DOCUMENT",
                failure_category=FailureCategory.COMPOSITION_FAILURE,
                target_element_ids=["subsec_table_split"],
                mutation_description="Experimental data table header detached from rows across page boundary.",
                expected_quality_signal="table_integrity",
                expected_severity=FailureSeverity.WARNING,
            ),
            ArtifactMutation.create(
                mutation_id="scientific_figure_caption_detached",
                artifact_type="SCIENTIFIC_DOCUMENT",
                failure_category=FailureCategory.COMPOSITION_FAILURE,
                target_element_ids=["subsec_caption_detached"],
                mutation_description="Scientific figure caption printed on subsequent page without the figure.",
                expected_quality_signal="figure_caption_coupling",
                expected_severity=FailureSeverity.WARNING,
            ),
            # CATEGORY E — ARGUMENT QUALITY
            ArtifactMutation.create(
                mutation_id="scientific_duplicate_argument",
                artifact_type="SCIENTIFIC_DOCUMENT",
                failure_category=FailureCategory.REPETITION_FAILURE,
                target_element_ids=["subsec_arg_dup1", "subsec_arg_dup2"],
                mutation_description="Exact same theoretical argument repeated in consecutive subsections.",
                expected_quality_signal="argument_redundancy",
                expected_severity=FailureSeverity.WARNING,
            ),
            ArtifactMutation.create(
                mutation_id="scientific_contradictory_adjacent_claims",
                artifact_type="SCIENTIFIC_DOCUMENT",
                failure_category=FailureCategory.SCIENTIFIC_INTEGRITY_FAILURE,
                target_element_ids=["subsec_contradiction"],
                mutation_description="Adjacent claims make mutually contradictory physical assertions.",
                expected_quality_signal="argument_consistency",
                expected_severity=FailureSeverity.CRITICAL,
            ),
            ArtifactMutation.create(
                mutation_id="scientific_limitation_removed_from_uncertain_conclusion",
                artifact_type="SCIENTIFIC_DOCUMENT",
                failure_category=FailureCategory.SCIENTIFIC_INTEGRITY_FAILURE,
                target_element_ids=["bab_05"],
                mutation_description="Methodological limitations stripped from uncertain conclusions.",
                expected_quality_signal="scientific_rigor",
                expected_severity=FailureSeverity.ERROR,
            ),
        ]

    def apply_mutation(
        self, doc: LegacyScientificDocument, mutation_id: str
    ) -> Tuple[LegacyScientificDocument, ArtifactMutation]:
        mutations_map = {m.mutation_id: m for m in self.list_mutations()}
        if mutation_id not in mutations_map:
            raise ValueError(f"Unknown mutation_id '{mutation_id}' for ScientificDocumentAdversary")

        mutation = mutations_map[mutation_id]
        babs = list(doc.babs)

        if not babs:
            return doc, mutation

        if mutation_id == "scientific_bab_hierarchy_inversion":
            # Swap BAB III and BAB IV
            idx_iii = next((i for i, b in enumerate(babs) if b.bab == KtiBab.BAB_3), -1)
            idx_iv = next((i for i, b in enumerate(babs) if b.bab == KtiBab.BAB_4), -1)
            if idx_iii != -1 and idx_iv != -1:
                babs[idx_iii], babs[idx_iv] = babs[idx_iv], babs[idx_iii]

        elif mutation_id == "scientific_results_before_methodology":
            # Invert order of BAB III and BAB IV
            idx_iii = next((i for i, b in enumerate(babs) if b.bab == KtiBab.BAB_3), -1)
            idx_iv = next((i for i, b in enumerate(babs) if b.bab == KtiBab.BAB_4), -1)
            if idx_iii != -1 and idx_iv != -1:
                babs[idx_iii], babs[idx_iv] = babs[idx_iv], babs[idx_iii]

        elif mutation_id == "scientific_conclusion_before_discussion":
            # Swap BAB IV and BAB V
            idx_iv = next((i for i, b in enumerate(babs) if b.bab == KtiBab.BAB_4), -1)
            idx_v = next((i for i, b in enumerate(babs) if b.bab == KtiBab.BAB_5), -1)
            if idx_iv != -1 and idx_v != -1:
                babs[idx_iv], babs[idx_v] = babs[idx_v], babs[idx_iv]

        elif mutation_id == "scientific_missing_argument_transition":
            meta = dict(babs[0].subsections[0].metadata) if babs[0].subsections else {}
            meta["argument_transition_gap"] = True
            if babs[0].subsections:
                new_subs = list(babs[0].subsections)
                new_subs[0] = new_subs[0].model_copy(update={"metadata": meta})
                babs[0] = babs[0].model_copy(update={"subsections": tuple(new_subs)})

        elif mutation_id == "scientific_claim_without_evidence":
            # Add an unsupported empirical claim to first subsection and clear evidence
            if babs[0].subsections:
                new_subs = list(babs[0].subsections)
                meta = dict(new_subs[0].metadata)
                meta["unsupported_claim_critical"] = True
                new_subs[0] = new_subs[0].model_copy(
                    update={
                        "claims": ("Oobleck terbukti mampu menahan peluru kaliber 9mm pada uji balistik.",),
                        "evidence_items": tuple(),
                        "evidence_ids": tuple(),
                        "unsupported_claims": ("Oobleck terbukti mampu menahan peluru kaliber 9mm pada uji balistik.",),
                        "metadata": meta,
                    }
                )
                babs[0] = babs[0].model_copy(update={"subsections": tuple(new_subs)})

        elif mutation_id == "scientific_evidence_attached_to_wrong_claim":
            if babs[0].subsections:
                new_subs = list(babs[0].subsections)
                meta = dict(new_subs[0].metadata)
                meta["evidence_relevance_mismatch"] = True
                new_subs[0] = new_subs[0].model_copy(
                    update={
                        "claims": ("Bahan maizena beracun dan mudah meledak di suhu ruang.",),
                        "evidence_items": (
                            LegacyScientificEvidence(
                                evidence_id="ev_wrong_01",
                                evidence_text="Viskositas meningkat dari 1.2 Pa.s menjadi 85.0 Pa.s.",
                                relationship_id="rel_viscosity",
                            ),
                        ),
                        "metadata": meta,
                    }
                )
                babs[0] = babs[0].model_copy(update={"subsections": tuple(new_subs)})

        elif mutation_id == "scientific_unsupported_claim_as_fact":
            if babs[0].subsections:
                new_subs = list(babs[0].subsections)
                meta = dict(new_subs[0].metadata)
                meta["unsupported_claim_critical"] = True
                new_subs[0] = new_subs[0].model_copy(
                    update={
                        "claims": ("Secara absolut fluida non-Newtonian melanggar hukum termodinamika kedua.",),
                        "unsupported_claims": ("Secara absolut fluida non-Newtonian melanggar hukum termodinamika kedua.",),
                        "confidence_score": 0.2,
                        "metadata": meta,
                    }
                )
                babs[0] = babs[0].model_copy(update={"subsections": tuple(new_subs)})

        elif mutation_id == "scientific_evidence_relationship_silently_removed":
            if babs[0].subsections:
                new_subs = list(babs[0].subsections)
                new_subs[0] = new_subs[0].model_copy(
                    update={
                        "relationship_ids": tuple(),  # Relationship metadata stripped!
                    }
                )
                babs[0] = babs[0].model_copy(update={"subsections": tuple(new_subs)})

        elif mutation_id == "scientific_citation_missing":
            meta = dict(babs[0].subsections[0].metadata) if babs[0].subsections else {}
            meta["citation_missing"] = True
            if babs[0].subsections:
                new_subs = list(babs[0].subsections)
                new_subs[0] = new_subs[0].model_copy(
                    update={
                        "claims": ("Hasil uji tegangan geser menunjukkan nilai kritis 14.5 kPa.",),
                        "evidence_items": tuple(),
                        "metadata": meta,
                    }
                )
                babs[0] = babs[0].model_copy(update={"subsections": tuple(new_subs)})

        elif mutation_id == "scientific_citation_detached_from_claim":
            meta = dict(babs[0].subsections[0].metadata) if babs[0].subsections else {}
            meta["citation_detached_paragraphs"] = 4
            if babs[0].subsections:
                new_subs = list(babs[0].subsections)
                new_subs[0] = new_subs[0].model_copy(update={"metadata": meta})
                babs[0] = babs[0].model_copy(update={"subsections": tuple(new_subs)})

        elif mutation_id == "scientific_fabricated_citation_marker":
            if babs[0].subsections:
                new_subs = list(babs[0].subsections)
                new_subs[0] = new_subs[0].model_copy(
                    update={
                        "evidence_ids": ("ghost_ref_99",),
                        "evidence_items": (
                            LegacyScientificEvidence(
                                evidence_id="ghost_ref_99",
                                evidence_text="Sumber tidak ada di daftar pustaka.",
                            ),
                        ),
                    }
                )
                babs[0] = babs[0].model_copy(update={"subsections": tuple(new_subs)})

        elif mutation_id == "scientific_orphan_subsection":
            orphan = LegacyScientificSubsection(
                subsection_id="sub_orphan_mutated",
                title="Catatan Singkat",
                sequence_index=99,
                claims=("Hanya satu kalimat pendek.",),
            )
            babs[0] = babs[0].model_copy(
                update={"subsections": babs[0].subsections + (orphan,)}
            )

        elif mutation_id == "scientific_empty_academic_subsection":
            empty_sub = LegacyScientificSubsection(
                subsection_id="sub_empty_mutated",
                title="Subbab Kosong Tanpa Isi",
                sequence_index=100,
                claims=tuple(),
                evidence_items=tuple(),
            )
            babs[0] = babs[0].model_copy(
                update={"subsections": babs[0].subsections + (empty_sub,)}
            )

        elif mutation_id == "scientific_table_split_incorrectly":
            meta = dict(babs[0].subsections[0].metadata) if babs[0].subsections else {}
            meta["table_split_error"] = True
            if babs[0].subsections:
                new_subs = list(babs[0].subsections)
                new_subs[0] = new_subs[0].model_copy(update={"metadata": meta})
                babs[0] = babs[0].model_copy(update={"subsections": tuple(new_subs)})

        elif mutation_id == "scientific_figure_caption_detached":
            meta = dict(babs[0].subsections[0].metadata) if babs[0].subsections else {}
            meta["figure_caption_detached"] = True
            if babs[0].subsections:
                new_subs = list(babs[0].subsections)
                new_subs[0] = new_subs[0].model_copy(update={"metadata": meta})
                babs[0] = babs[0].model_copy(update={"subsections": tuple(new_subs)})

        elif mutation_id == "scientific_duplicate_argument":
            if babs[0].subsections and len(babs[0].subsections) >= 2:
                new_subs = list(babs[0].subsections)
                dup_claims = ("Argumen identik: Oobleck mengental karena interaksi hidrodinamik suspensi.",)
                new_subs[0] = new_subs[0].model_copy(update={"claims": dup_claims})
                new_subs[1] = new_subs[1].model_copy(update={"claims": dup_claims})
                babs[0] = babs[0].model_copy(update={"subsections": tuple(new_subs)})

        elif mutation_id == "scientific_contradictory_adjacent_claims":
            if babs[0].subsections:
                new_subs = list(babs[0].subsections)
                meta = dict(new_subs[0].metadata)
                meta["contradictory_claims"] = True
                new_subs[0] = new_subs[0].model_copy(
                    update={
                        "claims": (
                            "Viskositas meningkat terhadap laju regangan geser (shear thickening).",
                            "Viskositas mutlak menurun terhadap laju regangan geser (shear thinning).",
                        ),
                        "metadata": meta,
                    }
                )
                babs[0] = babs[0].model_copy(update={"subsections": tuple(new_subs)})

        elif mutation_id == "scientific_limitation_removed_from_uncertain_conclusion":
            idx_v = next((i for i, b in enumerate(babs) if b.bab == KtiBab.BAB_5), -1)
            if idx_v != -1 and babs[idx_v].subsections:
                new_subs = list(babs[idx_v].subsections)
                new_subs[0] = new_subs[0].model_copy(
                    update={
                        "limitations": tuple(),  # Limitations completely removed!
                    }
                )
                babs[idx_v] = babs[idx_v].model_copy(update={"subsections": tuple(new_subs)})

        mutated_doc = doc.model_copy(
            update={
                "babs": tuple(babs),
            }
        )
        return mutated_doc, mutation
