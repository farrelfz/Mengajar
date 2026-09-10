"""Unit tests for Artifact Drift Detection and Safety Invariants."""

import pytest
from app.quality.repair.contracts import RepairAction, RepairMutationClass, RepairPlan, RepairRiskLevel, RepairTarget
from app.quality.repair.drift_analyzer import ArtifactDriftAnalyzer
from app.quality.repair.safety_invariants import RepairSafetyInvariants


class MockSlide:
    def __init__(self, slide_id, title, content, refs):
        self.slide_id = slide_id
        self.title = title
        self.content = content
        self.source_refs = refs


class MockDeck:
    def __init__(self, slides):
        self.slides = slides


def test_drift_analyzer_clean_identity():
    """Identical pre and post states produce zero drift."""
    deck = MockDeck([MockSlide("s1", "Title", "Content", ["ref1", "ref2"])])
    report = ArtifactDriftAnalyzer.analyze(deck, deck, "PRESENTATION")

    assert report.is_acceptable is True
    assert report.semantic_drift_score == 0.0
    assert report.traceability_drift_score == 0.0
    assert report.overall_drift_score < 0.05


def test_drift_analyzer_catches_traceability_drop():
    """Dropping source references triggers an unacceptable drift violation."""
    pre = MockDeck([MockSlide("s1", "Title", "Content", ["ref1", "ref2", "ref3", "ref4"])])
    post = MockDeck([MockSlide("s1", "Title", "Content", ["ref1"])])  # 75% dropped

    report = ArtifactDriftAnalyzer.analyze(pre, post, "PRESENTATION")
    assert report.is_acceptable is False
    assert report.traceability_drift_score > 0.50
    assert any("Traceability loss" in v for v in report.violations)


def test_safety_invariants_blocks_orphan_traceability():
    """Verifies that traceability loss fails safety invariants."""
    pre = MockDeck([MockSlide("s1", "Title", "Content", ["ref1", "ref2"])])
    post = MockDeck([MockSlide("s1", "Title", "Content", [])])

    plan = RepairPlan(
        root_cause_id="rc_test",
        artifact_type="PRESENTATION",
        actions=(),
        execution_order=(),
        expected_quality_improvement=0.1,
    )
    drift = ArtifactDriftAnalyzer.analyze(pre, post, "PRESENTATION")
    passed, violations = RepairSafetyInvariants.evaluate_all(pre, post, plan, drift, "PRESENTATION")

    assert passed is False
    assert any("Traceability" in v for v in violations)
