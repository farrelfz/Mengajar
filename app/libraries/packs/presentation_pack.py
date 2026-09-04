"""
Presentation & High-Impact Communication Domain Pack.

Provides slide storytelling, hook panels, executive takeaways, and narrative transformation structures.
"""

from app.capabilities.contracts import CapabilityMetadata
from app.capabilities.families.factory import register_family_capability
from app.capabilities.registry import CapabilityRegistry
from app.capabilities.taxonomy import (
    CapabilityFamily,
    DensityProfile,
    InformationStructure,
    PedagogicalRole,
    SemanticIntent,
    TaxonomySignature,
    VisualGrammar,
)


def register_presentation_pack(registry: CapabilityRegistry) -> None:
    """Register all high-impact presentation capabilities into registry."""

    # 1. Problem Tension Hook
    register_family_capability(
        registry=registry,
        capability_id="presentation.problem_hook",
        template_id="collection.grid",
        metadata=CapabilityMetadata(
            capability_id="presentation.problem_hook",
            category="presentation",
            display_name="Dramatic Problem Hook & Tension Card",
            description="High-contrast opening slide presenting an urgent real-world paradox or unanswered question",
            semantic_tags=["hook", "problem_tension", "opening_slide", "attention_grabber", "storytelling"],
            supported_artifacts=["presentation", "document", "poster"],
            domain="presentation",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.CONCEPT_STRUCTURE,
                primary_intent=SemanticIntent.HOOK,
                structure=InformationStructure.SINGLE_ENTITY,
                pedagogical_role=PedagogicalRole.HOOK,
                visual_grammar=VisualGrammar.HERO,
                density=DensityProfile.MINIMAL,
            ),
        ),
    )

    # 2. Big Idea Callout
    register_family_capability(
        registry=registry,
        capability_id="presentation.big_idea",
        template_id="collection.grid",
        metadata=CapabilityMetadata(
            capability_id="presentation.big_idea",
            category="presentation",
            display_name="Executive Big Idea Banner",
            description="Full-bleed visual statement highlighting the single most critical paradigm shift of the presentation",
            semantic_tags=["big_idea", "core_message", "paradigm_shift", "takeaway_banner"],
            supported_artifacts=["presentation", "poster"],
            domain="presentation",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.CONCEPT_STRUCTURE,
                primary_intent=SemanticIntent.HOOK,
                structure=InformationStructure.SINGLE_ENTITY,
                pedagogical_role=PedagogicalRole.EXPLANATION,
                visual_grammar=VisualGrammar.HERO,
                density=DensityProfile.MINIMAL,
            ),
        ),
    )

    # 3. Narrative Arc Storyboard
    register_family_capability(
        registry=registry,
        capability_id="presentation.narrative_arc",
        template_id="process.linear",
        metadata=CapabilityMetadata(
            capability_id="presentation.narrative_arc",
            category="presentation",
            display_name="Presentation Narrative Arc Storyboard",
            description="5-part storytelling arc: Status Quo → Inciting Challenge → Exploration → Resolution → New Vision",
            semantic_tags=["narrative_arc", "storyboard", "presentation_flow", "rhetorical_arc"],
            supported_artifacts=["presentation", "document"],
            domain="presentation",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.PROCESS_VISUALIZATION,
                primary_intent=SemanticIntent.SEQUENCE,
                structure=InformationStructure.LINEAR_SEQUENCE,
                pedagogical_role=PedagogicalRole.INTRODUCTION,
                visual_grammar=VisualGrammar.PROCESS_FLOW,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 4. Final Call to Action & Reflection
    register_family_capability(
        registry=registry,
        capability_id="presentation.call_to_action",
        template_id="collection.grid",
        metadata=CapabilityMetadata(
            capability_id="presentation.call_to_action",
            category="presentation",
            display_name="Call to Action & Future Horizon",
            description="Closing presentation card mobilizing audience next steps, research directions, and key inquiry questions",
            semantic_tags=["call_to_action", "closing_slide", "next_steps", "future_horizon"],
            supported_artifacts=["presentation", "poster"],
            domain="presentation",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.CONCEPT_STRUCTURE,
                primary_intent=SemanticIntent.SYNTHESIZE,
                structure=InformationStructure.SINGLE_ENTITY,
                pedagogical_role=PedagogicalRole.SYNTHESIS,
                visual_grammar=VisualGrammar.HERO,
                density=DensityProfile.MINIMAL,
            ),
        ),
    )

    # 5. Question Hook Card
    register_family_capability(
        registry=registry,
        capability_id="presentation.question_hook",
        template_id="collection.grid",
        metadata=CapabilityMetadata(
            capability_id="presentation.question_hook",
            category="presentation",
            display_name="Provocative Inquiry & Question Hook",
            description="High-engagement opening slide posing a foundational question to stimulate audience curiosity",
            semantic_tags=["question_hook", "inquiry", "opening", "curiosity_driver"],
            supported_artifacts=["presentation", "document", "poster"],
            domain="presentation",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.CONCEPT_STRUCTURE,
                primary_intent=SemanticIntent.HOOK,
                structure=InformationStructure.SINGLE_ENTITY,
                pedagogical_role=PedagogicalRole.HOOK,
                visual_grammar=VisualGrammar.HERO,
                density=DensityProfile.MINIMAL,
            ),
        ),
    )

    # 6. Executive Visual Summary
    register_family_capability(
        registry=registry,
        capability_id="presentation.visual_summary",
        template_id="collection.grid",
        metadata=CapabilityMetadata(
            capability_id="presentation.visual_summary",
            category="presentation",
            display_name="Executive Visual Summary Dashboard",
            description="Clean 3-panel dashboard synthesizing key project metrics, milestones, and impacts",
            semantic_tags=["visual_summary", "executive_dashboard", "overview_slide", "metrics"],
            supported_artifacts=["presentation", "document", "poster"],
            domain="presentation",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.CONCEPT_STRUCTURE,
                primary_intent=SemanticIntent.SYNTHESIZE,
                structure=InformationStructure.MATRIX,
                pedagogical_role=PedagogicalRole.SYNTHESIS,
                visual_grammar=VisualGrammar.CONCEPT_PANEL,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 7. Problem-Tension-Solution Sequence
    register_family_capability(
        registry=registry,
        capability_id="presentation.problem_tension_solution",
        template_id="process.linear",
        metadata=CapabilityMetadata(
            capability_id="presentation.problem_tension_solution",
            category="presentation",
            display_name="Problem-Tension-Solution Rhetorical Flow",
            description="3-stage narrative presentation arc: Current Friction → Critical Tension → Breakthrough Solution",
            semantic_tags=["pitch_flow", "problem_solution", "rhetoric", "presentation_flow"],
            supported_artifacts=["presentation", "document"],
            domain="presentation",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.PROCESS_VISUALIZATION,
                primary_intent=SemanticIntent.SEQUENCE,
                structure=InformationStructure.LINEAR_SEQUENCE,
                pedagogical_role=PedagogicalRole.EXPLANATION,
                visual_grammar=VisualGrammar.PROCESS_FLOW,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )
