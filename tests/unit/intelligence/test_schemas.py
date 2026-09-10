"""
Unit tests for Universal Knowledge Core schemas and payload families.
"""

import pytest
from pydantic import ValidationError

from app.intelligence.schemas import (
    ConceptPayload,
    ProcedureStep,
    ProcedurePayload,
    FormalPayload,
    VariableDefinition,
    EvidenceType,
    QuantitativeEvidenceData,
    QualitativeEvidenceData,
    EvidencePayload,
    ArgumentPayload,
    PedagogicalPayload,
    KnowledgeCategory,
    IntrinsicImportance,
    KnowledgeProvenance,
    KnowledgeUnit,
    RelationshipType,
    RelationshipOrigin,
    RelationshipEvidence,
    KnowledgeRelationship,
    ContentType,
    generate_stable_knowledge_id,
)


def test_concept_payload_valid():
    payload = ConceptPayload(
        formal_definition="Titik nyala adalah suhu terendah...",
        intuitive_explanation="Suhu minimal agar bahan bakar bisa menyala.",
        key_principles=["Transfer kalor", "Kapasitas panas air"],
    )
    assert payload.kind == "concept"
    assert len(payload.key_principles) == 2


def test_procedure_payload_valid():
    step1 = ProcedureStep(step_number=1, action="Beri label 5 tabung reaksi")
    payload = ProcedurePayload(
        objective="Uji Enzim Katalase",
        apparatus_and_materials=["Tabung reaksi", "H2O2 10%"],
        steps=[step1],
    )
    assert payload.kind == "procedure"
    assert payload.steps[0].action == "Beri label 5 tabung reaksi"


def test_formal_payload_valid():
    var_q = VariableDefinition(symbol="Q", name="Kalor", unit="J")
    payload = FormalPayload(
        latex_equation="Q = m \\cdot c \\cdot \\Delta T",
        variables=[var_q],
    )
    assert payload.kind == "formal"
    assert payload.variables[0].symbol == "Q"


def test_evidence_payload_qualitative_and_quantitative():
    qual = QualitativeEvidenceData(
        observed_phenomenon="Nyala bara api terang",
        textual_findings="Oksigen dihasilkan pada konsentrasi 100%",
    )
    quant = QuantitativeEvidenceData(
        numeric_values={"tinggi_gelembung_cm": 9.53},
        units={"tinggi_gelembung_cm": "cm"},
    )
    payload = EvidencePayload(
        evidence_type=EvidenceType.EXPERIMENTAL_RESULT,
        statement="Gelembung oksigen mencapai puncak pada konsentrasi 100%",
        qualitative_data=qual,
        quantitative_data=quant,
    )
    assert payload.kind == "evidence"
    assert payload.evidence_type == EvidenceType.EXPERIMENTAL_RESULT
    assert payload.quantitative_data.numeric_values["tinggi_gelembung_cm"] == 9.53


def test_argument_payload_valid():
    payload = ArgumentPayload(
        claim_statement="Laju pembentukan gas O2 berbanding lurus dengan konsentrasi enzim",
        reasoning="Peningkatan jumlah sisi aktif bebas mempercepat dekomposisi H2O2",
    )
    assert payload.kind == "argument"


def test_pedagogical_payload_valid():
    payload = PedagogicalPayload(
        prompt_type="MISCONCEPTION",
        misconception_belief="Air di dalam busa ikut terbakar",
        correct_explanation="Kalor pembakaran diserap oleh air karena kapasitas kalor tinggi",
    )
    assert payload.kind == "pedagogical"


def test_knowledge_unit_with_provenance():
    prov = KnowledgeProvenance(
        source_document_id="doc_123",
        source_section_id="sec_teori",
        source_section_title="Teori Dasar",
        raw_snippet="Air memiliki kapasitas kalor tinggi.",
    )
    payload = ConceptPayload(formal_definition="Definisi kalor...")
    
    ku_id = generate_stable_knowledge_id("doc_123", "Air memiliki kapasitas kalor tinggi.", ContentType.CONCEPT)
    ku = KnowledgeUnit(
        id=ku_id,
        title="Kapasitas Kalor Air",
        content_type=ContentType.CONCEPT,
        category=KnowledgeCategory.CORE_CONCEPT,
        intrinsic_importance=IntrinsicImportance.FOUNDATIONAL,
        provenance=prov,
        payload=payload,
    )
    assert ku.id.startswith("ku_")
    assert ku.intrinsic_importance == IntrinsicImportance.FOUNDATIONAL
    assert ku.payload.kind == "concept"
