"""
Convergence and Oscillation Detector: Identifies improvement plateaus, oscillations, and termination states.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any
from app.refinement.contracts import ImprovementDecision, RefinementCandidate


class ConvergenceDetector:
    """Detects convergence plateaus, state oscillations (A -> B -> A), and cycles."""

    @classmethod
    def compute_state_fingerprint(cls, candidate: RefinementCandidate) -> str:
        """Computes structural & diagnostic hash of candidate state."""
        bundle = candidate.artifact_bundle
        q_score = candidate.quality_report.overall_score if candidate.quality_report else 0.0
        findings = [f.id for f in (candidate.critique_report.findings if candidate.critique_report else [])]
        page_count = len(bundle.composition.pages) if bundle.composition else 0

        payload = {
            "score": round(q_score, 2),
            "findings": sorted(findings),
            "page_count": page_count,
        }
        raw_str = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()[:12]

    @classmethod
    def check_convergence(
        cls,
        history_fingerprints: list[str],
        history_scores: list[float],
        current_fingerprint: str,
        current_score: float,
    ) -> ImprovementDecision | None:
        # 1. Oscillation Check: Current fingerprint previously seen in history
        if current_fingerprint in history_fingerprints:
            return ImprovementDecision.STOP_OSCILLATION

        # 2. Convergence Plateau Check: Last 2 score deltas < 0.005
        if len(history_scores) >= 2:
            last_delta = abs(current_score - history_scores[-1])
            prev_delta = abs(history_scores[-1] - history_scores[-2])
            if last_delta < 0.005 and prev_delta < 0.005:
                return ImprovementDecision.STOP_CONVERGED

        return None
