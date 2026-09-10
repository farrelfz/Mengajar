"""
Universal Knowledge Core — Handout Contract Adapter.

Phase 2A Controlled Renderer Adapter Integration:
Translates Handout RenderArtifact (ExplanatorySections) into DocumentContent and DocumentOutline.

Preserves:
- Heading hierarchy and level structure
- Reading continuity and sequential flow
- Explicit definitions and examples
- Complete bidirectional traceability (Many-to-One mapping supported)

Contains zero AI calls, layout generation, or renderer imports.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from app.integration.artifact_bridge.contracts import RenderArtifact, RenderUnit
from app.integration.renderer_adapters.base import RendererContractAdapter
from app.integration.renderer_adapters.contracts import (
    DocumentContent,
    DocumentContentSection,
    DocumentOutline,
    DocumentOutlineItem,
    GroupingDecisionTrace,
)


def _extract_definitions_and_examples(unit: RenderUnit) -> Tuple[List[str], List[str]]:
    defs: List[str] = []
    exs: List[str] = []

    if unit.content:
        content_text = unit.content
        if "Definitions:" in content_text:
            part = content_text.split("Definitions:", 1)[1]
            if "Examples:" in part:
                part = part.split("Examples:", 1)[0]
            for line in part.splitlines():
                line = line.strip()
                if line.startswith("- "):
                    defs.append(line[2:].strip())
                elif line.startswith("-"):
                    defs.append(line[1:].strip())

        if "Examples:" in content_text:
            part = content_text.split("Examples:", 1)[1]
            for line in part.splitlines():
                line = line.strip()
                if line.startswith("- "):
                    exs.append(line[2:].strip())
                elif line.startswith("-"):
                    exs.append(line[1:].strip())

    if unit.supporting_content:
        exs.extend(unit.supporting_content)

    meta_defs = unit.semantic_metadata.get("definitions", [])
    if isinstance(meta_defs, (list, tuple)):
        defs.extend(meta_defs)

    meta_exs = unit.semantic_metadata.get("examples", [])
    if isinstance(meta_exs, (list, tuple)):
        exs.extend(meta_exs)

    return defs, exs


class HandoutContractAdapter(RendererContractAdapter):
    """Adapts Handout RenderArtifact into DocumentContent and DocumentOutline."""

    @property
    def supported_artifact_type(self) -> str:
        return "HANDOUT"

    def adapt(
        self,
        render_artifact: RenderArtifact,
        group_by_section: bool = True,
    ) -> DocumentContent:
        """Deterministically adapts handout RenderArtifact into DocumentContent.

        Args:
            render_artifact: Certified handout RenderArtifact contract.
            group_by_section: If True, uses RenderSection hierarchy or structural grouping.

        Returns:
            DocumentContent containing DocumentOutline and DocumentContentSections.
        """
        self.validate_artifact(render_artifact)

        # 1. Validate render units
        for unit in render_artifact.units:
            if unit.role not in ("EXPLANATORY_SECTION", "EXPLANATORY_BLOCK"):
                raise ValueError(
                    f"Unsupported unit role '{unit.role}' in handout RenderArtifact. "
                    f"Expected 'EXPLANATORY_SECTION'."
                )

        outline_items: List[DocumentOutlineItem] = []
        content_sections: List[DocumentContentSection] = []
        all_source_refs: List[str] = []
        decision_traces: List[GroupingDecisionTrace] = []

        # 2. Determine section grouping
        if group_by_section and render_artifact.sections:
            for sec in render_artifact.sections:
                sec_units = sec.units if sec.units else ()
                if not sec_units:
                    continue

                source_elem_ids = tuple(u.traceability_refs.blueprint_element_id for u in sec_units)
                for u in sec_units:
                    all_source_refs.append(u.unit_id)

                all_defs: List[str] = []
                all_exs: List[str] = []
                body_texts: List[str] = []

                for u in sec_units:
                    if u.content:
                        body_texts.append(u.content)
                    u_defs, u_exs = _extract_definitions_and_examples(u)
                    all_defs.extend(u_defs)
                    all_exs.extend(u_exs)

                heading_lvl = sec.section_metadata.get(
                    "heading_level", sec_units[0].semantic_metadata.get("heading_level", 1)
                )
                reading_depth = sec.section_metadata.get(
                    "reading_depth", sec_units[0].semantic_metadata.get("reading_depth", "STANDARD")
                )

                outline_item = DocumentOutlineItem(
                    section_id=sec.section_id,
                    title=sec.title,
                    level=heading_lvl,
                    sequence_index=sec.sequence_index,
                    source_element_ids=source_elem_ids,
                )
                outline_items.append(outline_item)

                content_sec = DocumentContentSection(
                    section_id=sec.section_id,
                    title=sec.title,
                    level=heading_lvl,
                    sequence_index=sec.sequence_index,
                    content="\n\n".join(body_texts),
                    definitions=tuple(dict.fromkeys(all_defs)),
                    examples=tuple(dict.fromkeys(all_exs)),
                    reading_depth=reading_depth,
                    source_element_ids=source_elem_ids,
                    metadata={
                        "unit_count": len(sec_units),
                        "source_blueprint_id": render_artifact.source_blueprint_id,
                    },
                )
                content_sections.append(content_sec)

                decision_traces.append(
                    GroupingDecisionTrace(
                        group_id=sec.section_id,
                        source_element_ids=source_elem_ids,
                        grouping_reason=f"Structural section grouping: '{sec.title}'",
                        compatibility_signals=("render_section_hierarchy", f"heading_level_{heading_lvl}"),
                        continuity_signals=(f"sequence_index_{sec.sequence_index}",),
                        capacity_constraint=f"unit_count={len(sec_units)}",
                    )
                )
        else:
            for unit in render_artifact.units:
                all_source_refs.append(unit.unit_id)
                heading_lvl = unit.semantic_metadata.get("heading_level", 1)
                reading_depth = unit.semantic_metadata.get("reading_depth", "STANDARD")
                source_elem_ids = (unit.traceability_refs.blueprint_element_id,)

                u_defs, u_exs = _extract_definitions_and_examples(unit)

                outline_item = DocumentOutlineItem(
                    section_id=f"out_{unit.unit_id}",
                    title=unit.title,
                    level=heading_lvl,
                    sequence_index=unit.sequence_index,
                    source_element_ids=source_elem_ids,
                )
                outline_items.append(outline_item)

                content_sec = DocumentContentSection(
                    section_id=f"sec_{unit.unit_id}",
                    title=unit.title,
                    level=heading_lvl,
                    sequence_index=unit.sequence_index,
                    content=unit.content,
                    definitions=tuple(dict.fromkeys(u_defs)),
                    examples=tuple(dict.fromkeys(u_exs)),
                    reading_depth=reading_depth,
                    source_element_ids=source_elem_ids,
                    metadata=unit.semantic_metadata,
                )
                content_sections.append(content_sec)

                decision_traces.append(
                    GroupingDecisionTrace(
                        group_id=f"sec_{unit.unit_id}",
                        source_element_ids=source_elem_ids,
                        grouping_reason="1-to-1 unit section allocation",
                        compatibility_signals=("solitary_unit", f"heading_level_{heading_lvl}"),
                        continuity_signals=(f"sequence_index_{unit.sequence_index}",),
                        capacity_constraint="single_unit",
                    )
                )

        outline = DocumentOutline(
            outline_id=f"outline_{render_artifact.artifact_id}",
            title=render_artifact.document_title,
            items=tuple(outline_items),
        )

        return DocumentContent(
            document_id=f"doc_{render_artifact.artifact_id}",
            title=render_artifact.document_title,
            outline=outline,
            sections=tuple(content_sections),
            total_sections=len(content_sections),
            source_refs=tuple(all_source_refs),
            grouping_decision_traces=tuple(decision_traces),
            metadata={
                "source_artifact_id": render_artifact.artifact_id,
                "source_blueprint_id": render_artifact.source_blueprint_id,
                "audience_level": render_artifact.metadata.audience_level,
                "total_units_adapted": len(render_artifact.units),
            },
        )
