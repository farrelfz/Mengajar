"""
Universal Document Intelligence System V5 — Quality Signal Contract Tests.

Phase 3A.2 Tests 1–8:
- Test 1: QualitySignal immutability
- Test 2: Unique identifier generation
- Test 3: Detection-only boundary invariant
- Test 4: Evidence requirement on BLOCKING / CRITICAL severity
- Test 5: Multi-format QualityLocation serialization
- Test 6: Bounding box and selector coordinates in QualityLocation
- Test 7: EvidenceReference machine-readable structure
- Test 8: QualitySnapshot in-memory serialization and deserialization
"""

import pytest
from pydantic import ValidationError

from app.quality.causal.contracts import (
    QualityLocation,
    QualitySignal,
    QualitySnapshot,
)
from app.quality.causal.provenance import (
    EvidenceReference,
    EvidenceSourceType,
)
from app.quality.causal.taxonomy import (
    CanonicalFailureCode,
    CanonicalFailureDomain,
    CanonicalSeverity,
    DetectionConfidence,
)


def test_01_quality_signal_immutability():
    """Test 1: QualitySignal is frozen and rejects attribute mutations."""
    ev = EvidenceReference(
        source_type=EvidenceSourceType.PYMUPDF_GEOMETRY,
        description="Text clipped by viewport",
        measurement="overflow_pt",
        raw_value=12.5,
    )
    sig = QualitySignal(
        source_engine="rendered_quality_engine",
        failure_domain=CanonicalFailureDomain.PHYSICAL_RENDER,
        failure_code=CanonicalFailureCode.TEXT_CLIPPING,
        severity=CanonicalSeverity.MAJOR,
        location=QualityLocation(artifact_type="PRESENTATION", slide_index=3),
        evidence=(ev,),
        description="Text clipping on slide 3",
    )

    with pytest.raises(ValidationError):
        sig.severity = CanonicalSeverity.BLOCKING

    with pytest.raises(ValidationError):
        sig.description = "Mutated description"


def test_02_unique_identifier_generation():
    """Test 2: Automatic generation of distinct unique signal identifiers."""
    ev = EvidenceReference(
        source_type=EvidenceSourceType.RASTER_ANALYSIS,
        description="Low visual entropy",
    )
    sig1 = QualitySignal(
        source_engine="raster_engine",
        failure_domain=CanonicalFailureDomain.STYLE_DESIGN,
        failure_code=CanonicalFailureCode.LAYOUT_MONOTONY,
        severity=CanonicalSeverity.MINOR,
        location=QualityLocation(artifact_type="HANDOUT", page_index=1),
        evidence=(ev,),
    )
    sig2 = QualitySignal(
        source_engine="raster_engine",
        failure_domain=CanonicalFailureDomain.STYLE_DESIGN,
        failure_code=CanonicalFailureCode.LAYOUT_MONOTONY,
        severity=CanonicalSeverity.MINOR,
        location=QualityLocation(artifact_type="HANDOUT", page_index=1),
        evidence=(ev,),
    )

    assert sig1.signal_id.startswith("sig_")
    assert sig2.signal_id.startswith("sig_")
    assert sig1.signal_id != sig2.signal_id


def test_03_detection_only_boundary_invariant():
    """Test 3: QualitySignal rejects causal attribution and repair action fields."""
    ev = EvidenceReference(
        source_type=EvidenceSourceType.PYMUPDF_GEOMETRY,
        description="Collision detected",
    )
    
    # Invariant: QualitySignal cannot contain cause_layer
    with pytest.raises(ValueError, match="detection-only"):
        QualitySignal(
            source_engine="test_engine",
            failure_domain=CanonicalFailureDomain.PHYSICAL_RENDER,
            failure_code=CanonicalFailureCode.ELEMENT_COLLISION,
            severity=CanonicalSeverity.MAJOR,
            location=QualityLocation(artifact_type="PRESENTATION", slide_index=1),
            evidence=(ev,),
            cause_layer="RENDER",  # FORBIDDEN!
        )

    # Invariant: QualitySignal cannot contain repair_action
    with pytest.raises(ValueError, match="detection-only"):
        QualitySignal(
            source_engine="test_engine",
            failure_domain=CanonicalFailureDomain.PHYSICAL_RENDER,
            failure_code=CanonicalFailureCode.ELEMENT_COLLISION,
            severity=CanonicalSeverity.MAJOR,
            location=QualityLocation(artifact_type="PRESENTATION", slide_index=1),
            evidence=(ev,),
            repair_action="CLASS_A_GEOMETRY",  # FORBIDDEN!
        )


def test_04_evidence_requirement_on_blocking_or_critical_severity():
    """Test 4: CRITICAL and BLOCKING signals require non-empty evidence."""
    # CRITICAL with empty evidence raises ValidationError
    with pytest.raises(ValidationError, match="requires non-empty evidence references"):
        QualitySignal(
            source_engine="test_engine",
            failure_domain=CanonicalFailureDomain.PHYSICAL_RENDER,
            failure_code=CanonicalFailureCode.BLANK_PAGE,
            severity=CanonicalSeverity.CRITICAL,
            location=QualityLocation(artifact_type="HANDOUT", page_index=2),
            evidence=(),
        )

    # BLOCKING with empty evidence raises ValidationError
    with pytest.raises(ValidationError, match="requires non-empty evidence references"):
        QualitySignal(
            source_engine="test_engine",
            failure_domain=CanonicalFailureDomain.PHYSICAL_RENDER,
            failure_code=CanonicalFailureCode.BLANK_PAGE,
            severity=CanonicalSeverity.BLOCKING,
            location=QualityLocation(artifact_type="HANDOUT", page_index=2),
            evidence=(),
        )

    # CRITICAL with valid evidence succeeds
    ev = EvidenceReference(
        source_type=EvidenceSourceType.PYMUPDF_GEOMETRY,
        description="Completely blank page",
        measurement="drawable_count",
        raw_value=0,
        threshold=1,
    )
    sig_ok = QualitySignal(
        source_engine="test_engine",
        failure_domain=CanonicalFailureDomain.PHYSICAL_RENDER,
        failure_code=CanonicalFailureCode.BLANK_PAGE,
        severity=CanonicalSeverity.CRITICAL,
        location=QualityLocation(artifact_type="HANDOUT", page_index=2),
        evidence=(ev,),
    )
    assert sig_ok.severity == CanonicalSeverity.CRITICAL
    assert len(sig_ok.evidence) == 1


