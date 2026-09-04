"""
KIR AI Document Intelligence — Scientific Thinking & Reasoning Capabilities.

Provides parameterized visual and pedagogical components for scientific inquiry:
- Scientific Reasoning Pathway (Observation -> Question -> Problem -> Hypothesis -> Investigation -> Evidence -> Reasoning -> Conclusion)
- Hypothesis Testing Matrix (Hypothesis, Variables, Predicted vs Observed Outcomes)
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


class ReasoningStage(BaseModel):
    stage_name: str  # e.g., "Observation", "Question", "Hypothesis", "Evidence", "Conclusion"
    description: str
    details: str | None = None
    is_active_focus: bool = False


class ScientificReasoningPathwaySpec(CapabilitySpec):
    topic: str = "Scientific Inquiry Pathway"
    stages: list[ReasoningStage] = Field(default_factory=lambda: [
        ReasoningStage(stage_name="Observation", description="Notice an anomaly or pattern in nature"),
        ReasoningStage(stage_name="Question", description="Formulate an inquiry about the causal mechanism"),
        ReasoningStage(stage_name="Hypothesis", description="Propose a testable, falsifiable explanation"),
        ReasoningStage(stage_name="Investigation", description="Design controlled experiment & gather data"),
        ReasoningStage(stage_name="Evidence", description="Analyze quantitative and qualitative data"),
        ReasoningStage(stage_name="Conclusion", description="Synthesize findings and evaluate hypothesis"),
    ])


class ScientificReasoningPathwayRenderer(CapabilityRenderer[ScientificReasoningPathwaySpec]):

    def validate_spec(self, spec: ScientificReasoningPathwaySpec) -> bool:
        return len(spec.stages) >= 3

    def measure(self, spec: ScientificReasoningPathwaySpec, context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"width_px": 800, "height_px": 280, "complexity": "standard"}

    def render(self, spec: ScientificReasoningPathwaySpec, context: dict[str, Any] | None = None) -> CapabilityOutput:
        n = len(spec.stages)
        width = 850
        height = 260
        stage_width = min(120, int((width - 60 - (n - 1) * 20) / n))
        
        stages_svg = ""
        colors = ["#3b82f6", "#0ea5e9", "#06b6d4", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899"]
        
        for i, s in enumerate(spec.stages):
            x = 30 + i * (stage_width + 20)
            y = 60
            color = colors[i % len(colors)]
            fill_bg = "#eff6ff" if s.is_active_focus else "#f8fafc"
            stroke_clr = color if s.is_active_focus else "#cbd5e1"
            stroke_w = "2.5" if s.is_active_focus else "1.5"

            stages_svg += f"""
            <g transform="translate({x}, {y})">
                <rect width="{stage_width}" height="140" rx="8" fill="{fill_bg}" stroke="{stroke_clr}" stroke-width="{stroke_w}"/>
                <rect width="{stage_width}" height="28" rx="8" fill="{color}"/>
                <text x="{stage_width/2}" y="18" font-family="sans-serif" font-size="11" font-weight="bold" fill="#ffffff" text-anchor="middle">{s.stage_name}</text>
                <foreignObject x="6" y="34" width="{stage_width-12}" height="100">
                    <p xmlns="http://www.w3.org/1999/xhtml" style="font-family:sans-serif; font-size:10px; color:#334155; margin:0; line-height:1.3;">{s.description}</p>
                </foreignObject>
            </g>
            """
            if i < n - 1:
                arrow_x = x + stage_width + 2
                arrow_y = y + 70
                stages_svg += f"""
                <line x1="{arrow_x}" y1="{arrow_y}" x2="{arrow_x + 16}" y2="{arrow_y}" stroke="#94a3b8" stroke-width="2" marker-end="url(#arrow-sci)"/>
                """

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">
  <defs>
    <marker id="arrow-sci" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect x="5" y="5" width="{width-10}" height="{height-10}" rx="12" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.5"/>
  <text x="30" y="38" font-family="sans-serif" font-size="16" font-weight="bold" fill="#0f172a">Scientific Reasoning Pathway: {spec.topic}</text>
  {stages_svg}
</svg>"""

        return CapabilityOutput(
            capability_id="research.scientific.reasoning_pathway",
            output_format="svg",
            rendered_content=svg,
            width_px=width,
            height_px=height,
        )


def _extract_reasoning_pathway(step: Any, material: Any) -> dict[str, Any]:
    return {"topic": material.content.metadata.title}


from app.capabilities.taxonomy import (
    CapabilityFamily,
    DensityProfile,
    InformationStructure,
    PedagogicalRole,
    SemanticIntent,
    TaxonomySignature,
    VisualGrammar,
)


