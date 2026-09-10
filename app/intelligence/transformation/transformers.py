"""
Universal Knowledge Core — Information Transformation Strategies.

Phase 1C.1 Adversarial Hardening:
Implements deterministic, offline semantic transformers with strict scientific evidence
discipline and context-sensitive inquiry generation.

100% offline, zero AI calls, zero HTML/CSS/PDF dependencies.
"""

from __future__ import annotations

import time
from typing import Dict, List, Tuple, Set, Any, Optional

from app.intelligence.schemas import (
    ContentType,
    KnowledgeCategory,
    KnowledgeUnit,
    UniversalKnowledgeManifest,
)
from app.intelligence.schemas.relationships import RelationshipType
from app.intelligence.transformation.blueprints import (
    ConceptualBeat,
    ExplanatorySection,
    HandoutBlueprint,
    LearningActivity,
    LearningActivityType,
    PresentationBlueprint,
    ScientificArgumentRole,
    ScientificArgumentUnit,
    ScientificDocumentBlueprint,
    WorksheetBlueprint,
)
from app.intelligence.transformation.intent import ResolvedArtifactIntent
from app.intelligence.transformation.selection import SelectedKnowledgeSet


# ============================================================================
# 1. PRESENTATION TRANSFORMER
# ============================================================================

class PresentationTransformer:
    """Transforms selected knowledge into progressive conceptual beats for presentations."""

    def transform(
        self,
        manifest: UniversalKnowledgeManifest,
        selection: SelectedKnowledgeSet,
        intent: ResolvedArtifactIntent,
    ) -> PresentationBlueprint:
        units = [selection.selected_units[uid] for uid in selection.selected_unit_ids if uid in selection.selected_units]

        beats: List[ConceptualBeat] = []
        narrative_stages = ["HOOK", "FOUNDATION", "CORE_MECHANISM", "APPLICATION", "SUMMARY"]

        # Group units into beats (1 primary concept + max 2 supporting units per beat)
        beat_idx = 0
        for i in range(0, len(units), 2):
            chunk = units[i : i + 2]
            primary = chunk[0]
            supporting = chunk[1:] if len(chunk) > 1 else []

            stage = narrative_stages[min(beat_idx, len(narrative_stages) - 1)]
            
            # Determine visual priority
            if primary.content_type == ContentType.FORMULA:
                vis_priority = "EQUATION_FOCUS"
            elif primary.content_type in (ContentType.PROCEDURE, ContentType.CONCEPT):
                vis_priority = "HIGH_DIAGRAM"
            else:
                vis_priority = "CONCEPT_TEXT"

            title_str = primary.title[:60] if len(primary.title) > 60 else primary.title

            beat = ConceptualBeat(
                beat_id=f"beat_{beat_idx + 1:02d}",
                sequence_index=beat_idx + 1,
                title=f"Beat {beat_idx + 1}: {title_str}",
                primary_concept_unit_id=primary.id,
                supporting_unit_ids=tuple(u.id for u in supporting),
                narrative_function=stage,
                information_gain=min(1.0, round(0.4 + (beat_idx * 0.1), 2)),
                cognitive_load_target=min(0.60, round(0.30 + (len(supporting) * 0.15), 2)),
                visual_priority=vis_priority,
                selection_rationale=f"Progressive beat created from primary unit {primary.id}",
                knowledge_unit_ids=tuple(u.id for u in chunk),
            )
            beats.append(beat)
            beat_idx += 1

        bp_id = f"bp_pres_{manifest.manifest_id[:8]}"
        return PresentationBlueprint(
            blueprint_id=bp_id,
            artifact_type=intent.artifact_type,
            source_manifest_id=manifest.manifest_id,
            document_title=manifest.document_title,
            intent=intent,
            selected_knowledge_unit_ids=selection.selected_unit_ids,
            selection_rationale=selection.selection_rationale,
            beats=tuple(beats),
        )


# ============================================================================
# 2. HANDOUT TRANSFORMER
# ============================================================================

