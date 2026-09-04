"""
KIR AI Document Intelligence — Research Problem Formulation Library.

Provides parameterized visual and pedagogical components for research problem design:
- Problem Formulation Funnel (Phenomenon -> Identification -> Scope Limitation -> Research Question)
- Literature Gap & Contribution Matrix
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from app.capabilities.contracts import (
    Capability,
    CapabilityMetadata,
    CapabilityOutput,
    CapabilityRenderer,
    CapabilitySpec,
)
from app.capabilities.taxonomy import (
    CapabilityFamily,
    DensityProfile,
    InformationStructure,
    PedagogicalRole,
    SemanticIntent,
    TaxonomySignature,
    VisualGrammar,
)


class ProblemFunnelLayer(BaseModel):
    layer_name: str
    description: str
    color: str = "#3b82f6"


class ProblemFunnelSpec(CapabilitySpec):
    topic: str = "Research Question Derivation"
    phenomenon: str = "Broad real-world phenomenon or observation"
    problem_identification: str = "Identified discrepancy between ideal and factual conditions"
    scope_limitation: str = "Boundary conditions, specific sample, or target context"
    final_research_question: str = "Specific, answerable, and measurable research question"


class ProblemFunnelRenderer(CapabilityRenderer[ProblemFunnelSpec]):

    def validate_spec(self, spec: ProblemFunnelSpec) -> bool:
        return bool(spec.phenomenon and spec.final_research_question)

    def measure(self, spec: ProblemFunnelSpec, context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"width_px": 750, "height_px": 360}

    def render(self, spec: ProblemFunnelSpec, context: dict[str, Any] | None = None) -> CapabilityOutput:
        width = 750
        height = 360
        
        # 4 trapezoid layers forming a funnel
        layers = [
            ("1. Broad Phenomenon", spec.phenomenon, 600, 480, 50, "#3b82f6"),
            ("2. Problem Identification", spec.problem_identification, 480, 360, 115, "#0284c7"),
            ("3. Scope Limitation", spec.scope_limitation, 360, 240, 180, "#0d9488"),
            ("4. Specific Research Question", spec.final_research_question, 240, 140, 245, "#e11d48"),
        ]

        svg_layers = ""
        cx = width / 2
        for title, desc, top_w, bot_w, top_y, color in layers:
            bot_y = top_y + 55
            x1 = cx - top_w / 2
            x2 = cx + top_w / 2
            x3 = cx + bot_w / 2
            x4 = cx - bot_w / 2

            svg_layers += f"""
            <g>
                <polygon points="{x1},{top_y} {x2},{top_y} {x3},{bot_y} {x4},{bot_y}" fill="{color}" opacity="0.9"/>
                <text x="{cx}" y="{top_y + 20}" font-family="sans-serif" font-size="12" font-weight="bold" fill="#ffffff" text-anchor="middle">{title}</text>
                <text x="{cx}" y="{top_y + 38}" font-family="sans-serif" font-size="10" fill="#f8fafc" text-anchor="middle">{desc[:55]}</text>
            </g>
            """

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">
  <rect x="5" y="5" width="{width-10}" height="{height-10}" rx="12" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.5"/>
  <text x="30" y="35" font-family="sans-serif" font-size="16" font-weight="bold" fill="#0f172a">Problem Formulation Funnel: {spec.topic}</text>
  {svg_layers}
  <!-- Output Arrow & Callout -->
  <line x1="{cx}" y1="305" x2="{cx}" y2="330" stroke="#e11d48" stroke-width="2.5" marker-end="url(#arrow-rq)"/>
  <text x="{cx}" y="348" font-family="sans-serif" font-size="11" font-weight="bold" fill="#e11d48" text-anchor="middle">🎯 Formulated Research Problem</text>
  <defs>
    <marker id="arrow-rq" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#e11d48"/>
    </marker>
  </defs>
</svg>"""

        return CapabilityOutput(
            capability_id="research.problem.funnel",
            output_format="svg",
            rendered_content=svg,
            width_px=width,
            height_px=height,
        )


def _extract_problem_funnel(step: Any, material: Any) -> dict[str, Any]:
    title = material.content.metadata.title
    facts = [f.statement for f in material.content.facts] if material.content.facts else []
    return {
        "topic": title,
        "phenomenon": facts[0] if len(facts) > 0 else "Observed environmental / physical phenomenon",
        "problem_identification": facts[1] if len(facts) > 1 else "Discrepancy between expectation and reality",
        "scope_limitation": facts[2] if len(facts) > 2 else "Constrained to specific context and boundary",
        "final_research_question": f"How does the core variable influence outcomes in {title}?",
    }