scientific_reasoning_pathway_capability = Capability(
    metadata=CapabilityMetadata(
        capability_id="research.scientific.reasoning_pathway",
        category="scientific_thinking",
        display_name="Scientific Reasoning Pathway",
        description="Sequential diagram mapping the inquiry cycle from observation and question to evidence and conclusion.",
        semantic_tags=["scientific_thinking", "scientific_reasoning", "inquiry", "reasoning_pathway", "observation", "hypothesis", "evidence", "conclusion"],
        supported_artifacts=["presentation", "document", "poster", "worksheet"],
        domain="research_education",
        complexity_score=2.0,
        preferred_renderer="svg",
        taxonomy=TaxonomySignature(
            family=CapabilityFamily.PROCESS_VISUALIZATION,
            primary_intent=SemanticIntent.SEQUENCE,
            supported_intents=[SemanticIntent.INVESTIGATE, SemanticIntent.EXPLAIN],
            structure=InformationStructure.LINEAR_SEQUENCE,
            pedagogical_role=PedagogicalRole.SCAFFOLD,
            visual_grammar=VisualGrammar.REASONING_FLOW,
            density=DensityProfile.FOCUSED,
            preferred_formats=["presentation_16_9", "a4_landscape", "a4_portrait"],
        ),
    ),
    spec_model=ScientificReasoningPathwaySpec,
    renderer=ScientificReasoningPathwayRenderer(),
    parameter_extractor=_extract_reasoning_pathway,
)


# --- 2. Hypothesis Formulation & Testing Matrix ---

class HypothesisTestSpec(CapabilitySpec):
    research_question: str
    hypothesis_statement: str
    independent_variable: str
    dependent_variable: str
    controlled_variables: list[str] = Field(default_factory=list)
    predicted_outcome: str
    observed_outcome: str | None = None
    conclusion_verdict: str | None = None  # "Supported", "Rejected", "Inconclusive"


class HypothesisTestRenderer(CapabilityRenderer[HypothesisTestSpec]):

    def validate_spec(self, spec: HypothesisTestSpec) -> bool:
        return bool(spec.research_question and spec.hypothesis_statement and spec.independent_variable and spec.dependent_variable)

    def measure(self, spec: HypothesisTestSpec, context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"height_px": 380}

    def render(self, spec: HypothesisTestSpec, context: dict[str, Any] | None = None) -> CapabilityOutput:
        ctrls_html = ", ".join(spec.controlled_variables) if spec.controlled_variables else "Standard laboratory conditions"
        observed_part = ""
        if spec.observed_outcome:
            observed_part = f"""
            <div class="verdict-banner {'verdict-supported' if spec.conclusion_verdict == 'Supported' else 'verdict-rejected'}">
                <strong>Observed Result:</strong> {spec.observed_outcome}
                <span class="verdict-tag">[{spec.conclusion_verdict or 'ANALYZED'}]</span>
            </div>
            """

        html = f"""
        <div class="capability-hypothesis-card card">
            <div class="hyp-header">
                <span class="badge sci-badge">Hypothesis Test Protocol</span>
                <h3>RQ: {spec.research_question}</h3>
            </div>
            <div class="hypothesis-banner">
                <strong>Hypothesis ($H_1$):</strong> {spec.hypothesis_statement}
            </div>
            <div class="variables-grid">
                <div class="var-box">
                    <span class="var-type">Independent Variable (Manipulated)</span>
                    <div class="var-name">{spec.independent_variable}</div>
                </div>
                <div class="var-box">
                    <span class="var-type">Dependent Variable (Measured)</span>
                    <div class="var-name">{spec.dependent_variable}</div>
                </div>
                <div class="var-box">
                    <span class="var-type">Controlled Variables (Constants)</span>
                    <div class="var-name">{ctrls_html}</div>
                </div>
            </div>
            <div class="prediction-box">
                <strong>Predicted Outcome:</strong> {spec.predicted_outcome}
            </div>
            {observed_part}
        </div>
        """
        return CapabilityOutput(
            capability_id="research.scientific.hypothesis_test",
            output_format="html",
            rendered_content=html,
            width_px=750,
            height_px=380,
        )


def _extract_hypothesis_test(step: Any, material: Any) -> dict[str, Any]:
    title = material.content.metadata.title
    return {
        "research_question": f"How does the primary factor affect target metrics in {title}?",
        "hypothesis_statement": "If the primary intervention increases, then the target outcome improves proportionally.",
        "independent_variable": "Primary Factor / Treatment Intervention",
        "dependent_variable": "Target Metric / Measured Response",
        "controlled_variables": ["Standard temperature & environment", "Consistent sample size", "Uniform measurement instrument"],
        "predicted_outcome": "Statistically significant correlation (p < 0.05)",
    }


