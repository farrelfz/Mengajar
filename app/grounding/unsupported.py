"""
Unsupported Claim Detector: Identifies ungrounded high-importance claims while ignoring harmless decorative rhetoric.
"""

from __future__ import annotations

from app.grounding.contracts import Claim, ClaimType, GroundingFinding, GroundingStatus


class UnsupportedClaimDetector:
    """Detects essential claims that lack evidence grounding."""

    @classmethod
    def detect_findings(cls, claims: list[Claim]) -> list[GroundingFinding]:
        findings: list[GroundingFinding] = []

        for c in claims:
            if not c.requires_grounding or c.grounding_status == GroundingStatus.NOT_REQUIRED:
                continue

            if c.grounding_status == GroundingStatus.CONTRADICTED:
                findings.append(
                    GroundingFinding(
                        severity="critical",
                        category="contradiction",
                        message=f"Claim is explicitly contradicted by authoritative evidence: '{c.content}'",
                        claim_id=c.claim_id,
                        recommendation="Review and rectify the factual statement to match source literature.",
                    )
                )
            elif c.grounding_status == GroundingStatus.UNGROUNDED:
                sev = "error" if c.importance >= 0.8 else "warning"
                findings.append(
                    GroundingFinding(
                        severity=sev,
                        category="unsupported_claim",
                        message=f"Foundational {c.claim_type.value} claim lacks evidence grounding: '{c.content}'",
                        claim_id=c.claim_id,
                        recommendation="Provide explicit textbook or literature evidence for this claim.",
                    )
                )
            elif c.grounding_status == GroundingStatus.PARTIALLY_GROUNDED and c.importance >= 0.9:
                findings.append(
                    GroundingFinding(
                        severity="warning",
                        category="partial_support",
                        message=f"High-importance claim only has partial evidence support: '{c.content}'",
                        claim_id=c.claim_id,
                        recommendation="Strengthen evidence source to achieve full grounding support.",
                    )
                )

        return findings
