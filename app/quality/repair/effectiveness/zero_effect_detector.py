"""
Universal Document Intelligence System V5 — Zero-Effect Mutation Detector & Domain Fingerprints.

Phase 3D.1: Explicitly detects mutations that execute and alter low-level markup or CSS,
but fail to modify the targeted semantic domain fingerprint or resolve the targeted defect.
"""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any, Dict, List, Optional, Sequence, Tuple
from pydantic import BaseModel, ConfigDict

logger = logging.getLogger("quality.repair.zero_effect")


class DomainFingerprint(BaseModel):
    """Immutable multidimensional fingerprint of an artifact's semantic and structural state."""
    model_config = ConfigDict(frozen=True)

    artifact_type: str
    structural_hash: str
    semantic_hash: str
    component_signatures: Dict[str, str] = {}
    composite_hash: str


class DomainFingerprinter:
    """Computes format-specific domain fingerprints for all four artifact types."""

    @classmethod
    def fingerprint(cls, artifact_type: str, blueprint: Any) -> DomainFingerprint:
        """Dispatches to the format-specific fingerprinter."""
        norm_art = artifact_type.strip().upper()
        if norm_art == "PRESENTATION":
            return cls._fingerprint_presentation(blueprint)
        elif norm_art == "WORKSHEET":
            return cls._fingerprint_worksheet(blueprint)
        elif norm_art == "SCIENTIFIC_DOCUMENT":
            return cls._fingerprint_scientific(blueprint)
        elif norm_art == "HANDOUT":
            return cls._fingerprint_handout(blueprint)
        else:
            return cls._fingerprint_generic(blueprint, norm_art)

    @classmethod
    def _fingerprint_presentation(cls, bp: Any) -> DomainFingerprint:
        slides = getattr(bp, "slides", None) or getattr(bp, "beats", None) or []
        slide_signatures = []
        density_signatures = []

        for s in slides:
            title = getattr(s, "title", "")
            layout = getattr(s, "layout", getattr(s, "visual_priority", ""))
            blocks = getattr(s, "key_blocks", ())
            claims = getattr(s, "claim_units", getattr(s, "supporting_unit_ids", ()))
            text_len = len(str(getattr(s, "text", "")))
            slide_signatures.append(f"{title}:{layout}:{len(blocks)}:{len(claims)}")
            density_signatures.append(f"{text_len}")

        struct_raw = "|".join(slide_signatures)
        sem_raw = "|".join(density_signatures)

        struct_hash = hashlib.sha256(struct_raw.encode("utf-8")).hexdigest()[:16]
        sem_hash = hashlib.sha256(sem_raw.encode("utf-8")).hexdigest()[:16]
        comp_hash = hashlib.sha256(f"{struct_hash}:{sem_hash}".encode("utf-8")).hexdigest()[:16]

        return DomainFingerprint(
            artifact_type="PRESENTATION",
            structural_hash=struct_hash,
            semantic_hash=sem_hash,
            component_signatures={
                "slide_grouping": struct_hash,
                "layout_graph": hashlib.sha256("|".join([getattr(s, "layout", "") for s in slides]).encode()).hexdigest()[:16],
                "cognitive_density": sem_hash,
            },
            composite_hash=comp_hash,
        )

    @classmethod
    def _fingerprint_worksheet(cls, bp: Any) -> DomainFingerprint:
        activities = getattr(bp, "activities", ()) or []
        act_signatures = []
        workspace_signatures = []

        for a in activities:
            aid = getattr(a, "activity_id", "")
            atype = str(getattr(a, "activity_type", ""))
            scaffolding = getattr(a, "scaffolding_level", "")
            prompt = getattr(a, "prompt_text", "")
            withhold = getattr(a, "withhold_explanation", False)
            act_signatures.append(f"{aid}:{atype}:{scaffolding}:{withhold}")
            workspace_signatures.append(f"{len(prompt)}:{getattr(a, 'workspace_lines', 0)}")

        struct_raw = "|".join(act_signatures)
        sem_raw = "|".join(workspace_signatures)

        struct_hash = hashlib.sha256(struct_raw.encode("utf-8")).hexdigest()[:16]
        sem_hash = hashlib.sha256(sem_raw.encode("utf-8")).hexdigest()[:16]
        comp_hash = hashlib.sha256(f"{struct_hash}:{sem_hash}".encode("utf-8")).hexdigest()[:16]

        return DomainFingerprint(
            artifact_type="WORKSHEET",
            structural_hash=struct_hash,
            semantic_hash=sem_hash,
            component_signatures={
                "inquiry_sequence": hashlib.sha256("|".join([str(getattr(a, "activity_type", "")) for a in activities]).encode()).hexdigest()[:16],
                "activity_signatures": struct_hash,
                "workspace_allocation": sem_hash,
            },
            composite_hash=comp_hash,
        )

    @classmethod
    def _fingerprint_scientific(cls, bp: Any) -> DomainFingerprint:
        arguments = getattr(bp, "arguments", ()) or []
        sections = getattr(bp, "sections", ()) or []
        refs = getattr(bp, "references", ()) or getattr(bp, "bibliography", ()) or []

        arg_signatures = []
        for a in arguments:
            aid = getattr(a, "argument_id", "")
            role = str(getattr(a, "argument_role", ""))
            cid = getattr(a, "claim_unit_id", "")
            ev_ids = sorted(list(getattr(a, "supporting_evidence_unit_ids", ())))
            arg_signatures.append(f"{aid}:{role}:{cid}:{','.join(ev_ids)}")

        struct_raw = "|".join(arg_signatures)
        sem_raw = "|".join([str(r) for r in refs]) + f":sections={len(sections)}"

        struct_hash = hashlib.sha256(struct_raw.encode("utf-8")).hexdigest()[:16]
        sem_hash = hashlib.sha256(sem_raw.encode("utf-8")).hexdigest()[:16]
        comp_hash = hashlib.sha256(f"{struct_hash}:{sem_hash}".encode("utf-8")).hexdigest()[:16]

        return DomainFingerprint(
            artifact_type="SCIENTIFIC_DOCUMENT",
            structural_hash=struct_hash,
            semantic_hash=sem_hash,
            component_signatures={
                "claim_evidence_graph": struct_hash,
                "citation_anchor_graph": hashlib.sha256(str(refs).encode()).hexdigest()[:16],
                "section_hierarchy": hashlib.sha256(str([getattr(s, "title", "") for s in sections]).encode()).hexdigest()[:16],
            },
            composite_hash=comp_hash,
        )

    @classmethod
    def _fingerprint_handout(cls, bp: Any) -> DomainFingerprint:
        sections = getattr(bp, "sections", ()) or []
        sec_signatures = []
        for s in sections:
            stitle = getattr(s, "title", "")
            blocks = getattr(s, "blocks", ()) or getattr(s, "content_blocks", ()) or []
            sec_signatures.append(f"{stitle}:{len(blocks)}")

        struct_raw = "|".join(sec_signatures)
        struct_hash = hashlib.sha256(struct_raw.encode("utf-8")).hexdigest()[:16]
        sem_hash = hashlib.sha256(f"sec_count={len(sections)}".encode("utf-8")).hexdigest()[:16]
        comp_hash = hashlib.sha256(f"{struct_hash}:{sem_hash}".encode("utf-8")).hexdigest()[:16]

        return DomainFingerprint(
            artifact_type="HANDOUT",
            structural_hash=struct_hash,
            semantic_hash=sem_hash,
            component_signatures={
                "section_hierarchy": struct_hash,
                "paragraph_flow": sem_hash,
                "pagination_structure": comp_hash,
            },
            composite_hash=comp_hash,
        )

    @classmethod
    def _fingerprint_generic(cls, bp: Any, artifact_type: str) -> DomainFingerprint:
        raw = repr(bp)
        h = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
        return DomainFingerprint(
            artifact_type=artifact_type,
            structural_hash=h,
            semantic_hash=h,
            component_signatures={"raw": h},
            composite_hash=h,
        )