def test_05_multiformat_quality_location_serialization():
    """Test 5: QualityLocation supports all 4 artifact formats without slide bias."""
    # 1. PRESENTATION
    loc_pres = QualityLocation(artifact_type="PRESENTATION", slide_index=4)
    assert loc_pres.page_indices == (4,)

    # 2. HANDOUT
    loc_hand = QualityLocation(artifact_type="HANDOUT", page_index=2, section_index=1)
    assert loc_hand.page_indices == (2,)

    # 3. WORKSHEET
    loc_work = QualityLocation(artifact_type="WORKSHEET", page_index=1, activity_index=3)
    assert loc_work.activity_index == 3

    # 4. SCIENTIFIC_DOCUMENT
    loc_sci = QualityLocation(
        artifact_type="SCIENTIFIC_DOCUMENT",
        page_index=7,
        chapter_index=3,
        section_index=2,
    )
    assert loc_sci.chapter_index == 3

    # Round-trip serialization
    dumped = loc_sci.model_dump()
    loaded = QualityLocation.model_validate(dumped)
    assert loaded == loc_sci


def test_06_bounding_box_and_selector_coordinates():
    """Test 6: Bounding box validation in QualityLocation."""
    # Valid bounding box
    loc_valid = QualityLocation(
        artifact_type="PRESENTATION",
        slide_index=2,
        element_id="card-1",
        bounding_box=(72.0, 100.0, 250.0, 400.0),
    )
    assert loc_valid.bounding_box == (72.0, 100.0, 250.0, 400.0)

    # Inverted bounding box (x0 > x1) raises ValidationError
    with pytest.raises(ValidationError, match="Invalid bounding box"):
        QualityLocation(
            artifact_type="PRESENTATION",
            slide_index=2,
            bounding_box=(300.0, 100.0, 200.0, 400.0),
        )


def test_07_evidence_reference_machine_readable_structure():
    """Test 7: EvidenceReference machine-readable metrics and threshold structure."""
    ev = EvidenceReference(
        source_type=EvidenceSourceType.PYMUPDF_GEOMETRY,
        description="Overlap detected between card and footer",
        measurement="overlap_area_pt2",
        measurement_unit="pt2",
        raw_value=45.8,
        threshold=0.0,
        comparison_operator=">",
        artifact_path="/tmp/doc.pdf",
        page_or_slide=3,
        element_selector=".slide-card-container",
        bounding_box=(50.0, 50.0, 200.0, 200.0),
        metadata={"colliding_elements": ["card_0", "footer_main"]},
    )
    assert ev.measurement == "overlap_area_pt2"
    assert ev.measurement_unit == "pt2"
    assert ev.raw_value == 45.8
    assert ev.comparison_operator == ">"
    assert ev.source_type == EvidenceSourceType.PYMUPDF_GEOMETRY


def test_08_quality_snapshot_serialization_and_aggregation():
    """Test 8: QualitySnapshot serialization round-trip and domain/severity aggregation."""
    ev = EvidenceReference(
        source_type=EvidenceSourceType.PYMUPDF_GEOMETRY,
        description="Minor spacing gap",
    )
    sig1 = QualitySignal(
        source_engine="engine_a",
        failure_domain=CanonicalFailureDomain.PHYSICAL_RENDER,
        failure_code=CanonicalFailureCode.MARGIN_INCONSISTENCY,
        severity=CanonicalSeverity.MINOR,
        location=QualityLocation(artifact_type="HANDOUT", page_index=1),
        evidence=(ev,),
    )
    sig2 = QualitySignal(
        source_engine="engine_b",
        failure_domain=CanonicalFailureDomain.BLUEPRINT_INTEGRITY,
        failure_code=CanonicalFailureCode.UNRESOLVED_SLOT,
        severity=CanonicalSeverity.MAJOR,
        location=QualityLocation(artifact_type="HANDOUT", page_index=2),
        evidence=(ev,),
    )

    snap = QualitySnapshot.from_signals(
        artifact_type="HANDOUT",
        signals=[sig1, sig2],
        metadata={"build_id": "b123"},
    )

    assert snap.total_signals == 2
    assert snap.domain_breakdown["PHYSICAL_RENDER"] == 1
    assert snap.domain_breakdown["BLUEPRINT_INTEGRITY"] == 1
    assert snap.severity_breakdown["MINOR"] == 1
    assert snap.severity_breakdown["MAJOR"] == 1

    # Round-trip dictionary serialization
    d = snap.to_dict()
    restored = QualitySnapshot.from_dict(d)
    assert restored.snapshot_id == snap.snapshot_id
    assert restored.total_signals == snap.total_signals
    assert restored.domain_breakdown == snap.domain_breakdown
