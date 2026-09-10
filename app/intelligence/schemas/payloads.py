"""
Universal Knowledge Core — Typed Semantic Payload Families.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field


class EvidenceType(str, Enum):
    OBSERVATION = "observation"
    MEASUREMENT = "measurement"
    EXPERIMENTAL_RESULT = "experimental_result"
    LITERATURE = "literature"
    CITATION = "citation"
    COMPARATIVE_EXAMPLE = "comparative_example"
    QUALITATIVE_ANALYSIS = "qualitative_analysis"


# ── 1. Concept Payload ────────────────────────────────────────────────────────
class ConceptPayload(BaseModel):
    kind: Literal["concept"] = "concept"
    concept_name: Optional[str] = None
    formal_definition: str = ""
    summary: Optional[str] = None
    intuitive_explanation: Optional[str] = None
    key_principles: List[str] = Field(default_factory=list)
    underlying_mechanisms: List[str] = Field(default_factory=list)
    symbol: Optional[str] = None
    si_unit: Optional[str] = None


# ── 2. Procedure Payload ──────────────────────────────────────────────────────
class ProcedureStep(BaseModel):
    step_number: int
    action: str
    safety_note: Optional[str] = None
    expected_result: Optional[str] = None


class ProcedurePayload(BaseModel):
    kind: Literal["procedure"] = "procedure"
    objective: str
    apparatus_and_materials: List[str] = Field(default_factory=list)
    steps: List[ProcedureStep] = Field(default_factory=list)
    safety_level: str = "standard"  # standard, warning, K3_critical


# ── 3. Formal Payload ─────────────────────────────────────────────────────────
class VariableDefinition(BaseModel):
    symbol: str
    name: str
    unit: str
    is_constant: bool = False


class FormalPayload(BaseModel):
    kind: Literal["formal"] = "formal"
    latex_equation: str
    variables: List[VariableDefinition] = Field(default_factory=list)
    derivation_notes: Optional[str] = None
    conditions_of_validity: List[str] = Field(default_factory=list)


# ── 4. Evidence Payload (Quantitative & Qualitative) ─────────────────────────
class QuantitativeEvidenceData(BaseModel):
    numeric_values: Dict[str, float] = Field(default_factory=dict)
    units: Dict[str, str] = Field(default_factory=dict)
    uncertainty: Optional[float] = None
    sample_size: Optional[int] = None


class QualitativeEvidenceData(BaseModel):
    observed_phenomenon: str
    textual_findings: str
    context_notes: Optional[str] = None


class EvidenceSourceMetadata(BaseModel):
    citation_key: Optional[str] = None
    authors: List[str] = Field(default_factory=list)
    year: Optional[int] = None
    doi_or_url: Optional[str] = None


class EvidencePayload(BaseModel):
    kind: Literal["evidence"] = "evidence"
    evidence_type: EvidenceType = EvidenceType.QUALITATIVE_ANALYSIS
    statement: str
    supports_claim_ids: List[str] = Field(default_factory=list)
    quantitative_data: Optional[QuantitativeEvidenceData] = None
    qualitative_data: Optional[QualitativeEvidenceData] = None
    source_metadata: Optional[EvidenceSourceMetadata] = None


# ── 5. Argument Payload ───────────────────────────────────────────────────────
class ArgumentPayload(BaseModel):
    kind: Literal["argument"] = "argument"
    claim_statement: str
    reasoning: str
    limitations: List[str] = Field(default_factory=list)
    counterarguments: List[str] = Field(default_factory=list)


# ── 6. Pedagogical Payload ────────────────────────────────────────────────────
class PedagogicalPayload(BaseModel):
    kind: Literal["pedagogical"] = "pedagogical"
    prompt_type: str  # QUESTION, MISCONCEPTION, WARNING, REFLECTION
    misconception_belief: Optional[str] = None
    correct_explanation: Optional[str] = None
    distractor_options: List[str] = Field(default_factory=list)
    hint: Optional[str] = None


# ── Discriminated Union Family ────────────────────────────────────────────────
KnowledgePayloadUnion = Union[
    ConceptPayload,
    ProcedurePayload,
    FormalPayload,
    EvidencePayload,
    ArgumentPayload,
    PedagogicalPayload,
]
