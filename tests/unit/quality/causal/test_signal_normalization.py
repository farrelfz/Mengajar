"""
Universal Document Intelligence System V5 — Signal Normalization Tests.

Phase 3A.2 Tests 22–27:
- Test 22: CalibrationSignalAdapter normalizes Phase 2C calibration result
- Test 23: RenderedSignalAdapter normalizes Phase 3A physical inspection output
- Test 24: LegacyPresentationGateAdapter normalizes legacy presentation gate findings
- Test 25: FidelitySignalAdapter normalizes Phase 2B fidelity evaluation
- Test 26: Original diagnostic metadata preservation
- Test 27: Immutability of input source object
"""

import copy
import pytest
from pydantic import BaseModel

from app.quality.causal.contracts import QualitySignal
from app.quality.causal.provenance import EvidenceSourceType
from app.quality.causal.signal_normalization import (
    CalibrationSignalAdapter,
    FidelitySignalAdapter,
    LegacyPresentationGateAdapter,
    QualitySignalNormalizer,
    RenderedSignalAdapter,
)
from app.quality.causal.taxonomy import (
    CanonicalFailureCode,
    CanonicalFailureDomain,
    CanonicalSeverity,
)


class MockCalibrationDefect(BaseModel):
    code: str = "LAYOUT_MONOTONY"
    severity: str = "MAJOR"
    affected_pages: list[int] = [1, 2, 3]
    score: float = 0.42
    description: str = "Consecutive card layouts"
    evidence: dict = {"card_count": 4}


class MockRenderDefect(BaseModel):
    code: str = "TEXT_CLIPPING"
    severity: str = "CRITICAL"
    page_indices: list[int] = [2]
    description: str = "Text clipped by 15pt"
    evidence: dict = {"overflow_pt": 15.0, "font_size": 12.0}
    repair_guidance: str = "Reduce font size or enlarge box"


class MockRenderInspection(BaseModel):
    artifact_type: str = "PRESENTATION"
    critical_failures: list[MockRenderDefect] = [MockRenderDefect()]
    major_warnings: list[MockRenderDefect] = []
    minor_warnings: list[MockRenderDefect] = []


def test_22_calibration_signal_adapter():
    """Test 22: CalibrationSignalAdapter translates Phase 2C defect to canonical QualitySignal."""
    defect = MockCalibrationDefect()
    signals = CalibrationSignalAdapter.adapt(defect, artifact_type="HANDOUT")

    assert len(signals) == 1
    sig = signals[0]
    assert isinstance(sig, QualitySignal)
    assert sig.failure_domain == CanonicalFailureDomain.STYLE_DESIGN
    assert sig.failure_code == CanonicalFailureCode.LAYOUT_MONOTONY
    assert sig.severity == CanonicalSeverity.MAJOR
    assert sig.location.page_index == 1
    assert len(sig.evidence) == 1
    assert sig.evidence[0].source_type == EvidenceSourceType.CALIBRATION_METRIC


def test_23_rendered_signal_adapter():
    """Test 23: RenderedSignalAdapter translates Phase 3A inspection to canonical QualitySignal."""
    insp = MockRenderInspection()
    signals = RenderedSignalAdapter.adapt(insp)

    assert len(signals) == 1
    sig = signals[0]
    assert isinstance(sig, QualitySignal)
    assert sig.failure_domain == CanonicalFailureDomain.PHYSICAL_RENDER
    assert sig.failure_code == CanonicalFailureCode.TEXT_CLIPPING
    assert sig.severity == CanonicalSeverity.CRITICAL
    assert sig.location.slide_index == 2
    assert sig.evidence[0].source_type == EvidenceSourceType.PYMUPDF_GEOMETRY


def test_24_legacy_presentation_gate_adapter():
    """Test 24: LegacyPresentationGateAdapter normalizes legacy gate finding."""
    legacy_gate_dict = {
        "findings": [
            {
                "code": "PRESENTATION_RHYTHM_FAILURE",
                "severity": "WARNING",
                "description": "Cadence score below 0.70",
                "score": 0.65,
            }
        ]
    }
    signals = LegacyPresentationGateAdapter.adapt(legacy_gate_dict, artifact_type="PRESENTATION")

    assert len(signals) == 1
    sig = signals[0]
    assert sig.failure_domain == CanonicalFailureDomain.PEDAGOGICAL_STRUCTURE
    assert sig.failure_code == CanonicalFailureCode.PRESENTATION_RHYTHM_FAILURE
    assert sig.evidence[0].source_type == EvidenceSourceType.LEGACY_GATE


def test_25_fidelity_signal_adapter():
    """Test 25: FidelitySignalAdapter normalizes dropped elements and unresolved slots."""
    fidelity_report = {
        "artifact_type": "SCIENTIFIC_DOCUMENT",
        "dropped_source_units": ["sec_methodology_1"],
        "unresolved_slots": ["slot_figure_2"],
    }
    signals = FidelitySignalAdapter.adapt(fidelity_report)

    assert len(signals) == 2
    codes = {s.failure_code for s in signals}
    assert CanonicalFailureCode.TRACEABILITY_BREAK in codes
    assert CanonicalFailureCode.UNRESOLVED_SLOT in codes
    domains = {s.failure_domain for s in signals}
    assert CanonicalFailureDomain.SEMANTIC_TRACEABILITY in domains
    assert CanonicalFailureDomain.BLUEPRINT_INTEGRITY in domains


def test_26_original_diagnostic_metadata_preservation():
    """Test 26: Adapters preserve original failure codes, severities, and metrics in raw_metadata."""
    defect = MockRenderDefect(
        code="TEXT_CLIPPING",
        severity="CRITICAL",
        evidence={"overflow_pt": 20.0},
    )
    insp = MockRenderInspection(critical_failures=[defect])
    signals = RenderedSignalAdapter.adapt(insp)

    assert len(signals) == 1
    raw_meta = signals[0].raw_metadata
    assert raw_meta["original_failure_code"] == "TEXT_CLIPPING"
    assert raw_meta["original_severity"] == "CRITICAL"
    assert raw_meta["adapter"] == "RenderedSignalAdapter"
    assert raw_meta["source_phase"] == "PHASE_3A"
    assert "repair_guidance" in raw_meta


def test_27_immutability_of_input_source_object():
    """Test 27: Normalization adapters do not mutate input objects or their dictionaries."""
    original_dict = {
        "code": "LAYOUT_MONOTONY",
        "severity": "MAJOR",
        "affected_pages": [1, 2, 3],
        "evidence": {"card_count": 4},
    }
    dict_snapshot = copy.deepcopy(original_dict)

    # Adapt
    signals = CalibrationSignalAdapter.adapt(original_dict, artifact_type="HANDOUT")
    assert len(signals) == 1

    # Verify input dictionary was not mutated
    assert original_dict == dict_snapshot