hypothesis_test_capability = Capability(
    metadata=CapabilityMetadata(
        capability_id="research.scientific.hypothesis_test",
        category="scientific_thinking",
        display_name="Hypothesis Formulation & Testing Matrix",
        description="Structured scaffold for operationalizing a testable hypothesis with independent, dependent, and controlled variables.",
        semantic_tags=["hypothesis", "hypothesis_testing", "variables", "independent_variable", "dependent_variable", "prediction", "scientific_method"],
        supported_artifacts=["presentation", "document", "worksheet", "poster"],
        domain="research_education",
        complexity_score=2.5,
        preferred_renderer="html",
        taxonomy=TaxonomySignature(
            family=CapabilityFamily.EVIDENCE_ANALYSIS,
            primary_intent=SemanticIntent.INVESTIGATE,
            supported_intents=[SemanticIntent.RELATE, SemanticIntent.ANALYZE],
            structure=InformationStructure.EVIDENCE_CHAIN,
            pedagogical_role=PedagogicalRole.ANALYSIS,
            visual_grammar=VisualGrammar.MATRIX,
            density=DensityProfile.ANALYTICAL,
            preferred_formats=["presentation_16_9", "a4_portrait", "a4_landscape"],
        ),
    ),
    spec_model=HypothesisTestSpec,
    renderer=HypothesisTestRenderer(),
    parameter_extractor=_extract_hypothesis_test,
)


# =====================================================================
# 3. Variable Relationship Map (Causal / Correlational Graph)
# =====================================================================

class VariableNode(BaseModel):
    name: str
    variable_role: str  # "Independent", "Dependent", "Moderator", "Mediator"
    description: str


class VariableRelationshipMapSpec(CapabilitySpec):
    diagram_title: str = "Theoretical Variable Structural Model"
    nodes: list[VariableNode] = Field(default_factory=list)
    relationship_statement: str = "Direct positive causal influence"


class VariableRelationshipMapRenderer(CapabilityRenderer[VariableRelationshipMapSpec]):

    def validate_spec(self, spec: VariableRelationshipMapSpec) -> bool:
        return len(spec.nodes) >= 2

    def measure(self, spec: VariableRelationshipMapSpec, context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"height_px": 300}

    def render(self, spec: VariableRelationshipMapSpec, context: dict[str, Any] | None = None) -> CapabilityOutput:
        nodes_html = ""
        for n in spec.nodes:
            nodes_html += f"""
            <div class="var-rel-node">
                <span class="var-role-tag">{n.variable_role}</span>
                <h4>{n.name}</h4>
                <p>{n.description}</p>
            </div>
            """

        html = f"""
        <div class="capability-variable-map card">
            <div class="map-header">
                <span class="badge rel-badge">Conceptual Framework</span>
                <h3>{spec.diagram_title}</h3>
            </div>
            <div class="nodes-container">
                {nodes_html}
            </div>
            <div class="rel-footer">
                <strong>Hypothesized Path:</strong> {spec.relationship_statement}
            </div>
        </div>
        """
        return CapabilityOutput(
            capability_id="research.variable_relationship_map",
            output_format="html",
            rendered_content=html,
            width_px=750,
            height_px=300,
        )


def _extract_variable_map(step: Any, material: Any) -> dict[str, Any]:
    title = material.content.metadata.title
    return {
        "diagram_title": f"Causal Structural Model: {title}",
        "nodes": [
            VariableNode(name="Core Factor (X)", variable_role="Independent", description="Manipulated or baseline variable"),
            VariableNode(name="Observed Response (Y)", variable_role="Dependent", description="Target measurement outcome"),
            VariableNode(name="Contextual Factor (M)", variable_role="Moderator", description="Environmental boundary condition"),
        ],
        "relationship_statement": f"X exerts statistically significant effect on Y across {title}.",
    }


