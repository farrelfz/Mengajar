"""
KIR AI Document Intelligence — Physics Mechanics Visualization Library.

Provides deterministic, parameterized vector diagrams for classical mechanics:
- Torque & Rotational Force System
- Free Body Diagram (FBD)
- Inclined Plane with Force Decomposition
"""

from __future__ import annotations

import math
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


# --- 1. Torque Diagram ---

class TorqueDiagramSpec(CapabilitySpec):
    pivot_label: str = "Pivot (O)"
    lever_length_m: float = 2.0
    force_newtons: float = 50.0
    force_angle_deg: float = 90.0  # Angle relative to lever arm
    show_perpendicular_component: bool = True
    show_lever_label: bool = True
    rotation_direction: str = "counterclockwise"  # "counterclockwise" (+) or "clockwise" (-)


class TorqueDiagramRenderer(CapabilityRenderer[TorqueDiagramSpec]):

    def validate_spec(self, spec: TorqueDiagramSpec) -> bool:
        return 0.0 <= spec.force_angle_deg <= 180.0

    def measure(self, spec: TorqueDiagramSpec, context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"width_px": 600, "height_px": 300, "aspect_ratio": "2:1"}

    def render(self, spec: TorqueDiagramSpec, context: dict[str, Any] | None = None) -> CapabilityOutput:
        # SVG Canvas Coordinates
        width, height = 650, 320
        pivot_x, pivot_y = 120, 200
        lever_len_px = 350
        end_x = pivot_x + lever_len_px
        end_y = pivot_y

        # Force vector geometry
        angle_rad = math.radians(spec.force_angle_deg)
        force_len_px = 100
        # In SVG y is downwards, so an upward force has negative dy
        fx = force_len_px * math.cos(angle_rad)
        fy = -force_len_px * math.sin(angle_rad)
        tip_x = end_x + fx
        tip_y = end_y + fy

        # Perpendicular component
        perp_len = force_len_px * math.sin(angle_rad)
        perp_tip_x = end_x
        perp_tip_y = end_y - perp_len

        # Torque calculation
        tau = spec.lever_length_m * spec.force_newtons * math.sin(angle_rad)

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#e74c3c"/>
    </marker>
    <marker id="arrow-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#3498db"/>
    </marker>
    <marker id="arrow-torque" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#2ecc71"/>
    </marker>
  </defs>

  <!-- Background Card -->
  <rect x="5" y="5" width="{width-10}" height="{height-10}" rx="12" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.5"/>

  <!-- Title & Torque Badge -->
  <text x="30" y="40" font-family="sans-serif" font-size="16" font-weight="bold" fill="#1e293b">Torque System: τ = r · F · sin(θ)</text>
  <rect x="440" y="20" width="180" height="34" rx="8" fill="#f0fdf4" stroke="#86efac" stroke-width="1"/>
  <text x="455" y="42" font-family="sans-serif" font-size="13" font-weight="bold" fill="#166534">τ = {tau:.1f} N·m ({spec.rotation_direction[:3].upper()})</text>

  <!-- Lever Arm (Rigid Body) -->
  <rect x="{pivot_x}" y="{pivot_y - 8}" width="{lever_len_px}" height="16" rx="4" fill="#64748b" stroke="#334155" stroke-width="1.5"/>
  <line x1="{pivot_x}" y1="{pivot_y}" x2="{end_x}" y2="{end_y}" stroke="#94a3b8" stroke-dasharray="4,4"/>

  <!-- Lever Dimension Line -->
  <line x1="{pivot_x}" y1="{pivot_y + 35}" x2="{end_x}" y2="{pivot_y + 35}" stroke="#475569" stroke-width="1.5" marker-start="url(#arrow-blue)" marker-end="url(#arrow-blue)"/>
  <text x="{pivot_x + lever_len_px/2}" y="{pivot_y + 55}" font-family="sans-serif" font-size="13" font-weight="600" text-anchor="middle" fill="#334155">r = {spec.lever_length_m} m</text>

  <!-- Pivot (Fulcrum) Triangle & Circle -->
  <polygon points="{pivot_x},{pivot_y} {pivot_x - 15},{pivot_y + 30} {pivot_x + 15},{pivot_y + 30}" fill="#334155"/>
  <circle cx="{pivot_x}" cy="{pivot_y}" r="7" fill="#fbbf24" stroke="#b45309" stroke-width="2"/>
  <text x="{pivot_x}" y="{pivot_y - 20}" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle" fill="#0f172a">{spec.pivot_label}</text>

  <!-- Force Vector Line -->
  <line x1="{end_x}" y1="{end_y}" x2="{tip_x}" y2="{tip_y}" stroke="#e74c3c" stroke-width="3.5" marker-end="url(#arrow)"/>
  <text x="{tip_x + 10}" y="{tip_y}" font-family="sans-serif" font-size="14" font-weight="bold" fill="#dc2626">F = {spec.force_newtons} N</text>

  <!-- Angle Arc & Label -->
  <path d="M {end_x + 40} {end_y} A 40 40 0 0 0 {end_x + 40*math.cos(angle_rad)} {end_y - 40*math.sin(angle_rad)}" fill="none" stroke="#f59e0b" stroke-width="2"/>
  <text x="{end_x + 50}" y="{end_y - 15}" font-family="sans-serif" font-size="12" font-weight="bold" fill="#d97706">θ = {spec.force_angle_deg:.0f}°</text>

  <!-- Perpendicular Component (if enabled) -->
  {f'''
  <line x1="{end_x}" y1="{end_y}" x2="{perp_tip_x}" y2="{perp_tip_y}" stroke="#3b82f6" stroke-width="2" stroke-dasharray="3,3" marker-end="url(#arrow-blue)"/>
  <line x1="{perp_tip_x}" y1="{perp_tip_y}" x2="{tip_x}" y2="{tip_y}" stroke="#cbd5e1" stroke-dasharray="2,2"/>
  <text x="{perp_tip_x - 70}" y="{perp_tip_y + 20}" font-family="sans-serif" font-size="11" fill="#2563eb">F_perp = {spec.force_newtons*math.sin(angle_rad):.1f} N</text>
  ''' if spec.show_perpendicular_component and spec.force_angle_deg != 90 else ''}

  <!-- Torque Direction Indicator Arc -->
  <path d="M {pivot_x + 60} {pivot_y - 50} A 50 50 0 0 0 {pivot_x + 20} {pivot_y - 70}" fill="none" stroke="#2ecc71" stroke-width="3" marker-end="url(#arrow-torque)"/>
  <text x="{pivot_x + 50}" y="{pivot_y - 75}" font-family="sans-serif" font-size="12" font-weight="bold" fill="#15803d">+τ (CCW)</text>
