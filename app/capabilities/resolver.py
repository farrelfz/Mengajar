"""
KIR AI Document Intelligence — Library Resolver V2.

Determines which registered capability fulfills each production requirement
in a deterministic, ranked manner based on universal Capability Grammar,
multi-axis taxonomy, domain affinity, format compatibility, and density.
"""

from __future__ import annotations

import logging
from typing import Any
from pydantic import BaseModel, Field

from app.capabilities.contracts import Capability
from app.capabilities.registry import CapabilityRegistry
from app.capabilities.taxonomy import (
    CapabilityFamily,
    DensityProfile,
    InformationStructure,
    PedagogicalRole,
    SemanticIntent,
    VisualGrammar,
)
from app.blueprints.production import ProductionBlueprint, ProductionRequirement
from app.blueprints.content import ContentBlueprint

log = logging.getLogger(__name__)


class ScoreBreakdown(BaseModel):
    """Inspectable breakdown of the multi-axis resolution score."""
    intent_score: float = 0.0
    structure_score: float = 0.0
    pedagogical_role_score: float = 0.0
    visual_grammar_score: float = 0.0
    domain_score: float = 0.0
    format_score: float = 0.0
    density_score: float = 0.0
    tag_score: float = 0.0
    family_score: float = 0.0
    total_score: float = 0.0
    matched_dimensions: list[str] = Field(default_factory=list)


class ResolutionCandidate(BaseModel):
    """Detailed candidate record in resolution trace."""
    capability_id: str
    display_name: str
    category: str
    family: str
    score: float
    breakdown: ScoreBreakdown = Field(default_factory=ScoreBreakdown)
    reason: str


class ResolutionResult(BaseModel):
    """Resolution outcome for a specific pedagogical/production step."""
    step_id: str
    semantic_type: str
    selected_capability_id: str
    score: float
    is_fallback: bool = False
    family: str | None = None
    template_selected: str | None = None
    family_candidates: list[str] = Field(default_factory=list)
    candidates: list[ResolutionCandidate] = Field(default_factory=list)
    resolved_parameters: dict[str, Any] = Field(default_factory=dict)
    breakdown: ScoreBreakdown = Field(default_factory=ScoreBreakdown)


class ResolutionPlan(BaseModel):
    """Complete resolution plan and trace across all material steps."""
    step_resolutions: list[ResolutionResult] = Field(default_factory=list)
    trace_log: dict[str, Any] = Field(default_factory=dict)

    def get_resolution(self, step_id: str) -> ResolutionResult | None:
        for r in self.step_resolutions:
            if r.step_id == step_id:
                return r
        return None


