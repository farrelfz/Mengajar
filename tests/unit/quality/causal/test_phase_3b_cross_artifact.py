"""
Universal Document Intelligence System V5 — Phase 3B Cross-Artifact Causal Attribution Tests.

Tests 37 to 43:
- PRESENTATION: Density overload -> capacity exceeded -> text clipping causal path
- PRESENTATION: Repetition streak -> invalid grouping -> narrative monotony streak
- HANDOUT: Wall of text -> content overdensity -> reading flow break
- HANDOUT: Page balance failure -> layout capacity exceeded
- WORKSHEET: Answer leakage -> artifact policy failure (anti-spoiling)
- WORKSHEET: Workspace failure -> layout capacity mismatch
- SCIENTIFIC_DOCUMENT: Invisible citation -> citation structure failure vs render clipping
"""

import pytest
from app.quality.causal.causal_engine import MasterCausalEngine
from app.quality.causal.causal_taxonomy import CausalDecision, RootCauseCategory
from app.quality.causal.contracts import QualityLocation, QualitySignal
from app.quality.causal.provenance import EvidenceReference, EvidenceSourceType
from app.quality.causal.repair_readiness import RepairAuthorityLevel
from app.quality.causal.taxonomy import (
    CanonicalFailureCode,
    CanonicalFailureDomain,
    CanonicalRepairClass,
    CanonicalSeverity,
    FailureScope,
)


def _signal(
    sig_id: str,
    code: CanonicalFailureCode,
    domain: CanonicalFailureDomain,
    artifact_type: str,
    page: int = 1,
    severity: CanonicalSeverity = CanonicalSeverity.MAJOR,
    element_id: str = "elem_main",
    source_units=("unit_main",),
    blueprint_elements=("bp_main",),
    render_elements=("rnd_main",),
) -> QualitySignal:
    ev = ()
    if severity in (CanonicalSeverity.CRITICAL, CanonicalSeverity.BLOCKING):
        ev = (
            EvidenceReference(
                source_type=EvidenceSourceType.PYMUPDF_GEOMETRY,
                description=f"Evidence for critical defect {code.value}",
            ),
        )

    return QualitySignal(
        signal_id=sig_id,
        source_engine="cross_artifact_inspector",
        failure_domain=domain,
        failure_code=code,
        severity=severity,
        evidence=ev,
        location=QualityLocation(
            artifact_type=artifact_type,
            page_index=page,
            element_id=element_id,
            source_unit_ids=tuple(source_units),
            blueprint_element_ids=tuple(blueprint_elements),
            render_element_ids=tuple(render_elements),
        ),
        description=f"{artifact_type} defect {code.value}",
    )


def test_37_presentation_density_capacity_causal_chain():
    """Test 37: PRESENTATION with text clipping and density overload attributes to LAYOUT_CAPACITY_EXCEEDED."""
    engine = MasterCausalEngine()

    s1 = _signal("p_clip", CanonicalFailureCode.TEXT_CLIPPING, CanonicalFailureDomain.PHYSICAL_RENDER, "PRESENTATION")
    s2 = _signal("p_dense", CanonicalFailureCode.DENSITY_OVERLOAD, CanonicalFailureDomain.COGNITIVE_LOAD, "PRESENTATION")
    s3 = _signal("p_small", CanonicalFailureCode.TEXT_TOO_SMALL, CanonicalFailureDomain.PHYSICAL_RENDER, "PRESENTATION")

    result = engine.analyze([s1, s2, s3], total_pages=5, artifact_type="PRESENTATION")

    assert len(result.clusters) == 1
    cluster = result.clusters[0]
    cause = cluster.primary_root_cause

    assert cause is not None
    assert cause.cause_code == RootCauseCategory.LAYOUT_CAPACITY_EXCEEDED.value
    assert "BLUEPRINT" in cause.causal_path
    assert "COMPOSITION" in cause.causal_path
    assert "RENDERING" in cause.causal_path
    assert cluster.recommended_repair_class == CanonicalRepairClass.CLASS_C_LAYOUT_REMAPPING


def test_38_presentation_monotony_streak():
    """Test 38: PRESENTATION with layout monotony and repetition streak attributes to INVALID_GROUPING."""
    engine = MasterCausalEngine()

    s1 = _signal("p_mono", CanonicalFailureCode.LAYOUT_MONOTONY, CanonicalFailureDomain.STYLE_DESIGN, "PRESENTATION")
    s2 = _signal("p_rep", CanonicalFailureCode.REPETITION_STREAK, CanonicalFailureDomain.STYLE_DESIGN, "PRESENTATION")

    result = engine.analyze([s1, s2], total_pages=8, artifact_type="PRESENTATION")

    assert len(result.clusters) == 1
    cause = result.clusters[0].primary_root_cause

    assert cause is not None
    assert cause.cause_code == RootCauseCategory.INVALID_GROUPING.value
    assert result.clusters[0].recommended_repair_class == CanonicalRepairClass.CLASS_D_BLUEPRINT_REGROUPING