</svg>"""

        return CapabilityOutput(
            capability_id="physics.mechanics.torque_diagram",
            output_format="svg",
            rendered_content=svg,
            width_px=width,
            height_px=height,
            metadata={"tau_newton_meters": tau, "lever_m": spec.lever_length_m, "force_n": spec.force_newtons},
        )


def _extract_torque_diagram(step: Any, material: Any) -> dict[str, Any]:
    return {
        "pivot_label": "Pivot (O)",
        "lever_length_m": 2.0,
        "force_newtons": 50.0,
        "force_angle_deg": 90.0,
        "rotation_direction": "counterclockwise",
    }


torque_diagram_capability = Capability(
    metadata=CapabilityMetadata(
        capability_id="physics.mechanics.torque_diagram",
        category="scientific_visualization",
        display_name="Torque & Rotational Force Diagram",
        description="Vector diagram showing pivot, lever arm, applied force vector, angle, and torque value.",
        semantic_tags=["torque", "rotation", "pivot", "force", "moment_arm", "rotational_equilibrium", "mechanics", "rotational_force_system"],
        supported_artifacts=["presentation", "document", "poster", "worksheet"],
        domain="physics",
        complexity_score=3.5,
        preferred_renderer="svg",
        taxonomy=TaxonomySignature(
            family=CapabilityFamily.SPATIAL_SYSTEMS,
            primary_intent=SemanticIntent.EXPLAIN,
            supported_intents=[SemanticIntent.RELATE, SemanticIntent.ANALYZE],
            structure=InformationStructure.SPATIAL_SYSTEM,
            pedagogical_role=PedagogicalRole.EXPLANATION,
            visual_grammar=VisualGrammar.ANNOTATED_DIAGRAM,
            density=DensityProfile.FOCUSED,
            preferred_formats=["presentation_16_9", "a4_landscape", "a4_portrait"],
        ),
    ),
    spec_model=TorqueDiagramSpec,
    renderer=TorqueDiagramRenderer(),
    parameter_extractor=_extract_torque_diagram,
)


# --- 2. Free Body Diagram ---

class ForceVector(BaseModel):
    name: str
    magnitude_n: float
    angle_deg: float  # 0 = right (+x), 90 = up (+y), 180 = left (-x), 270 = down (-y)
    color: str = "#e74c3c"


class FreeBodyDiagramSpec(CapabilitySpec):
    body_name: str = "Object (m)"
    forces: list[ForceVector] = Field(default_factory=lambda: [
        ForceVector(name="F_N", magnitude_n=49.0, angle_deg=90.0, color="#3498db"),
        ForceVector(name="W (mg)", magnitude_n=49.0, angle_deg=270.0, color="#e74c3c"),
        ForceVector(name="F_app", magnitude_n=20.0, angle_deg=0.0, color="#2ecc71"),
        ForceVector(name="f_k", magnitude_n=10.0, angle_deg=180.0, color="#f39c12"),
    ])


class FreeBodyDiagramRenderer(CapabilityRenderer[FreeBodyDiagramSpec]):

    def validate_spec(self, spec: FreeBodyDiagramSpec) -> bool:
        return len(spec.forces) > 0

    def measure(self, spec: FreeBodyDiagramSpec, context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"width_px": 500, "height_px": 400}

    def render(self, spec: FreeBodyDiagramSpec, context: dict[str, Any] | None = None) -> CapabilityOutput:
        width, height = 500, 400
        cx, cy = width / 2, height / 2

        forces_svg = ""
        for f in spec.forces:
            rad = math.radians(f.angle_deg)
            # Scale magnitude to px
            arrow_len = 50 + min(f.magnitude_n * 2, 90)
            fx = cx + arrow_len * math.cos(rad)
            fy = cy - arrow_len * math.sin(rad)
            
            label_x = cx + (arrow_len + 25) * math.cos(rad)
            label_y = cy - (arrow_len + 15) * math.sin(rad)

            forces_svg += f"""
            <line x1="{cx}" y1="{cy}" x2="{fx}" y2="{fy}" stroke="{f.color}" stroke-width="3" marker-end="url(#fbd-arrow)"/>
            <text x="{label_x}" y="{label_y}" font-family="sans-serif" font-size="12" font-weight="bold" fill="{f.color}" text-anchor="middle">{f.name} ({f.magnitude_n}N)</text>
            """

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">
  <defs>
    <marker id="fbd-arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#334155"/>
    </marker>
  </defs>
  <rect x="5" y="5" width="{width-10}" height="{height-10}" rx="12" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.5"/>
  <text x="30" y="38" font-family="sans-serif" font-size="16" font-weight="bold" fill="#0f172a">Free Body Diagram: {spec.body_name}</text>
  
  <!-- Coordinate axes -->
  <line x1="{cx - 160}" y1="{cy}" x2="{cx + 160}" y2="{cy}" stroke="#e2e8f0" stroke-width="1.5" stroke-dasharray="4,4"/>
  <line x1="{cx}" y1="{cy - 140}" x2="{cx}" y2="{cy + 140}" stroke="#e2e8f0" stroke-width="1.5" stroke-dasharray="4,4"/>
  <text x="{cx + 170}" y="{cy + 4}" font-family="sans-serif" font-size="11" fill="#94a3b8">+x</text>
  <text x="{cx + 4}" y="{cy - 145}" font-family="sans-serif" font-size="11" fill="#94a3b8">+y</text>

  <!-- Central Body (Mass) -->
  <rect x="{cx - 30}" y="{cy - 30}" width="60" height="60" rx="8" fill="#3b82f6" stroke="#1d4ed8" stroke-width="2"/>
  <text x="{cx}" y="{cy + 5}" font-family="sans-serif" font-size="13" font-weight="bold" fill="#ffffff" text-anchor="middle">m</text>

  <!-- Force Vectors -->
  {forces_svg}
</svg>"""

        return CapabilityOutput(
            capability_id="physics.mechanics.free_body_diagram",
            output_format="svg",
            rendered_content=svg,
            width_px=width,
            height_px=height,
        )


