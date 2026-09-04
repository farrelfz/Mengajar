"""
Unit tests for Citation Provenance traceability.
"""

import pytest
from app.grounding.contracts import Claim, ClaimEvidenceLink, Evidence, SupportRelation
from app.grounding.provenance import ProvenanceTracer


def test_provenance_tracer_constructs_machine_readable_path():
    c = Claim(claim_id="c_torque", content="Torque equation", domain="physics")
    ev = Evidence(evidence_id="ev_001", source_id="src_physics_001", content="tau = r * F sin(theta)", domain="physics")
    link = ClaimEvidenceLink(claim_id="c_torque", evidence_id="ev_001", relation=SupportRelation.SUPPORTS)

    provenances = ProvenanceTracer.trace_provenance([c], [link], {"ev_001": ev})

    assert len(provenances) == 1
    assert provenances[0].claim_id == "c_torque"
    assert "ev_001" in provenances[0].evidence_ids
    assert "src_physics_001" in provenances[0].source_ids
    assert "c_torque -> ev_001 -> src_physics_001" in provenances[0].trace_path
