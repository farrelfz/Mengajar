"""
Unit tests for Critic Contracts, Enums, and Serialization models.
"""

import pytest

from app.critic.contracts import (
    CritiqueAgreement,
    CritiqueConfidence,
    CritiqueConflict,
    CritiqueEvidence,
    CritiqueFinding,
    CritiquePerspective,
    CritiquePriority,
    CritiqueRecommendation,
    CritiqueReport,
    CritiqueSeverity,
    CritiqueStatus,
    CritiqueTrace,
    ImplementationScope,
)


def test_critic_enums_and_constants():
    assert CritiquePerspective.STRUCTURAL.value == "structural"
    assert CritiquePerspective.COGNITIVE_LOAD.value == "cognitive_load"
    assert CritiqueSeverity.CRITICAL.value == "critical"
    assert CritiquePriority.BLOCKER.value == "blocker"
    assert ImplementationScope.PAGE.value == "page"


def test_critique_finding_and_report_serialization():
    evidence = CritiqueEvidence(
        source="blueprint",
        location="Stage 1",
        observation="Worked example is first.",
        supporting_data={"index": 0},
        confidence=CritiqueConfidence.HIGH,
    )
    finding = CritiqueFinding(
        id="finding_1",
        perspective=CritiquePerspective.PEDAGOGICAL,
        title="Worked Example Precedes Concept",
        observation="Observation text",
        diagnosis="Diagnosis text",
        why_it_matters="Why it matters text",
        evidence=[evidence],
        severity=CritiqueSeverity.HIGH,
        confidence=CritiqueConfidence.CERTAIN,
        affected_locations=["Stage 1"],
        improvement_direction="Reorder steps",
    )
    rec = CritiqueRecommendation(
        id="rec_1",
        finding_ids=["finding_1"],
        recommendation="Reorder steps",
        rationale="Pedagogical integrity",
        expected_impact="High",
        implementation_scope=ImplementationScope.PAGE,
        priority=CritiquePriority.HIGH,
    )
    report = CritiqueReport(
        artifact_id="art_1",
        overall_assessment="Assessment text",
        findings=[finding],
        recommendations=[rec],
        conflicts=[],
        agreements=[],
        priority_queue=["finding_1"],
        trace=CritiqueTrace(critics_executed=["pedagogical"], evidence_sources=["blueprint"]),
    )

    data = report.model_dump()
    assert data["artifact_id"] == "art_1"
    assert len(data["findings"]) == 1
    assert data["findings"][0]["perspective"] == "pedagogical"
    assert len(data["recommendations"]) == 1
    assert data["recommendations"][0]["priority"] == "high"