def _extract_fbd(step: Any, material: Any) -> dict[str, Any]:
    return {"body_name": f"Object ({material.content.metadata.title[:20]})"}


free_body_diagram_capability = Capability(
    metadata=CapabilityMetadata(
        capability_id="physics.mechanics.free_body_diagram",
        category="scientific_visualization",
        display_name="Free Body Diagram (FBD)",
        description="2D Free Body Diagram showing all concurrent forces acting on a body with coordinate axes.",
        semantic_tags=["free_body_diagram", "fbd", "forces", "mechanics", "newton_laws", "equilibrium"],
        supported_artifacts=["presentation", "document", "poster", "worksheet"],
        domain="physics",
        complexity_score=2.5,
        preferred_renderer="svg",
        taxonomy=TaxonomySignature(
            family=CapabilityFamily.SPATIAL_SYSTEMS,
            primary_intent=SemanticIntent.ANALYZE,
            supported_intents=[SemanticIntent.EXPLAIN, SemanticIntent.RELATE],
            structure=InformationStructure.SPATIAL_SYSTEM,
            pedagogical_role=PedagogicalRole.ANALYSIS,
            visual_grammar=VisualGrammar.ANNOTATED_DIAGRAM,
            density=DensityProfile.FOCUSED,
            preferred_formats=["presentation_16_9", "a4_landscape", "a4_portrait"],
        ),
    ),
    spec_model=FreeBodyDiagramSpec,
    renderer=FreeBodyDiagramRenderer(),
    parameter_extractor=_extract_fbd,
)
