"""
KIR AI Document Intelligence — Pedagogy Scaffolding & Assessment Library.

Provides parameterized learning scaffolds:
- Question Progression Ladder
- Concept Checkpoint (Formative Assessment)
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


# =====================================================================
# 1. Question Progression Ladder
# =====================================================================

class ScaffoldingQuestion(BaseModel):
    level: int
    prompt: str
    target_cognitive_depth: str  # "Recall", "Application", "Analysis", "Evaluation"
    hint: str | None = None


class QuestionProgressionSpec(CapabilitySpec):
    topic: str
    questions: list[ScaffoldingQuestion] = Field(default_factory=list)


class QuestionProgressionRenderer(CapabilityRenderer[QuestionProgressionSpec]):

    def validate_spec(self, spec: QuestionProgressionSpec) -> bool:
        return len(spec.questions) > 0

    def measure(self, spec: QuestionProgressionSpec, context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"height_px": len(spec.questions) * 80 + 130}

    def render(self, spec: QuestionProgressionSpec, context: dict[str, Any] | None = None) -> CapabilityOutput:
        q_html = ""
        for q in spec.questions:
            q_html += f"""
            <div class="scaffold-question-row">
                <div class="level-pill">Level {q.level}: {q.target_cognitive_depth}</div>
                <div class="question-text">{q.prompt}</div>
                {f'<div class="question-hint">💡 <em>Hint: {q.hint}</em></div>' if q.hint else ''}
            </div>
            """

        html = f"""
        <div class="capability-question-progression card">
            <div class="progression-header">
                <span class="badge scaffold-badge">Scaffolded Inquiry Ladder</span>
                <h3>{spec.topic}</h3>
            </div>
            <div class="question-ladder-body">
                {q_html}
            </div>
        </div>
        """
        return CapabilityOutput(
            capability_id="pedagogy.question_progression",
            output_format="html",
            rendered_content=html,
            width_px=750,
            height_px=len(spec.questions) * 80 + 130,
        )


def _extract_question_progression(step: Any, material: Any) -> dict[str, Any]:
    title = material.content.metadata.title
    return {
        "topic": f"Inquiry Progression: {title}",
        "questions": [
            ScaffoldingQuestion(level=1, prompt=f"Define the foundational terms and units in {title}.", target_cognitive_depth="Recall", hint="Refer to standard definitions."),
            ScaffoldingQuestion(level=2, prompt=f"Calculate the resulting outcome when force and distance change.", target_cognitive_depth="Application", hint="Apply governing equations."),
            ScaffoldingQuestion(level=3, prompt=f"What happens if conditions violate equilibrium assumptions?", target_cognitive_depth="Analysis", hint="Consider rotational acceleration."),
        ],
    }


question_progression_capability = Capability(
    metadata=CapabilityMetadata(
        capability_id="pedagogy.question_progression",
        category="pedagogy",
        display_name="Scaffolded Question Progression Ladder",
        description="Progressive series of questions scaffolding Bloom's taxonomy from recall to deep evaluation.",
        semantic_tags=["question_ladder", "scaffold", "inquiry", "blooms_taxonomy", "guided_practice", "questions"],
        supported_artifacts=["presentation", "document", "worksheet"],
        domain="general",
        complexity_score=2.0,
        preferred_renderer="html",
        taxonomy=TaxonomySignature(
            family=CapabilityFamily.STEPWISE_REASONING,
            primary_intent=SemanticIntent.INVESTIGATE,
            supported_intents=[SemanticIntent.EXPLAIN, SemanticIntent.ANALYZE],
            structure=InformationStructure.QUESTION_SET,
            pedagogical_role=PedagogicalRole.SCAFFOLD,
            visual_grammar=VisualGrammar.CHECKPOINT_CARD,
            density=DensityProfile.FOCUSED,
            preferred_formats=["presentation_16_9", "a4_portrait", "a4_landscape"],
        ),
    ),
    spec_model=QuestionProgressionSpec,
    renderer=QuestionProgressionRenderer(),
    parameter_extractor=_extract_question_progression,
)


# =====================================================================
# 2. Concept Checkpoint (Formative Assessment)
# =====================================================================

class CheckpointQuestion(BaseModel):
    prompt: str
    options: list[str] = Field(default_factory=list)
    correct_option_index: int = 0
    explanation: str


class ConceptCheckpointSpec(CapabilitySpec):
    checkpoint_title: str = "Concept Checkpoint"
    questions: list[CheckpointQuestion] = Field(default_factory=list)


class ConceptCheckpointRenderer(CapabilityRenderer[ConceptCheckpointSpec]):

    def validate_spec(self, spec: ConceptCheckpointSpec) -> bool:
        return len(spec.questions) > 0

    def measure(self, spec: ConceptCheckpointSpec, context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"height_px": len(spec.questions) * 160 + 100}

    def render(self, spec: ConceptCheckpointSpec, context: dict[str, Any] | None = None) -> CapabilityOutput:
        body_html = ""
        for idx, q in enumerate(spec.questions, 1):
            opts_html = "".join(f"""
            <li class="checkpoint-opt {'opt-correct' if o_idx == q.correct_option_index else ''}">
                <span class="opt-label">{chr(65 + o_idx)}.</span> {opt}
            </li>
            """ for o_idx, opt in enumerate(q.options))

            body_html += f"""
            <div class="checkpoint-item">
                <div class="check-q-prompt"><strong>Q{idx}.</strong> {q.prompt}</div>
                <ul class="check-options-list">
                    {opts_html}
                </ul>
                <div class="check-explanation"><strong>Rationale:</strong> {q.explanation}</div>
            </div>
            """

        html = f"""
        <div class="capability-concept-checkpoint card">
            <div class="checkpoint-header">
                <span class="badge assess-badge">Formative Checkpoint</span>
                <h3>{spec.checkpoint_title}</h3>
            </div>
            <div class="checkpoint-body">
                {body_html}
            </div>
        </div>
        """
        return CapabilityOutput(
            capability_id="pedagogy.concept_checkpoint",
            output_format="html",
            rendered_content=html,
            width_px=750,
            height_px=len(spec.questions) * 160 + 100,
        )


def _extract_concept_checkpoint(step: Any, material: Any) -> dict[str, Any]:
    title = material.content.metadata.title
    return {
        "checkpoint_title": f"Quick Check: {title}",
        "questions": [
            CheckpointQuestion(
                prompt=f"Which condition produces maximal effect in {title}?",
                options=["Perpendicular alignment (90 deg)", "Parallel alignment (0 deg)", "Zero lever arm", "Random force orientation"],
                correct_option_index=0,
                explanation="Sine of 90 degrees equals 1.0, maximizing turning leverage.",
            )
        ],
    }


concept_checkpoint_capability = Capability(
    metadata=CapabilityMetadata(
        capability_id="pedagogy.concept_checkpoint",
        category="pedagogy",
        display_name="Formative Concept Checkpoint",
        description="Formative assessment checkpoint with multiple-choice verification and immediate pedagogical rationale.",
        semantic_tags=["assessment", "checkpoint", "quiz", "formative", "concept_check", "evaluation"],
        supported_artifacts=["presentation", "document", "worksheet"],
        domain="general",
        complexity_score=1.5,
        preferred_renderer="html",
        taxonomy=TaxonomySignature(
            family=CapabilityFamily.ASSESSMENT_CHECKPOINT,
            primary_intent=SemanticIntent.ASSESS,
            supported_intents=[SemanticIntent.EVALUATE, SemanticIntent.EXPLAIN],
            structure=InformationStructure.QUESTION_SET,
            pedagogical_role=PedagogicalRole.ASSESSMENT,
            visual_grammar=VisualGrammar.CHECKPOINT_CARD,
            density=DensityProfile.FOCUSED,
            preferred_formats=["presentation_16_9", "a4_portrait", "a4_landscape"],
        ),
    ),
    spec_model=ConceptCheckpointSpec,
    renderer=ConceptCheckpointRenderer(),
    parameter_extractor=_extract_concept_checkpoint,
)
