"""
KIR AI Document Intelligence — General Diagram Library.

Provides parameterized deterministic vector diagrams:
- Linear Process Flow
- Sequential Timeline
- Research / Conceptual Funnel
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


class ProcessStep(BaseModel):
    step_number: int
    title: str
    description: str
    badge_color: str = "#3b82f6"


class ProcessFlowSpec(CapabilitySpec):
    flow_title: str = "Methodology / Process Pipeline"
    steps: list[ProcessStep] = Field(default_factory=list)


class ProcessFlowRenderer(CapabilityRenderer[ProcessFlowSpec]):

    def validate_spec(self, spec: ProcessFlowSpec) -> bool:
        return len(spec.steps) > 0

    def measure(self, spec: ProcessFlowSpec, context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"width_px": 750, "height_px": 220}

    def render(self, spec: ProcessFlowSpec, context: dict[str, Any] | None = None) -> CapabilityOutput:
        n = len(spec.steps)
        width = 800
        height = 240
        box_width = min(180, int((width - 80 - (n - 1) * 40) / max(n, 1)))
        
        nodes_svg = ""
        for i, s in enumerate(spec.steps):
            x = 40 + i * (box_width + 40)
            y = 70
            
            # Step box
            nodes_svg += f"""
            <g transform="translate({x}, {y})">
                <rect width="{box_width}" height="120" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>
                <circle cx="20" cy="20" r="14" fill="{s.badge_color}"/>
                <text x="20" y="24" font-family="sans-serif" font-size="12" font-weight="bold" fill="#ffffff" text-anchor="middle">{s.step_number}</text>
                <text x="42" y="24" font-family="sans-serif" font-size="12" font-weight="bold" fill="#1e293b">{s.title[:16]}</text>
                <foreignObject x="10" y="45" width="{box_width-20}" height="65">
                    <p xmlns="http://www.w3.org/1999/xhtml" style="font-family:sans-serif; font-size:11px; color:#475569; margin:0; line-height:1.3;">{s.description}</p>
                </foreignObject>
            </g>
            """
            
            # Connecting Arrow
            if i < n - 1:
                arrow_x1 = x + box_width + 5
                arrow_x2 = arrow_x1 + 30
                arrow_y = y + 60
                nodes_svg += f"""
                <line x1="{arrow_x1}" y1="{arrow_y}" x2="{arrow_x2}" y2="{arrow_y}" stroke="#94a3b8" stroke-width="2.5" marker-end="url(#arrow-flow)"/>
                """

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">
  <defs>
    <marker id="arrow-flow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect x="5" y="5" width="{width-10}" height="{height-10}" rx="12" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.5"/>
  <text x="30" y="40" font-family="sans-serif" font-size="16" font-weight="bold" fill="#0f172a">{spec.flow_title}</text>
  {nodes_svg}
</svg>"""

        return CapabilityOutput(
            capability_id="diagram.process_flow",
            output_format="svg",
            rendered_content=svg,
            width_px=width,
            height_px=height,
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


process_flow_capability = Capability(
    metadata=CapabilityMetadata(
        capability_id="diagram.process_flow",
        category="diagram",
        display_name="Linear Process & Methodology Flow",
        description="Horizontal step-by-step pipeline diagram showing stages, numbered badges, and descriptions.",
        semantic_tags=["process_flow", "pipeline", "methodology_flow", "step_by_step", "sequence_diagram", "workflow"],
        supported_artifacts=["presentation", "document", "poster", "worksheet"],
        domain="general",
        complexity_score=2.0,
        preferred_renderer="svg",
        taxonomy=TaxonomySignature(
            family=CapabilityFamily.PROCESS_VISUALIZATION,
            primary_intent=SemanticIntent.SEQUENCE,
            supported_intents=[SemanticIntent.EXPLAIN, SemanticIntent.ANALYZE],
            structure=InformationStructure.LINEAR_SEQUENCE,
            pedagogical_role=PedagogicalRole.EXPLANATION,
            visual_grammar=VisualGrammar.PROCESS_FLOW,
            density=DensityProfile.FOCUSED,
            preferred_formats=["presentation_16_9", "a4_landscape", "a4_portrait"],
        ),
    ),
    spec_model=ProcessFlowSpec,
    renderer=ProcessFlowRenderer(),
)