class ZeroEffectMutationDetector:
    """Evaluates whether a committed mutation was functionally zero-effect."""

    @classmethod
    def detect_zero_effect(
        cls,
        pre_fingerprint: DomainFingerprint,
        post_fingerprint: DomainFingerprint,
        pre_state_hash: str,
        post_state_hash: str,
        pre_findings: Sequence[str],
        post_findings: Sequence[str],
        targeted_finding_codes: Sequence[str] = (),
    ) -> Tuple[bool, str]:
        """
        Determines if a mutation was zero-effect:
        1. State hash unchanged
        2. Domain fingerprint unchanged
        3. Targeted finding signature remained 100% identical despite mutation execution
        """
        # Condition A: Document state hash completely unchanged
        if pre_state_hash == post_state_hash:
            return True, "Committed mutation produced byte-identical document state hash."

        # Condition B: Target domain fingerprint completely unchanged
        if pre_fingerprint.composite_hash == post_fingerprint.composite_hash:
            return True, (
                f"Mutation modified rendered state but targeted domain fingerprint "
                f"({pre_fingerprint.artifact_type}) remained unchanged."
            )

        # Condition C: Targeted findings remained completely unaffected
        targeted_set = set(targeted_finding_codes)
        if targeted_set:
            pre_targeted = set(pre_findings).intersection(targeted_set)
            post_targeted = set(post_findings).intersection(targeted_set)
            if pre_targeted and pre_targeted == post_targeted:
                # Targeted findings did not change at all
                return True, (
                    f"Mutation modified peripheral layout, but targeted findings "
                    f"{sorted(list(pre_targeted))} remained 100% unresolved."
                )

        return False, "Mutation produced verifiable domain and defect changes."