def test_39_handout_wall_of_text_content_overdensity():
    """Test 39: HANDOUT with wall of text and density overload attributes to SOURCE_CONTENT overdensity."""
    engine = MasterCausalEngine()

    s1 = _signal("h_wall", CanonicalFailureCode.WALL_OF_TEXT, CanonicalFailureDomain.COGNITIVE_LOAD, "HANDOUT")
    s2 = _signal("h_dense", CanonicalFailureCode.DENSITY_OVERLOAD, CanonicalFailureDomain.COGNITIVE_LOAD, "HANDOUT")

    result = engine.analyze([s1, s2], total_pages=4, artifact_type="HANDOUT")

    assert len(result.clusters) == 1
    cause = result.clusters[0].primary_root_cause

    assert cause is not None
    assert cause.cause_code == RootCauseCategory.CONTENT_OVERDENSITY.value
    assert cause.cause_layer == "SOURCE_CONTENT"


def test_40_handout_page_balance_capacity():
    """Test 40: HANDOUT with page balance failure attributes to LAYOUT_CAPACITY_EXCEEDED."""
    engine = MasterCausalEngine()

    s1 = _signal("h_bal", CanonicalFailureCode.HANDOUT_PAGE_BALANCE_FAILURE, CanonicalFailureDomain.PEDAGOGICAL_STRUCTURE, "HANDOUT")
    s2 = _signal("h_void", CanonicalFailureCode.SUSPICIOUS_VOID, CanonicalFailureDomain.COGNITIVE_LOAD, "HANDOUT")

    result = engine.analyze([s1, s2], total_pages=4, artifact_type="HANDOUT")

    assert len(result.clusters) == 1
    cause = result.clusters[0].primary_root_cause

    assert cause is not None
    assert cause.cause_code == RootCauseCategory.LAYOUT_CAPACITY_EXCEEDED.value


def test_41_worksheet_answer_leakage_anti_spoiling():
    """Test 41: WORKSHEET with spoiling failure attributes to WORKSHEET_ANSWER_LEAKAGE."""
    engine = MasterCausalEngine()

    s1 = _signal("w_spoil", CanonicalFailureCode.WORKSHEET_SPOILING_FAILURE, CanonicalFailureDomain.PEDAGOGICAL_STRUCTURE, "WORKSHEET", severity=CanonicalSeverity.CRITICAL)

    result = engine.analyze([s1], total_pages=2, artifact_type="WORKSHEET")

    assert len(result.clusters) == 1
    cluster = result.clusters[0]
    assert cluster.scope == FailureScope.ARTIFACT_WIDE
    cause = cluster.primary_root_cause

    assert cause is not None
    assert cause.cause_code == RootCauseCategory.WORKSHEET_ANSWER_LEAKAGE.value
    assert cluster.recommended_repair_class == CanonicalRepairClass.CLASS_F_ARTIFACT_POLICY


def test_42_worksheet_workspace_failure():
    """Test 42: WORKSHEET with insufficient workspace attributes to LAYOUT_CAPACITY_EXCEEDED."""
    engine = MasterCausalEngine()

    s1 = _signal("w_work", CanonicalFailureCode.WORKSHEET_WORKSPACE_INSUFFICIENT, CanonicalFailureDomain.PEDAGOGICAL_STRUCTURE, "WORKSHEET")
    s2 = _signal("w_col", CanonicalFailureCode.ELEMENT_COLLISION, CanonicalFailureDomain.PHYSICAL_RENDER, "WORKSHEET")

    result = engine.analyze([s1, s2], total_pages=2, artifact_type="WORKSHEET")

    assert len(result.clusters) == 1
    cause = result.clusters[0].primary_root_cause

    assert cause is not None
    assert cause.cause_code == RootCauseCategory.LAYOUT_CAPACITY_EXCEEDED.value


def test_43_scientific_citation_invisible_distinction():
    """Test 43: SCIENTIFIC_DOCUMENT with invisible citation attributes to CITATION_STRUCTURE_FAILURE, not render bug."""
    engine = MasterCausalEngine()

    s1 = _signal("s_cite", CanonicalFailureCode.SCIENTIFIC_CITATION_INVISIBLE, CanonicalFailureDomain.SCIENTIFIC_RIGOR, "SCIENTIFIC_DOCUMENT", severity=CanonicalSeverity.CRITICAL)
    s2 = _signal("s_disc", CanonicalFailureCode.EVIDENCE_DISCIPLINE_FAILURE, CanonicalFailureDomain.SEMANTIC_TRACEABILITY, "SCIENTIFIC_DOCUMENT")

    result = engine.analyze([s1, s2], total_pages=15, artifact_type="SCIENTIFIC_DOCUMENT")

    assert len(result.clusters) == 1
    cluster = result.clusters[0]
    cause = cluster.primary_root_cause

    assert cause is not None
    assert cause.cause_code == RootCauseCategory.CITATION_STRUCTURE_FAILURE.value
    assert cause.cause_layer == "KNOWLEDGE_MODEL"
    assert cluster.recommended_repair_class == CanonicalRepairClass.CLASS_F_ARTIFACT_POLICY