problem_funnel_capability = Capability(
    metadata=CapabilityMetadata(
        capability_id="research.problem.funnel",
        category="research_problem",
        display_name="Research Problem Formulation Funnel",
        description="Tapering funnel diagram structuring the transformation of a broad phenomenon into a narrow research question.",
        semantic_tags=["research_problem", "problem_funnel", "phenomenon", "scope_limitation", "research_question", "problem_formulation"],
        supported_artifacts=["presentation", "document", "poster", "worksheet"],
        domain="research_education",
        complexity_score=2.0,
        preferred_renderer="svg",
        taxonomy=TaxonomySignature(
            family=CapabilityFamily.PROCESS_VISUALIZATION,
            primary_intent=SemanticIntent.NARROW_SCOPE,
            supported_intents=[SemanticIntent.SEQUENCE, SemanticIntent.EXPLAIN],
            structure=InformationStructure.HIERARCHY,
            pedagogical_role=PedagogicalRole.SCAFFOLD,
            visual_grammar=VisualGrammar.FUNNEL,
            density=DensityProfile.FOCUSED,
            preferred_formats=["presentation_16_9", "a4_landscape", "a4_portrait"],
        ),
    ),
    spec_model=ProblemFunnelSpec,
    renderer=ProblemFunnelRenderer(),
    parameter_extractor=_extract_problem_funnel,
)


# --- 2. Literature Gap Matrix ---

class ResearchGapSpec(CapabilitySpec):
    topic: str
    existing_consensus: str
    unresolved_gap: str
    study_contribution: str
    target_objective: str | None = None


class ResearchGapRenderer(CapabilityRenderer[ResearchGapSpec]):

    def validate_spec(self, spec: ResearchGapSpec) -> bool:
        return bool(spec.existing_consensus and spec.unresolved_gap and spec.study_contribution)

    def measure(self, spec: ResearchGapSpec, context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"height_px": 320}

    def render(self, spec: ResearchGapSpec, context: dict[str, Any] | None = None) -> CapabilityOutput:
        html = f"""
        <div class="capability-research-gap-card card">
            <div class="gap-header">
                <span class="badge gap-badge">Literature Gap Analysis</span>
                <h3>{spec.topic}</h3>
            </div>
            <div class="gap-columns-grid">
                <div class="gap-col known-col">
                    <div class="col-icon">📚</div>
                    <h4>What is Known</h4>
                    <p>{spec.existing_consensus}</p>
                </div>
                <div class="gap-col missing-col">
                    <div class="col-icon">❓</div>
                    <h4>The Knowledge Gap</h4>
                    <p class="gap-highlight">{spec.unresolved_gap}</p>
                </div>
                <div class="gap-col novel-col">
                    <div class="col-icon">💡</div>
                    <h4>This Study's Value</h4>
                    <p>{spec.study_contribution}</p>
                </div>
            </div>
        </div>
        """
        return CapabilityOutput(
            capability_id="research.problem.gap_matrix",
            output_format="html",
            rendered_content=html,
            width_px=750,
            height_px=320,
        )


def _extract_research_gap(step: Any, material: Any) -> dict[str, Any]:
    title = material.content.metadata.title
    return {
        "topic": title,
        "existing_consensus": "Established baseline knowledge in domain",
        "unresolved_gap": "Lack of deterministic operationalization in target setting",
        "study_contribution": "Provides structured empirical evidence and verification",
    }


research_gap_capability = Capability(
    metadata=CapabilityMetadata(
        capability_id="research.problem.gap_matrix",
        category="research_problem",
        display_name="Research Gap & Contribution Matrix",
        description="Three-column matrix contrasting established literature knowledge, the unresolved research gap, and the study's novel contribution.",
        semantic_tags=["research_gap", "literature_gap", "state_of_the_art", "novelty", "contribution", "kti_bab2"],
        supported_artifacts=["presentation", "document", "poster", "worksheet"],
        domain="research_education",
        complexity_score=2.0,
        preferred_renderer="html",
        taxonomy=TaxonomySignature(
            family=CapabilityFamily.COMPARATIVE_REASONING,
            primary_intent=SemanticIntent.COMPARE,
            supported_intents=[SemanticIntent.ARGUE, SemanticIntent.ANALYZE],
            structure=InformationStructure.MATRIX,
            pedagogical_role=PedagogicalRole.ANALYSIS,
            visual_grammar=VisualGrammar.COMPARISON,
            density=DensityProfile.FOCUSED,
            preferred_formats=["presentation_16_9", "a4_portrait", "a4_landscape"],
        ),
    ),
    spec_model=ResearchGapSpec,
    renderer=ResearchGapRenderer(),
    parameter_extractor=_extract_research_gap,
)
