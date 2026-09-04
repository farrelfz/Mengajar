"""
Adversarial Case A: Empty structure and zero-page composition detection.
"""

import pytest

from app.composition.schemas import DocumentComposition
from app.intelligence.schemas import DocumentMode
from app.quality.contracts import QualityGateDecision, QualitySeverity
from app.quality.engine import QualityEvaluationEngine
from app.quality.structural_evaluator import StructuralEvaluator


def test_empty_composition_triggers_critical_and_gate_fail():
    # Construct completely empty composition
    empty_comp = DocumentComposition(
        document_id="doc_empty",
        title="Empty Document",
        mode=DocumentMode.A4_PORTRAIT,
        theme_reference="default",
        source_blueprint_id="bp_empty",
        pages=[],
    )

    metrics, findings = StructuralEvaluator.evaluate(composition=empty_comp)

    assert len(findings) >= 1
    assert any(f.severity == QualitySeverity.CRITICAL for f in findings)
    assert any("zero pages" in f.finding.lower() for f in findings)

    # Evaluate through full engine
    report = QualityEvaluationEngine.evaluate_artifact(
        job_id="job_empty_struct",
        composition=empty_comp,
        target_format="a4_portrait",
    )

    assert report.gate_result.decision == QualityGateDecision.FAIL
    assert report.gate_result.can_proceed is False
    assert any(f.severity == QualitySeverity.CRITICAL for f in report.findings)