variable_relationship_map_capability = Capability(
    metadata=CapabilityMetadata(
        capability_id="research.variable_relationship_map",
        category="scientific_thinking",
        display_name="Variable Relationship Structural Model",
        description="Structural diagram mapping independent, dependent, mediator, and moderator variables in a study.",
        semantic_tags=["variables", "causal_model", "relationship_map", "moderator", "mediator", "framework"],
        supported_artifacts=["presentation", "document", "poster", "worksheet"],
        domain="research_education",
        complexity_score=2.5,
        preferred_renderer="html",
        taxonomy=TaxonomySignature(
            family=CapabilityFamily.RELATIONSHIP_MAPPING,
            primary_intent=SemanticIntent.RELATE,
            supported_intents=[SemanticIntent.ANALYZE, SemanticIntent.EXPLAIN],
            structure=InformationStructure.MAPPING,
            pedagogical_role=PedagogicalRole.ANALYSIS,
            visual_grammar=VisualGrammar.ANNOTATED_DIAGRAM,
            density=DensityProfile.FOCUSED,
            preferred_formats=["presentation_16_9", "a4_landscape", "a4_portrait"],
        ),
    ),
    spec_model=VariableRelationshipMapSpec,
    renderer=VariableRelationshipMapRenderer(),
    parameter_extractor=_extract_variable_map,
)


# =====================================================================
# 4. Experiment Workflow Pipeline
# =====================================================================

class ExperimentPhase(BaseModel):
    phase_number: int
    title: str
    action_details: str
    controls_applied: str


class ExperimentWorkflowSpec(CapabilitySpec):
    experiment_title: str
    phases: list[ExperimentPhase] = Field(default_factory=list)


class ExperimentWorkflowRenderer(CapabilityRenderer[ExperimentWorkflowSpec]):

    def validate_spec(self, spec: ExperimentWorkflowSpec) -> bool:
        return len(spec.phases) > 0

    def measure(self, spec: ExperimentWorkflowSpec, context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"height_px": len(spec.phases) * 85 + 130}

    def render(self, spec: ExperimentWorkflowSpec, context: dict[str, Any] | None = None) -> CapabilityOutput:
        phases_html = ""
        for p in spec.phases:
            phases_html += f"""
            <div class="exp-phase-card">
                <div class="phase-badge">Phase {p.phase_number}</div>
                <div class="phase-content">
                    <h4>{p.title}</h4>
                    <p class="phase-action"><strong>Procedure:</strong> {p.action_details}</p>
                    <p class="phase-control">🔒 <strong>Controls:</strong> {p.controls_applied}</p>
                </div>
            </div>
            """

        html = f"""
        <div class="capability-experiment-workflow card">
            <div class="exp-header">
                <span class="badge exp-badge">Experimental Procedure</span>
                <h3>{spec.experiment_title}</h3>
            </div>
            <div class="exp-phases-list">
                {phases_html}
            </div>
        </div>
        """
        return CapabilityOutput(
            capability_id="research.experiment_workflow",
            output_format="html",
            rendered_content=html,
            width_px=750,
            height_px=len(spec.phases) * 85 + 130,
        )


def _extract_experiment_workflow(step: Any, material: Any) -> dict[str, Any]:
    title = material.content.metadata.title
    return {
        "experiment_title": f"Experimental Protocol: {title}",
        "phases": [
            ExperimentPhase(phase_number=1, title="Sample Preparation & Calibration", action_details="Standardize baseline specimen parameters.", controls_applied="Controlled temperature & instrument zeroing."),
            ExperimentPhase(phase_number=2, title="Treatment Execution & Logging", action_details="Apply incremental test interventions.", controls_applied="Continuous multi-sensor recording."),
            ExperimentPhase(phase_number=3, title="Post-Test Verification & Statistics", action_details="Perform triplicate verification and ANOVA.", controls_applied="Blind statistical evaluation."),
        ],
    }


experiment_workflow_capability = Capability(
    metadata=CapabilityMetadata(
        capability_id="research.experiment_workflow",
        category="scientific_thinking",
        display_name="Experimental Workflow Protocol",
        description="Multi-phase experimental pipeline detailing procedures, measurements, and procedural controls.",
        semantic_tags=["experiment", "workflow", "procedure", "laboratory", "experimental_design", "pipeline"],
        supported_artifacts=["presentation", "document", "poster", "worksheet"],
        domain="research_education",
        complexity_score=2.5,
        preferred_renderer="html",
        taxonomy=TaxonomySignature(
            family=CapabilityFamily.PROCESS_VISUALIZATION,
            primary_intent=SemanticIntent.SEQUENCE,
            supported_intents=[SemanticIntent.INVESTIGATE, SemanticIntent.EXPLAIN],
            structure=InformationStructure.LINEAR_SEQUENCE,
            pedagogical_role=PedagogicalRole.SCAFFOLD,
            visual_grammar=VisualGrammar.PROCESS_FLOW,
            density=DensityProfile.ANALYTICAL,
            preferred_formats=["presentation_16_9", "a4_portrait", "a4_landscape"],
        ),
    ),
    spec_model=ExperimentWorkflowSpec,
    renderer=ExperimentWorkflowRenderer(),
    parameter_extractor=_extract_experiment_workflow,
)