class LibraryResolver:
    """Deterministic Resolver V2 matching production requirements against Capability Grammar."""

    def __init__(self, registry: CapabilityRegistry | None = None) -> None:
        self.registry = registry or CapabilityRegistry.get_instance()

    def resolve(
        self,
        production_blueprint: ProductionBlueprint,
        content_blueprint: ContentBlueprint | None = None,
        target_format_id: str | None = None,
    ) -> dict[str, ResolutionResult]:
        """Resolve all production requirements into concrete capabilities."""
        results: dict[str, ResolutionResult] = {}
        artifact_type = production_blueprint.target_artifact.value
        fmt_id = target_format_id or production_blueprint.target_format

        for req in production_blueprint.requirements:
            res = self._resolve_requirement(req, artifact_type, content_blueprint, fmt_id)
            results[req.step_id] = res

        return results

    def resolve_material_plan(
        self,
        production_blueprint: ProductionBlueprint,
        content_blueprint: ContentBlueprint | None = None,
        target_format_id: str | None = None,
    ) -> ResolutionPlan:
        """Resolve full material plan with structured traces."""
        res_map = self.resolve(production_blueprint, content_blueprint, target_format_id)
        resolutions = list(res_map.values())
        return ResolutionPlan(
            step_resolutions=resolutions,
            trace_log={
                "total_steps": len(resolutions),
                "target_artifact": production_blueprint.target_artifact.value,
                "target_format": target_format_id or production_blueprint.target_format,
            },
        )

    def _resolve_requirement(
        self,
        req: ProductionRequirement,
        artifact_type: str,
        content_blueprint: ContentBlueprint | None,
        target_format_id: str | None,
    ) -> ResolutionResult:
        # 1. Direct explicit capability ID match
        if req.required_capability_id:
            direct_cap = self.registry.get(req.required_capability_id)
            if direct_cap:
                bd = ScoreBreakdown(
                    intent_score=30.0,
                    structure_score=25.0,
                    pedagogical_role_score=20.0,
                    visual_grammar_score=15.0,
                    domain_score=10.0,
                    total_score=100.0,
                    matched_dimensions=["explicit_capability_override"],
                )
                cand = ResolutionCandidate(
                    capability_id=direct_cap.metadata.capability_id,
                    display_name=direct_cap.metadata.display_name,
                    category=direct_cap.metadata.category,
                    family=direct_cap.metadata.family.value,
                    score=100.0,
                    breakdown=bd,
                    reason="Direct explicit capability requested",
                )
                tpl = getattr(getattr(direct_cap, "renderer", None), "template", None)
                tpl_id = getattr(tpl, "template_id", None)
                return ResolutionResult(
                    step_id=req.step_id,
                    semantic_type=req.semantic_type,
                    selected_capability_id=direct_cap.metadata.capability_id,
                    score=100.0,
                    is_fallback=False,
                    family=direct_cap.metadata.family.value,
                    template_selected=tpl_id,
                    family_candidates=[direct_cap.metadata.family.value],
                    candidates=[cand],
                    breakdown=bd,
                    resolved_parameters=req.semantic_intent.parameters if req.semantic_intent else {},
                )

        # 2. Multi-Axis Semantic Grammar Matching & Scoring
        domain = req.semantic_intent.domain if req.semantic_intent else None
        intent_str = req.semantic_intent.semantic_intent if req.semantic_intent else req.semantic_type
        
        all_caps = self.registry.list_all()
        scored_candidates: list[tuple[Capability[Any], ScoreBreakdown, str]] = []

        for cap in all_caps:
            reasons: list[str] = []
            matched_dims: list[str] = []
            breakdown = ScoreBreakdown()

            # A. Check artifact compatibility (Hard Filter)
            is_compat = (
                "all" in cap.metadata.supported_artifacts
                or artifact_type in cap.metadata.supported_artifacts
                or any(sup in artifact_type or artifact_type in sup for sup in cap.metadata.supported_artifacts)
            )
            if not is_compat:
                continue

            has_semantic_affinity = False

            # B. Semantic Intent Match (+30)
            if cap.metadata.primary_intent.value in intent_str.lower() or intent_str.lower() in cap.metadata.primary_intent.value:
                breakdown.intent_score = 30.0
                has_semantic_affinity = True
                matched_dims.append("semantic_intent")
                reasons.append(f"Intent match ({cap.metadata.primary_intent.value})")
            elif cap.metadata.taxonomy and any(si.value in intent_str.lower() for si in cap.metadata.taxonomy.supported_intents):
                breakdown.intent_score = 25.0
                has_semantic_affinity = True
                matched_dims.append("supported_intent")
                reasons.append("Supported intent match")

            # C. Pedagogical Role Match (+20)
            if cap.metadata.pedagogical_role.value.lower() in intent_str.lower() or intent_str.lower() in cap.metadata.pedagogical_role.value.lower():
                breakdown.pedagogical_role_score = 20.0
                has_semantic_affinity = True
                matched_dims.append("pedagogical_role")
                reasons.append(f"Pedagogical role match ({cap.metadata.pedagogical_role.value})")

            # D. Category / Semantic Type Affinity (+15)
            if req.semantic_type.lower() in cap.metadata.category.lower() or cap.metadata.category.lower() in req.semantic_type.lower():
                breakdown.structure_score = 15.0
                has_semantic_affinity = True
                matched_dims.append("semantic_category")
                reasons.append(f"Category affinity ({cap.metadata.category})")

            # E. Semantic Tag Matches (+10 per tag)
            intent_tokens = set(intent_str.lower().replace("_", " ").replace("-", " ").split())
            cap_tags = {t.lower() for t in cap.metadata.semantic_tags}
            matched_tags = (intent_tokens & cap_tags) | {t for t in cap_tags if t.replace("_", " ") in intent_str.lower().replace("_", " ")}
            if matched_tags:
                tag_pts = min(len(matched_tags) * 15.0, 30.0)
                breakdown.tag_score = tag_pts
                has_semantic_affinity = True
                matched_dims.append("tags")
                reasons.append(f"Tags matched: {', '.join(matched_tags)}")

            # E. String Containment in ID (+10)
            if intent_str.lower() in cap.metadata.capability_id.lower():
                breakdown.visual_grammar_score = 10.0
                has_semantic_affinity = True
                matched_dims.append("id_substring")
                reasons.append("Capability ID match")

            # Only proceed if there is fundamental semantic affinity
            if has_semantic_affinity:
                # F. Domain Match (+20 for exact, +5 for general)
                if domain and cap.metadata.domain == domain:
                    breakdown.domain_score = 20.0
                    matched_dims.append("domain_exact")
                    reasons.append(f"Domain match ({domain})")
                elif cap.metadata.domain == "general":
                    breakdown.domain_score = 5.0

                # G. Format Preference Match (+10)
                if target_format_id and cap.metadata.taxonomy:
                    if target_format_id in cap.metadata.taxonomy.preferred_formats:
                        breakdown.format_score = 10.0
                        matched_dims.append("format_preference")
                        reasons.append(f"Preferred format ({target_format_id})")

                # H. Density Suitability (+5)
                if req.density_hint and req.density_hint.lower() == cap.metadata.density.value.lower():
                    breakdown.density_score = 5.0
                    matched_dims.append("density_match")
                    reasons.append(f"Density match ({cap.metadata.density.value})")

                total = (
                    breakdown.intent_score
                    + breakdown.structure_score
                    + breakdown.pedagogical_role_score
                    + breakdown.visual_grammar_score
                    + breakdown.domain_score
                    + breakdown.format_score
                    + breakdown.density_score
                    + breakdown.tag_score
                )
                breakdown.total_score = total
                breakdown.matched_dimensions = matched_dims
                scored_candidates.append((cap, breakdown, "; ".join(reasons)))

        # Sort descending by total score, then alphabetically by capability ID for 100% deterministic tie-breaking
        scored_candidates.sort(key=lambda x: (-x[1].total_score, x[0].metadata.capability_id))

        if scored_candidates:
            top_cap, top_breakdown, top_reason = scored_candidates[0]
            candidates_list = [
                ResolutionCandidate(
                    capability_id=c.metadata.capability_id,
                    display_name=c.metadata.display_name,
                    category=c.metadata.category,
                    family=c.metadata.family.value,
                    score=bd.total_score,
                    breakdown=bd,
                    reason=r,
                )
                for c, bd, r in scored_candidates[:5]
            ]
            tpl = getattr(getattr(top_cap, "renderer", None), "template", None)
            tpl_id = getattr(tpl, "template_id", None)
            fam_cands = list({cand.family for cand in candidates_list})
            return ResolutionResult(
                step_id=req.step_id,
                semantic_type=req.semantic_type,
                selected_capability_id=top_cap.metadata.capability_id,
                score=top_breakdown.total_score,
                is_fallback=False,
                family=top_cap.metadata.family.value,
                template_selected=tpl_id,
                family_candidates=fam_cands,
                candidates=candidates_list,
                breakdown=top_breakdown,
                resolved_parameters=req.semantic_intent.parameters if req.semantic_intent else {},
            )

        # 3. Fallback to generic concept introduction
        fallback_cap_id = "presentation.concept_introduction"
        fb_cap = self.registry.get(fallback_cap_id)
        fb_breakdown = ScoreBreakdown(total_score=10.0, matched_dimensions=["system_fallback"])
        return ResolutionResult(
            step_id=req.step_id,
            semantic_type=req.semantic_type,
            selected_capability_id=fallback_cap_id,
            score=10.0,
            is_fallback=True,
            family=CapabilityFamily.CONCEPT_STRUCTURE.value,
            template_selected=None,
            family_candidates=[CapabilityFamily.CONCEPT_STRUCTURE.value],
            candidates=[
                ResolutionCandidate(
                    capability_id=fallback_cap_id,
                    display_name=fb_cap.metadata.display_name if fb_cap else "Concept Introduction",
                    category="presentation",
                    family=CapabilityFamily.CONCEPT_STRUCTURE.value,
                    score=10.0,
                    breakdown=fb_breakdown,
                    reason="Default fallback capability",
                )
            ],
            breakdown=fb_breakdown,
            resolved_parameters=req.semantic_intent.parameters if req.semantic_intent else {},
        )
