"""
Universal Knowledge Core — Scientific Document Contract Adapter.

Phase 2A Controlled Renderer Adapter Integration:
Translates ScientificDocument RenderArtifact (ScientificArgumentUnits) into LegacyScientificDocument
(LegacyKtiBabSections adhering to KtiBab Indonesian standard).

Preserves:
- Claim -> Evidence -> Argument relationship structures
- Explicit evidence item IDs and relationship IDs — NEVER flattened into anonymous prose
- Scientific claims without evidence remain flagged or isolated as limitations
- Strict chapter ordering: BAB 1 -> BAB 2 -> BAB 3 -> BAB 4 -> BAB 5
- Complete bidirectional traceability (Many-to-One mapping supported)

Contains zero AI calls, citation fabrication, or renderer imports.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict

from app.intelligence.schemas import KtiBab
from app.integration.artifact_bridge.contracts import RenderArtifact, RenderUnit
from app.integration.renderer_adapters.base import RendererContractAdapter
from app.integration.renderer_adapters.contracts import (
    GroupingDecisionTrace,
    LegacyKtiBabSection,
    LegacyScientificDocument,
    LegacyScientificEvidence,
    LegacyScientificSubsection,
)

# Deterministic mapping from Argument Roles to KTI Chapters
ROLE_TO_KTI_BAB = {
    "BACKGROUND_CLAIM": KtiBab.BAB_1,
    "HYPOTHESIS": KtiBab.BAB_2,
    "METHODOLOGY_DESCRIPTION": KtiBab.BAB_3,
    "EMPIRICAL_EVIDENCE": KtiBab.BAB_4,
    "COUNTER_CONSIDERATION": KtiBab.BAB_5,
    "LIMITATION": KtiBab.BAB_5,
    "CONCLUSION": KtiBab.BAB_5,
}

KTI_BAB_TITLES = {
    KtiBab.BAB_1: "BAB I: PENDAHULUAN",
    KtiBab.BAB_2: "BAB II: TINJAUAN PUSTAKA",
    KtiBab.BAB_3: "BAB III: METODOLOGI PENELITIAN",
    KtiBab.BAB_4: "BAB IV: HASIL DAN PEMBAHASAN",
    KtiBab.BAB_5: "BAB V: KESIMPULAN DAN SARAN",
}


class ScientificDocumentContractAdapter(RendererContractAdapter):
    """Adapts ScientificDocument RenderArtifact into LegacyScientificDocument."""

    @property
    def supported_artifact_type(self) -> str:
        return "SCIENTIFIC_DOCUMENT"

    def adapt(
        self,
        render_artifact: RenderArtifact,
        arguments_per_subsection: int = 3,
        grouping_mode: str = "chunk",
    ) -> LegacyScientificDocument:
        """Deterministically adapts scientific RenderArtifact into LegacyScientificDocument.

        Args:
            render_artifact: Certified scientific RenderArtifact contract.
            arguments_per_subsection: Target number of arguments grouped per subsection.
            grouping_mode: "chunk", "compatibility", or "1_to_1".

        Returns:
            LegacyScientificDocument organized by standard KtiBab sections with traces.
        """
        self.validate_artifact(render_artifact)

        # 1. Validate render units and organize arguments by KtiBab
        bab_arguments: Dict[KtiBab, List[RenderUnit]] = defaultdict(list)
        unsupported_claims_flagged: List[str] = []
        evidence_graph: Dict[str, List[str]] = defaultdict(list)

        for unit in render_artifact.units:
            if unit.role != "SCIENTIFIC_ARGUMENT":
                raise ValueError(
                    f"Unsupported unit role '{unit.role}' in scientific RenderArtifact. "
                    f"Expected 'SCIENTIFIC_ARGUMENT'."
                )

            role_str = unit.semantic_metadata.get("argument_role")
            if not role_str:
                raise ValueError(
                    f"RenderUnit '{unit.unit_id}' missing required 'argument_role' metadata."
                )

            target_bab = ROLE_TO_KTI_BAB.get(role_str, KtiBab.BAB_4)
            bab_arguments[target_bab].append(unit)

            # Check for ungrounded claims:
            # Empirical evidence units MUST have supporting evidence links
            ev_ids = unit.semantic_metadata.get("supporting_evidence_unit_ids", unit.supporting_content)
            rel_ids = unit.semantic_metadata.get("evidence_relationship_ids", ())

            if role_str == "EMPIRICAL_EVIDENCE" and not ev_ids:
                unsupported_claims_flagged.append(
                    f"Claim in unit '{unit.unit_id}' lacks supporting empirical evidence."
                )

            # Record in evidence graph
            claim_id = unit.semantic_metadata.get("claim_unit_id", unit.unit_id)
            for eid in ev_ids:
                evidence_graph[claim_id].append(eid)
            for rid in rel_ids:
                evidence_graph[claim_id].append(rid)

        # 2. Construct LegacyKtiBabSections with grouped subsections
        babs: List[LegacyKtiBabSection] = []
        all_decision_traces: List[GroupingDecisionTrace] = []
        source_to_subsec_map: Dict[str, List[str]] = defaultdict(list)
        total_args = 0
        total_ev_links = 0

        ordered_babs = [
            KtiBab.BAB_1,
            KtiBab.BAB_2,
            KtiBab.BAB_3,
            KtiBab.BAB_4,
            KtiBab.BAB_5,
        ]

        bab_sequence = 1
        for bab in ordered_babs:
            units_in_bab = bab_arguments.get(bab, [])
            if not units_in_bab:
                # Still create standard bab container to preserve structural sequence
                babs.append(
                    LegacyKtiBabSection(
                        bab=bab,
                        title=KTI_BAB_TITLES[bab],
                        sequence_index=bab_sequence,
                        subsections=tuple(),
                        source_element_ids=tuple(),
                    )
                )
                bab_sequence += 1
                continue

            arg_chunks: List[List[RenderUnit]] = []
            if grouping_mode == "1_to_1" or arguments_per_subsection == 1:
                for u in units_in_bab:
                    arg_chunks.append([u])
            elif grouping_mode == "compatibility":
                curr_chunk: List[RenderUnit] = []
                for u in units_in_bab:
                    if not curr_chunk:
                        curr_chunk.append(u)
                        continue
                    last_u = curr_chunk[-1]
                    same_role = (u.semantic_metadata.get("argument_role") == last_u.semantic_metadata.get("argument_role"))
                    is_contiguous = (u.sequence_index == last_u.sequence_index + 1)
                    capacity_ok = (len(curr_chunk) < arguments_per_subsection and len(curr_chunk) < 5)

                    if same_role and is_contiguous and capacity_ok:
                        curr_chunk.append(u)
                    else:
                        arg_chunks.append(curr_chunk)
                        curr_chunk = [u]
                if curr_chunk:
                    arg_chunks.append(curr_chunk)
            else:  # grouping_mode == "chunk"
                chunk_size = max(1, arguments_per_subsection)
                arg_chunks = [
                    units_in_bab[i : i + chunk_size]
                    for i in range(0, len(units_in_bab), chunk_size)
                ]

            subsections: List[LegacyScientificSubsection] = []
            bab_source_element_ids: List[str] = []
            sub_counter = 1

            for chunk in arg_chunks:
                sub_id = f"sub_{bab.value}_{sub_counter:02d}"
                first_unit = chunk[0]
                role_label = first_unit.semantic_metadata.get("argument_role", "ARGUMENT")
                sub_title = f"Subbab {bab_sequence}.{sub_counter}: {role_label.replace('_', ' ').title()}"

                claims: List[str] = []
                arg_ids: List[str] = []
                ev_items: List[LegacyScientificEvidence] = []
                ev_ids_all: List[str] = []
                rel_ids_all: List[str] = []
                counter_cons: List[str] = []
                limits: List[str] = []
                unsupported_in_sub: List[str] = []
                confidences: List[float] = []
                chunk_source_elem_ids: List[str] = []

                for u in chunk:
                    total_args += 1
                    bp_id = u.traceability_refs.blueprint_element_id
                    chunk_source_elem_ids.append(bp_id)
                    bab_source_element_ids.append(bp_id)
                    source_to_subsec_map[bp_id].append(sub_id)

                    claims.append(u.content)
                    arg_ids.append(u.unit_id)

                    conf = float(u.semantic_metadata.get("confidence", 1.0))
                    confidences.append(conf)

                    u_ev_ids = u.semantic_metadata.get("supporting_evidence_unit_ids", u.supporting_content)
                    u_rel_ids = u.semantic_metadata.get("evidence_relationship_ids", ())
                    u_counters = u.semantic_metadata.get("counter_considerations", ())

                    if u.semantic_metadata.get("argument_role") == "LIMITATION":
                        limits.append(u.content)
                    elif u_counters:
                        counter_cons.extend(u_counters)

                    if not u_ev_ids and u.semantic_metadata.get("argument_role") == "EMPIRICAL_EVIDENCE":
                        unsupported_in_sub.append(u.content)

                    # Build explicit evidence items
                    for eid in u_ev_ids:
                        ev_ids_all.append(eid)
                        total_ev_links += 1
                        ev_items.append(
                            LegacyScientificEvidence(
                                evidence_id=eid,
                                evidence_text=f"Supporting evidence for claim {u.unit_id}",
                                relationship_id=u_rel_ids[0] if u_rel_ids else "",
                                source_refs=(u.unit_id,),
                            )
                        )

                    for rid in u_rel_ids:
                        rel_ids_all.append(rid)

                min_confidence = min(confidences) if confidences else 1.0

                subsec = LegacyScientificSubsection(
                    subsection_id=sub_id,
                    title=sub_title,
                    sequence_index=sub_counter,
                    argument_ids=tuple(arg_ids),
                    claims=tuple(claims),
                    evidence_items=tuple(ev_items),
                    evidence_ids=tuple(dict.fromkeys(ev_ids_all)),
                    relationship_ids=tuple(dict.fromkeys(rel_ids_all)),
                    counter_considerations=tuple(dict.fromkeys(counter_cons)),
                    limitations=tuple(dict.fromkeys(limits)),
                    unsupported_claims=tuple(unsupported_in_sub),
                    confidence_score=round(min_confidence, 3),
                    source_element_ids=tuple(chunk_source_elem_ids),
                    metadata={
                        "arguments_count": len(chunk),
                        "roles": [u.semantic_metadata.get("argument_role") for u in chunk],
                    },
                )
                subsections.append(subsec)

                trace = GroupingDecisionTrace(
                    group_id=sub_id,
                    source_element_ids=tuple(chunk_source_elem_ids),
                    grouping_reason=f"KTI {bab.value} thematic grouping ({len(chunk)} arguments, role: {role_label})",
                    compatibility_signals=tuple(f"role_{u.semantic_metadata.get('argument_role')}" for u in chunk),
                    continuity_signals=(f"sequence_indices_{chunk[0].sequence_index}_to_{chunk[-1].sequence_index}",),
                    capacity_constraint=f"arguments_per_subsection={arguments_per_subsection}",
                )
                all_decision_traces.append(trace)
                sub_counter += 1

            bab_sec = LegacyKtiBabSection(
                bab=bab,
                title=KTI_BAB_TITLES[bab],
                sequence_index=bab_sequence,
                subsections=tuple(subsections),
                source_element_ids=tuple(bab_source_element_ids),
            )
            babs.append(bab_sec)
            bab_sequence += 1

        return LegacyScientificDocument(
            document_id=f"sci_doc_{render_artifact.artifact_id}",
            title=render_artifact.document_title,
            babs=tuple(babs),
            total_arguments=total_args,
            total_evidence_links=total_ev_links,
            source_to_subsection_map={k: tuple(v) for k, v in source_to_subsec_map.items()},
            evidence_traceability_graph={k: tuple(v) for k, v in evidence_graph.items()},
            unsupported_claims_flagged=tuple(unsupported_claims_flagged),
            grouping_decision_traces=tuple(all_decision_traces),
            metadata={
                "source_artifact_id": render_artifact.artifact_id,
                "source_blueprint_id": render_artifact.source_blueprint_id,
                "audience_level": render_artifact.metadata.audience_level,
                "total_units_adapted": len(render_artifact.units),
                "arguments_per_subsection": arguments_per_subsection,
                "grouping_mode": grouping_mode,
            },
        )