class HandoutTransformer:
    """Transforms selected knowledge into hierarchical explanatory sections for handouts."""

    def transform(
        self,
        manifest: UniversalKnowledgeManifest,
        selection: SelectedKnowledgeSet,
        intent: ResolvedArtifactIntent,
    ) -> HandoutBlueprint:
        units = [selection.selected_units[uid] for uid in selection.selected_unit_ids if uid in selection.selected_units]

        sections: List[ExplanatorySection] = []
        
        # Group units by category or content type into comprehensive reading sections
        categories: Dict[str, List[KnowledgeUnit]] = {}
        for u in units:
            cat_name = u.category.value if hasattr(u.category, "value") else str(u.category)
            if cat_name not in categories:
                categories[cat_name] = []
            categories[cat_name].append(u)

        sec_idx = 1
        for cat_name, cat_units in categories.items():
            core_uids = [u.id for u in cat_units if u.content_type in (ContentType.DEFINITION, ContentType.CONCEPT, ContentType.FORMULA)]
            supp_uids = [u.id for u in cat_units if u.id not in core_uids]

            defs = [u.title for u in cat_units if u.content_type == ContentType.DEFINITION]
            examples = [u.title for u in cat_units if u.content_type == ContentType.EXAMPLE]
            rel_snippets = [f"Rel: {u.content_type.value}" for u in cat_units if u.content_type == ContentType.EXPLANATION]

            topic_title = f"{cat_name.replace('_', ' ').title()} - Detailed Overview"

            sec = ExplanatorySection(
                section_id=f"sec_{sec_idx:02d}",
                sequence_index=sec_idx,
                topic=topic_title,
                heading_level=1 if sec_idx == 1 else 2,
                core_unit_ids=tuple(core_uids if core_uids else [u.id for u in cat_units]),
                supporting_unit_ids=tuple(supp_uids),
                definitions=tuple(defs),
                examples=tuple(examples),
                relationships=tuple(rel_snippets),
                reading_depth="COMPREHENSIVE_REFERENCE",
                knowledge_unit_ids=tuple(u.id for u in cat_units),
            )
            sections.append(sec)
            sec_idx += 1

        bp_id = f"bp_handout_{manifest.manifest_id[:8]}"
        return HandoutBlueprint(
            blueprint_id=bp_id,
            artifact_type=intent.artifact_type,
            source_manifest_id=manifest.manifest_id,
            document_title=manifest.document_title,
            intent=intent,
            selected_knowledge_unit_ids=selection.selected_unit_ids,
            selection_rationale=selection.selection_rationale,
            sections=tuple(sections),
        )


# ============================================================================
# 3. WORKSHEET TRANSFORMER
# ============================================================================

class WorksheetTransformer:
    """Transforms selected knowledge into active learning activities for worksheets without answer spoiling."""

    def transform(
        self,
        manifest: UniversalKnowledgeManifest,
        selection: SelectedKnowledgeSet,
        intent: ResolvedArtifactIntent,
    ) -> WorksheetBlueprint:
        units = [selection.selected_units[uid] for uid in selection.selected_unit_ids if uid in selection.selected_units]

        activities: List[LearningActivity] = []
        activity_types = [
            LearningActivityType.PHENOMENON,
            LearningActivityType.PREDICTION,
            LearningActivityType.QUESTION,
            LearningActivityType.OBSERVATION,
            LearningActivityType.INVESTIGATION,
            LearningActivityType.DATA_ANALYSIS,
            LearningActivityType.REFLECTION,
        ]

        act_idx = 1
        for u in units:
            act_type = activity_types[(act_idx - 1) % len(activity_types)]
            
            # Formulate inquiry prompt based on activity type without revealing full answer
            if act_type == LearningActivityType.PHENOMENON:
                prompt = f"Amati fenomena berikut: '{u.title[:80]}...'. Catat hasil pengamatan awal Anda."
                reasoning = "OBSERVATIONAL_DEDUCTION"
            elif act_type == LearningActivityType.PREDICTION:
                prompt = f"Berdasarkan pemahaman Anda, prediksikan apa yang terjadi jika parameter pada '{u.title[:60]}' diubah."
                reasoning = "HYPOTHESIS_FORMATION"
            elif act_type == LearningActivityType.QUESTION:
                prompt = f"Jelaskan mekanisme dasar yang melatarbelakangi '{u.title[:60]}'."
                reasoning = "CONCEPTUAL_EXPLANATION"
            elif act_type == LearningActivityType.INVESTIGATION:
                prompt = f"Rancang langkah investigasi sederhana untuk menguji kebenaran konsep '{u.title[:60]}'."
                reasoning = "EXPERIMENTAL_DESIGN"
            elif act_type == LearningActivityType.DATA_ANALYSIS:
                prompt = f"Analisis data dan korelasi variabel terkait: '{u.title[:60]}'."
                reasoning = "DATA_INTERPRETATION"
            else:
                prompt = f"Refleksikan bagaimana konsep '{u.title[:60]}' dapat diterapkan dalam kehidupan sehari-hari."
                reasoning = "CRITICAL_REFLECTION"

            act = LearningActivity(
                activity_id=f"act_{act_idx:02d}",
                sequence_index=act_idx,
                activity_type=act_type,
                title=f"Aktivitas {act_idx}: {act_type.value.title()}",
                prompt_text=prompt,
                target_knowledge_unit_ids=(u.id,),
                scaffolding_level="MEDIUM" if act_idx <= 2 else "LOW",
                withhold_explanation=True,  # Crucial rule: answers withheld
                expected_reasoning_type=reasoning,
                knowledge_unit_ids=(u.id,),
            )
            activities.append(act)
            act_idx += 1

        bp_id = f"bp_ws_{manifest.manifest_id[:8]}"
        return WorksheetBlueprint(
            blueprint_id=bp_id,
            artifact_type=intent.artifact_type,
            source_manifest_id=manifest.manifest_id,
            document_title=manifest.document_title,
            intent=intent,
            selected_knowledge_unit_ids=selection.selected_unit_ids,
            selection_rationale=selection.selection_rationale,
            activities=tuple(activities),
        )


