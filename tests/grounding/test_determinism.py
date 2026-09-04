"""
Unit tests for Grounding Engine determinism across 10 runs.
"""

from pathlib import Path
import pytest
from app.grounding.engine import KnowledgeGroundingEngine
from app.grounding.providers.local_doc import LocalDocumentKnowledgeProvider


def test_grounding_determinism_across_10_runs():
    provider = LocalDocumentKnowledgeProvider("local_phys")
    provider.load_markdown_file(Path("tests/fixtures/grounding/physics_sources.md"), domain="physics")
    engine = KnowledgeGroundingEngine(providers=[provider])

    raw_text = "Torque is defined as rotational analog of force. The formula is tau = r * F sin(theta)."

    reports = [engine.ground_material(raw_text, domain="physics").report for _ in range(10)]

    first = reports[0]
    for idx, rep in enumerate(reports[1:], start=2):
        assert rep.claims_total == first.claims_total, f"Claims count mismatch on run {idx}"
        assert rep.claims_grounded == first.claims_grounded, f"Grounded count mismatch on run {idx}"
        assert rep.score.overall_score == first.score.overall_score, f"Overall score mismatch on run {idx}"
        assert rep.score.coverage == first.score.coverage, f"Coverage score mismatch on run {idx}"
