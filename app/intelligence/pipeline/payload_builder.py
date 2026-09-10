"""
Stage 5 — PayloadBuilder.

Constructs atomic KnowledgeUnit instances with strongly-typed KnowledgePayloadUnion
and deterministic stable IDs (ku_<12-char-hex-hash>).
DO NOT infer cross-unit relationships.
"""

from __future__ import annotations

import re
from typing import List
from app.intelligence.pipeline.ambiguity_resolver import ResolvedUnit
from app.intelligence.schemas import (
    ArgumentPayload,
    ConceptPayload,
    ContentType,
    EvidencePayload,
    EvidenceType,
    FormalPayload,
    IntrinsicImportance,
    KnowledgeCategory,
    KnowledgePayloadUnion,
    KnowledgeUnit,
    PedagogicalPayload,
    ProcedurePayload,
    ProcedureStep,
    QualitativeEvidenceData,
    QuantitativeEvidenceData,
    VariableDefinition,
    generate_stable_knowledge_id,
)


class PayloadBuilder:
    """Stage 5: Constructs atomic typed KnowledgeUnits."""

    def build_units(self, resolved_units: List[ResolvedUnit]) -> List[KnowledgeUnit]:
        units: List[KnowledgeUnit] = []
        unit_map: dict[str, KnowledgeUnit] = {}

        for ru in resolved_units:
            cand = ru.classified_unit.candidate
            c_type = ru.final_content_type
            category = ru.final_category

            # 1. Deterministic Stable ID Hashing
            stable_id = generate_stable_knowledge_id(
                source_fingerprint=cand.source_fingerprint,
                raw_content=cand.raw_content,
                content_type=c_type,
            )

            # 2. Semantic Identity Merge Check
            # If identical semantic unit (same doc, normalized text & c_type) was already built,
            # merge provenance anchors deterministically without creating duplicate unit IDs or losing locations.
            if stable_id in unit_map:
                existing_unit = unit_map[stable_id]
                existing_keys = {
                    (p.source_section_id, p.source_start_line)
                    for p in existing_unit.all_provenances
                }
                cand_key = (cand.provenance.source_section_id, cand.provenance.source_start_line)
                if cand_key not in existing_keys:
                    existing_unit.secondary_provenances.append(cand.provenance)
                continue

            # 3. Build Typed Payload Family
            payload = self._build_payload(cand.raw_content, c_type, cand.parent_section_title)

            # Default baseline intrinsic importance (refined in Stage 8)
            importance = IntrinsicImportance.SUPPORTING
            if c_type in (ContentType.DEFINITION, ContentType.CONCEPT, ContentType.THEORY, ContentType.FORMULA):
                importance = IntrinsicImportance.FOUNDATIONAL
            elif c_type in (ContentType.PROCEDURE, ContentType.METHOD, ContentType.PROBLEM, ContentType.OBJECTIVE):
                importance = IntrinsicImportance.CENTRAL
            elif c_type in (ContentType.BACKGROUND, ContentType.CONTEXT, ContentType.TIP):
                importance = IntrinsicImportance.CONTEXTUAL

            title = cand.parent_section_title or c_type.value.replace("_", " ").title()
            if len(cand.raw_content) < 60:
                title = f"{title}: {cand.raw_content[:40]}"

            unit = KnowledgeUnit(
                id=stable_id,
                title=title,
                content_type=c_type,
                category=category,
                intrinsic_importance=importance,
                provenance=cand.provenance,
                secondary_provenances=[],
                payload=payload,
                classification_confidence=ru.final_confidence,
                resolution_status=ru.resolution_status,
                tags=list(cand.heading_path),
            )
            units.append(unit)
            unit_map[stable_id] = unit

        return units

    def _build_payload(self, text: str, c_type: ContentType, section_title: str) -> KnowledgePayloadUnion:
        if c_type == ContentType.FORMULA or "$$" in text:
            # Extract equation
            eq_match = re.search(r"\$\$(.*?)\$\$", text, re.DOTALL)
            latex_eq = eq_match.group(1).strip() if eq_match else text

            # Extract variables if present (e.g. Q = m . c . dT)
            vars_list: List[VariableDefinition] = []
            if "Q" in latex_eq:
                vars_list.append(VariableDefinition(symbol="Q", name="Kalor", unit="J"))
            if "m" in latex_eq:
                vars_list.append(VariableDefinition(symbol="m", name="Massa", unit="kg"))
            if "c" in latex_eq:
                vars_list.append(VariableDefinition(symbol="c", name="Kapasitas Kalor Jenis", unit="J/g°C"))

            return FormalPayload(
                latex_equation=latex_eq,
                variables=vars_list,
            )

        elif c_type in (ContentType.PROCEDURE, ContentType.METHOD, ContentType.PROCESS, ContentType.SEQUENCE, ContentType.INSTRUCTION):
            steps: List[ProcedureStep] = []
            lines = text.splitlines()
            step_idx = 0
            for line in lines:
                m = re.match(r"^\s*\d+[\.\)]\s+(.*)", line)
                if m:
                    step_idx += 1
                    steps.append(ProcedureStep(step_number=step_idx, action=m.group(1).strip()))

            if not steps:
                steps.append(ProcedureStep(step_number=1, action=text))

            return ProcedurePayload(
                objective=section_title or "Prosedur Kerja",
                steps=steps,
                safety_level="warning" if "k3" in text.lower() or "bahaya" in text.lower() else "standard",
            )

        elif c_type in (ContentType.EVIDENCE, ContentType.DATA, ContentType.RESULT, ContentType.FINDING):
            # Check if text contains table or numeric values
            has_numbers = bool(re.search(r"\d+\.\d+", text))
            if has_numbers:
                nums: dict[str, float] = {}
                for m in re.finditer(r"([a-zA-Z_\s]+)[:=]\s*(\d+(?:\.\d+)?)", text):
                    nums[m.group(1).strip()] = float(m.group(2))

                quant = QuantitativeEvidenceData(numeric_values=nums) if nums else None
                return EvidencePayload(
                    evidence_type=EvidenceType.MEASUREMENT if nums else EvidenceType.OBSERVATION,
                    statement=text[:200],
                    quantitative_data=quant,
                    qualitative_data=QualitativeEvidenceData(observed_phenomenon=section_title, textual_findings=text),
                )
            else:
                return EvidencePayload(
                    evidence_type=EvidenceType.QUALITATIVE_ANALYSIS,
                    statement=text[:200],
                    qualitative_data=QualitativeEvidenceData(observed_phenomenon=section_title, textual_findings=text),
                )

        elif c_type in (ContentType.ARGUMENT, ContentType.ANALYSIS, ContentType.DISCUSSION, ContentType.CONCLUSION, ContentType.LIMITATION):
            return ArgumentPayload(
                claim_statement=text[:150],
                reasoning=text,
            )

        elif c_type in (ContentType.QUESTION, ContentType.WARNING, ContentType.REFLECTION, ContentType.PROBLEM, ContentType.HYPOTHESIS):
            return PedagogicalPayload(
                prompt_type=c_type.value.upper(),
                correct_explanation=text if c_type != ContentType.QUESTION else None,
                hint=f"Review section {section_title}" if section_title else None,
            )

        else:
            # Default ConceptPayload
            return ConceptPayload(
                formal_definition=text,
                intuitive_explanation=text[:120] if len(text) > 120 else text,
            )