# ============================================================================
# 4. SCIENTIFIC DOCUMENT TRANSFORMER (STRICT EVIDENCE DISCIPLINE)
# ============================================================================

class ScientificDocumentTransformer:
    """Transforms selected knowledge into claim-evidence scientific argument units.
    
    STRICT INVARIANT: Concept relationships (causes, prerequisite_of, explained_by)
    do NOT qualify as scientific evidence edges. Evidence relationships are strictly
    filtered to SUPPORTED_BY, REFUTES, DEMONSTRATED_BY, and MEASURED_BY.
    """

    _VALID_EVIDENCE_RELATIONSHIP_TYPES: Set[RelationshipType] = {
        RelationshipType.SUPPORTED_BY,
        RelationshipType.REFUTES,
        RelationshipType.DEMONSTRATED_BY,
        RelationshipType.MEASURED_BY,
    }

    def transform(
        self,
        manifest: UniversalKnowledgeManifest,
        selection: SelectedKnowledgeSet,
        intent: ResolvedArtifactIntent,
    ) -> ScientificDocumentBlueprint:
        selected_uids = set(selection.selected_unit_ids)
        units = [selection.selected_units[uid] for uid in selection.selected_unit_ids if uid in selection.selected_units]

        # Map strictly VALID scientific evidence relationships (excluding concept relationships)
        evidence_rel_map: Dict[str, List[Any]] = {}
        for rel in manifest.relationships:
            if rel.relationship in self._VALID_EVIDENCE_RELATIONSHIP_TYPES:
                if rel.source_unit_id not in evidence_rel_map:
                    evidence_rel_map[rel.source_unit_id] = []
                evidence_rel_map[rel.source_unit_id].append(rel)

        arguments: List[ScientificArgumentUnit] = []
        roles = [
            ScientificArgumentRole.BACKGROUND_CLAIM,
            ScientificArgumentRole.HYPOTHESIS,
            ScientificArgumentRole.METHODOLOGY_DESCRIPTION,
            ScientificArgumentRole.EMPIRICAL_EVIDENCE,
            ScientificArgumentRole.CONCLUSION,
        ]

        arg_idx = 1
        for u in units:
            role = roles[(arg_idx - 1) % len(roles)]

            # Find real supporting evidence relationships in manifest
            rels = evidence_rel_map.get(u.id, [])
            evidence_uids = [r.target_unit_id for r in rels if r.target_unit_id in selected_uids]
            evidence_rel_ids = [f"{r.source_unit_id}->{r.relationship.value}->{r.target_unit_id}" for r in rels]

            counters = []
            if not evidence_uids and role in (ScientificArgumentRole.HYPOTHESIS, ScientificArgumentRole.EMPIRICAL_EVIDENCE):
                counters.append("Claim currently lacks empirical evidence relationships in manifest.")

            arg = ScientificArgumentUnit(
                argument_id=f"arg_{arg_idx:02d}",
                sequence_index=arg_idx,
                claim_unit_id=u.id,
                argument_role=role,
                claim_statement=u.title,
                supporting_evidence_unit_ids=tuple(evidence_uids),
                evidence_relationship_ids=tuple(evidence_rel_ids),
                counter_considerations=tuple(counters),
                confidence=u.classification_confidence if evidence_uids else min(u.classification_confidence, 0.60),
                source_traceability=tuple(f"doc:{u.provenance.source_document_id}/sec:{u.provenance.source_section_id}"),
                knowledge_unit_ids=tuple([u.id] + evidence_uids),
            )
            arguments.append(arg)
            arg_idx += 1

        bp_id = f"bp_sci_{manifest.manifest_id[:8]}"
        return ScientificDocumentBlueprint(
            blueprint_id=bp_id,
            artifact_type=intent.artifact_type,
            source_manifest_id=manifest.manifest_id,
            document_title=manifest.document_title,
            intent=intent,
            selected_knowledge_unit_ids=selection.selected_unit_ids,
            selection_rationale=selection.selection_rationale,
            arguments=tuple(arguments),
        )
