"""
KIR AI Document Intelligence — Pedagogical Capabilities.

Provides parameterized components for pedagogical patterns:
- Worked Example (Problem, Knowns, Principles, Step-by-Step, Answer)
- Misconception Correction (Belief, Counterexample, Explanation)
- Question & Hook
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


# --- 1. Worked Example ---

class WorkedExampleStepSpec(BaseModel):
    step_number: int
    title: str
    calculation: str | None = None
    explanation: str


class WorkedExampleSpec(CapabilitySpec):
    problem: str
    knowns: dict[str, str] = Field(default_factory=dict)
    unknowns: list[str] = Field(default_factory=list)
    principles: list[str] = Field(default_factory=list)
    steps: list[WorkedExampleStepSpec] = Field(default_factory=list)
    final_answer: str
    interpretation: str | None = None


class WorkedExampleRenderer(CapabilityRenderer[WorkedExampleSpec]):

    def validate_spec(self, spec: WorkedExampleSpec) -> bool:
        return bool(spec.problem and spec.final_answer)

    def measure(self, spec: WorkedExampleSpec, context: dict[str, Any] | None = None) -> dict[str, Any]:
        step_count = len(spec.steps)
        height = 300 + (step_count * 60)
        return {"estimated_height_px": height, "complexity": "high" if step_count > 3 else "standard"}

    def render(self, spec: WorkedExampleSpec, context: dict[str, Any] | None = None) -> CapabilityOutput:
        knowns_html = "".join(f"<li><strong>{k}:</strong> {v}</li>" for k, v in spec.knowns.items())
        principles_html = "".join(f"<span class='badge principle-badge'>{p}</span> " for p in spec.principles)
        
        steps_html = ""
        for s in spec.steps:
            calc_part = f"<div class='step-math'><code>{s.calculation}</code></div>" if s.calculation else ""
            steps_html += f"""
            <div class="worked-step">
                <div class="step-num">Step {s.step_number}</div>
                <div class="step-body">
                    <div class="step-title"><strong>{s.title}</strong></div>
                    <div class="step-desc">{s.explanation}</div>
                    {calc_part}
                </div>
            </div>
            """

        html = f"""
        <div class="capability-worked-example card">
            <div class="we-header">
                <span class="we-tag">Worked Example</span>
                <h3 class="we-problem">{spec.problem}</h3>
            </div>
            <div class="we-meta-grid">
                {f'<div class="we-knowns"><h4>Known Data:</h4><ul>{knowns_html}</ul></div>' if knowns_html else ''}
                {f'<div class="we-principles"><h4>Key Principles:</h4><div>{principles_html}</div></div>' if principles_html else ''}
            </div>
            <div class="we-steps-container">
                {steps_html}
            </div>
            <div class="we-final-answer">
                <strong>Result:</strong> {spec.final_answer}
                {f'<div class="we-interpretation">{spec.interpretation}</div>' if spec.interpretation else ''}
            </div>
        </div>
        """
        return CapabilityOutput(
            capability_id="pedagogy.worked_example",
            output_format="html",
            rendered_content=html,
            width_px=800,
            height_px=len(spec.steps) * 80 + 250,
        )


def _extract_worked_example(step: Any, material: Any) -> dict[str, Any]:
    title = material.content.metadata.title
    we = material.content.worked_examples[0] if material.content.worked_examples else None
    if we:
        return {
            "problem": we.problem_statement,
            "knowns": we.knowns,
            "principles": we.principles_used,
            "final_answer": we.final_answer,
            "interpretation": we.interpretation,
        }
    return {
        "problem": f"Sample Application: {title}",
        "final_answer": "Demonstrated Solution",
    }


from app.capabilities.taxonomy import (
    CapabilityFamily,
    DensityProfile,
    InformationStructure,
    PedagogicalRole,
    SemanticIntent,
    TaxonomySignature,
    VisualGrammar,
)


worked_example_capability = Capability(
    metadata=CapabilityMetadata(
        capability_id="pedagogy.worked_example",
        category="pedagogy",
        display_name="Worked Example Scaffold",
        description="Structured problem solving scaffold with knowns, principles, steps, and final interpretation.",
        semantic_tags=["worked_example", "problem_solving", "calculation", "step_by_step", "math_steps"],
        supported_artifacts=["presentation", "document", "worksheet", "poster"],
        domain="general",
        complexity_score=3.0,
        preferred_renderer="html",
        taxonomy=TaxonomySignature(
            family=CapabilityFamily.STEPWISE_REASONING,
            primary_intent=SemanticIntent.DERIVE,
            supported_intents=[SemanticIntent.EXPLAIN, SemanticIntent.SEQUENCE],
            structure=InformationStructure.TRANSFORMATION,
            pedagogical_role=PedagogicalRole.WORKED_EXAMPLE,
            visual_grammar=VisualGrammar.EQUATION_CHAIN,
            density=DensityProfile.ANALYTICAL,
            preferred_formats=["presentation_16_9", "a4_portrait", "a4_landscape"],
        ),
    ),
    spec_model=WorkedExampleSpec,
    renderer=WorkedExampleRenderer(),
    parameter_extractor=_extract_worked_example,
)


# --- 2. Misconception Correction ---

class MisconceptionSpec(CapabilitySpec):
    common_belief: str
    why_it_seems_true: str
    counterexample: str
    correct_explanation: str
    topic: str | None = None


class MisconceptionRenderer(CapabilityRenderer[MisconceptionSpec]):

    def validate_spec(self, spec: MisconceptionSpec) -> bool:
        return bool(spec.common_belief and spec.correct_explanation)

    def measure(self, spec: MisconceptionSpec, context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"estimated_height_px": 350, "density": "medium"}

    def render(self, spec: MisconceptionSpec, context: dict[str, Any] | None = None) -> CapabilityOutput:
        html = f"""
        <div class="capability-misconception-card">
            <div class="misconception-header">
                <span class="badge warning-badge">Common Misconception</span>
                {f'<span class="topic-tag">{spec.topic}</span>' if spec.topic else ''}
            </div>
            <div class="misconception-grid">
                <div class="card false-belief-card">
                    <div class="card-icon">❌</div>
                    <h4>Common Belief</h4>
                    <p class="belief-text">"{spec.common_belief}"</p>
                    <div class="intuition-note"><strong>Why it seems intuitive:</strong> {spec.why_it_seems_true}</div>
                </div>
                <div class="card correct-model-card">
                    <div class="card-icon">✅</div>
                    <h4>Scientific Reality</h4>
                    <p class="explanation-text">{spec.correct_explanation}</p>
                    <div class="counterexample-box"><strong>Counterexample:</strong> {spec.counterexample}</div>
                </div>
            </div>
        </div>
        """
        return CapabilityOutput(
            capability_id="pedagogy.misconception_correction",
            output_format="html",
            rendered_content=html,
            width_px=750,
            height_px=350,
        )


def _extract_misconception(step: Any, material: Any) -> dict[str, Any]:
    title = material.content.metadata.title
    misc = material.content.misconceptions[0] if material.content.misconceptions else None
    if misc:
        return {
            "common_belief": misc.common_belief,
            "why_it_seems_true": misc.why_it_seems_true,
            "counterexample": misc.counterexample,
            "correct_explanation": misc.correct_explanation,
            "topic": title,
        }
    return {
        "common_belief": "Common intuitive assumption",
        "why_it_seems_true": "Superficial observation",
        "counterexample": "Rigorous experimental finding",
        "correct_explanation": "Scientific theoretical model",
        "topic": title,
    }


misconception_capability = Capability(
    metadata=CapabilityMetadata(
        capability_id="pedagogy.misconception_correction",
        category="pedagogy",
        display_name="Misconception Correction Card",
        description="Side-by-side contrast between an intuitive misconception and the accurate scientific explanation.",
        semantic_tags=["misconception", "intuition", "counterexample", "conceptual_change", "correction"],
        supported_artifacts=["presentation", "document", "worksheet"],
        domain="general",
        complexity_score=2.0,
        preferred_renderer="html",
        taxonomy=TaxonomySignature(
            family=CapabilityFamily.COMPARATIVE_REASONING,
            primary_intent=SemanticIntent.COMPARE,
            supported_intents=[SemanticIntent.EXPLAIN, SemanticIntent.ARGUE],
            structure=InformationStructure.MATRIX,
            pedagogical_role=PedagogicalRole.MISCONCEPTION,
            visual_grammar=VisualGrammar.COMPARISON,
            density=DensityProfile.FOCUSED,
            preferred_formats=["presentation_16_9", "a4_landscape", "a4_portrait"],
        ),
    ),
    spec_model=MisconceptionSpec,
    renderer=MisconceptionRenderer(),
    parameter_extractor=_extract_misconception,
)
