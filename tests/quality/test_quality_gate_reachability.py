"""
Unit tests proving reachability of all formal Quality Gate states:
1. PASS
2. PASS_WITH_WARNINGS
3. NEEDS_REFINEMENT
4. FAIL
"""

import pytest

from app.quality.contracts import (
    QualityDimension,
    QualityFinding,
    QualityGateDecision,
    QualityLevel,
    QualityMetric,
    QualitySeverity,
)
from app.quality.engine import QualityEvaluationEngine


def test_quality_gate_reaches_all_states():
    # 1. State: PASS
    m_pass = [QualityMetric(name="m1", dimension=QualityDimension.SEMANTIC_CORRECTNESS, score=1.0, weight=1.0)]
    s_pass = QualityEvaluationEngine._compute_quality_score(m_pass)
    g_pass = QualityEvaluationEngine._arbitrate_quality_gate(s_pass, [])
    assert g_pass.decision == QualityGateDecision.PASS
    assert g_pass.can_proceed is True

    # 2. State: PASS_WITH_WARNINGS
    m_warn = [QualityMetric(name="m1", dimension=QualityDimension.SEMANTIC_CORRECTNESS, score=0.88, weight=1.0)]
    s_warn = QualityEvaluationEngine._compute_quality_score(m_warn)
    f_warn = [QualityFinding(dimension=QualityDimension.INFORMATION_DENSITY, severity=QualitySeverity.WARNING, finding="Slight overdensity", recommendation="Recap")]
    g_warn = QualityEvaluationEngine._arbitrate_quality_gate(s_warn, f_warn)
    assert g_warn.decision == QualityGateDecision.PASS_WITH_WARNINGS
    assert g_warn.can_proceed is True

    # 3. State: NEEDS_REFINEMENT (due to ERROR finding or low score < 0.70)
    m_refine = [QualityMetric(name="m1", dimension=QualityDimension.PEDAGOGICAL_ALIGNMENT, score=0.65, weight=1.0)]
    s_refine = QualityEvaluationEngine._compute_quality_score(m_refine)
    f_refine = [QualityFinding(dimension=QualityDimension.PEDAGOGICAL_ALIGNMENT, severity=QualitySeverity.ERROR, finding="Worked example before concept", recommendation="Reorder")]
    g_refine = QualityEvaluationEngine._arbitrate_quality_gate(s_refine, f_refine)
    assert g_refine.decision == QualityGateDecision.NEEDS_REFINEMENT
    assert g_refine.can_proceed is False

    # 4. State: FAIL (due to CRITICAL invariant violation)
    m_fail = [QualityMetric(name="m1", dimension=QualityDimension.FORMAT_INTEGRITY, score=0.0, weight=1.0)]
    s_fail = QualityEvaluationEngine._compute_quality_score(m_fail)
    f_fail = [QualityFinding(dimension=QualityDimension.FORMAT_INTEGRITY, severity=QualitySeverity.CRITICAL, finding="PDF rendering failed / 0 pages", recommendation="Fix HTML")]
    g_fail = QualityEvaluationEngine._arbitrate_quality_gate(s_fail, f_fail)
    assert g_fail.decision == QualityGateDecision.FAIL
    assert g_fail.can_proceed is False
