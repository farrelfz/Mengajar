"""
Universal Document Intelligence System V5 — Review Intake Router.

Phase 6: Ingests review cases from production quality halts, convergence
reports, and benchmark regressions into normalized ReviewCase instances.
"""

from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from app.review.contracts.enums import (
    ReviewState,
    ReviewTrigger,
    ReviewabilityStatus,
    ReviewerCapability,
)
from app.review.contracts.review_case import ReviewCase
from app.review.intake.reviewability import ReviewabilityClassifier


class ReviewIntakeRouter:
    """Creates ReviewCase instances from diverse system failure channels."""

    @classmethod
    def determine_capabilities(
        cls, artifact_type: str, findings: Sequence[Dict[str, Any]]
    ) -> Tuple[ReviewerCapability, ...]:
        """Maps artifact format and finding types to required expert capabilities."""
        caps: List[ReviewerCapability] = []
        fmt = artifact_type.upper()

        if fmt == "PRESENTATION":
            caps.extend([ReviewerCapability.DOCUMENT_LAYOUT, ReviewerCapability.VISUAL_DESIGN])
        elif fmt == "HANDOUT":
            caps.extend([ReviewerCapability.PEDAGOGY, ReviewerCapability.DOCUMENT_LAYOUT])
        elif fmt == "WORKSHEET":
            caps.extend([ReviewerCapability.INQUIRY_LEARNING, ReviewerCapability.PEDAGOGY])
        elif fmt in ("SCIENTIFIC_DOCUMENT", "KTI"):
            caps.extend([ReviewerCapability.SCIENTIFIC_WRITING, ReviewerCapability.CITATION_FORENSICS])

        # Check finding specific tags
        for f in findings:
            msg = str(f.get("message", "")).lower()
            code = str(f.get("failure_code", "")).lower()
            if "physics" in msg or "force" in msg or "velocity" in msg:
                if ReviewerCapability.PHYSICS_EDUCATION not in caps:
                    caps.append(ReviewerCapability.PHYSICS_EDUCATION)
            if "citation" in msg or "citation" in code or "reference" in msg:
                if ReviewerCapability.CITATION_FORENSICS not in caps:
                    caps.append(ReviewerCapability.CITATION_FORENSICS)
            if "spoiling" in msg or "answer" in msg or "inquiry" in code:
                if ReviewerCapability.INQUIRY_LEARNING not in caps:
                    caps.append(ReviewerCapability.INQUIRY_LEARNING)

        return tuple(caps)

    @classmethod
    def ingest_case(
        cls,
        artifact_id: str,
        artifact_type: str,
        trigger: ReviewTrigger,
        job_id: str = "",
        findings: Sequence[Dict[str, Any]] = (),
        hard_blockers: Sequence[str] = (),
        has_render_artifacts: bool = True,
        is_regression: bool = False,
        artifact_digest: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ReviewCase:
        """Constructs a normalized ReviewCase with reviewability classification."""
        if not artifact_digest:
            # Deterministic fallback digest
            raw = f"{artifact_id}:{artifact_type}:{trigger.value}:{job_id}"
            artifact_digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()

        reviewability, reason = ReviewabilityClassifier.classify(
            findings=findings,
            has_render_artifacts=has_render_artifacts,
            is_regression=is_regression,
        )

        caps = cls.determine_capabilities(artifact_type, findings)

        # Baseline priority computation
        p_score = 0.5
        if hard_blockers:
            p_score = min(1.0, p_score + 0.3)
        if is_regression:
            p_score = min(1.0, p_score + 0.2)
        if trigger == ReviewTrigger.CONVERGENCE_FAILURE:
            p_score = min(1.0, p_score + 0.15)

        initial_state = ReviewState.OPEN
        if reviewability in (ReviewabilityStatus.AUTO_RESOLVABLE, ReviewabilityStatus.NON_REVIEWABLE):
            initial_state = ReviewState.CLOSED_NO_ACTION

        meta = dict(metadata or {})
        meta["reviewability_rationale"] = reason
        meta["hard_blocker_count"] = len(hard_blockers)
        meta["finding_count"] = len(findings)

        return ReviewCase(
            artifact_id=artifact_id,
            job_id=job_id,
            artifact_type=artifact_type,
            artifact_digest=artifact_digest,
            trigger=trigger,
            current_state=initial_state,
            priority_score=round(p_score, 3),
            reviewability=reviewability,
            required_capabilities=caps,
            metadata=meta,
        )
