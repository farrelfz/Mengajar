"""
Academic Writing & Essay Composition Domain Pack.

Provides structural and argumentation components for academic essays, paragraph logic, and thesis building.
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


def register_academic_writing_pack(registry: CapabilityRegistry) -> None:
    """Register all academic writing capabilities into registry."""

    # 1. Paragraph Anatomy
    register_family_capability(
        registry=registry,
        capability_id="writing.paragraph_anatomy",
        template_id="process.linear",
        metadata=CapabilityMetadata(
            capability_id="writing.paragraph_anatomy",
            category="academic_writing",
            display_name="Paragraph Anatomy & Structure Flow",
            description="4-part academic paragraph flow: Topic Sentence → Evidence/Data → Critical Analysis → Concluding Transition",
            semantic_tags=["paragraph_structure", "topic_sentence", "evidence_integration", "analytical_flow", "writing"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="academic_writing",
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

    # 2. Thesis & Argument Map
    register_family_capability(
        registry=registry,
        capability_id="writing.thesis_argument_map",
        template_id="hierarchy.tree",
        metadata=CapabilityMetadata(
            capability_id="writing.thesis_argument_map",
            category="academic_writing",
            display_name="Thesis & Argument Hierarchy Map",
            description="Hierarchical decomposition of central thesis statement into supporting claims, sub-arguments, and evidence",
            semantic_tags=["thesis_statement", "argument_map", "claims_hierarchy", "essay_structure"],
            supported_artifacts=["presentation", "document", "poster"],
            domain="academic_writing",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.CONCEPT_STRUCTURE,
                primary_intent=SemanticIntent.CLASSIFY,
                structure=InformationStructure.HIERARCHY,
                pedagogical_role=PedagogicalRole.SCAFFOLD,
                visual_grammar=VisualGrammar.CONCEPT_MAP,
                density=DensityProfile.ANALYTICAL,
            ),
        ),
    )

    # 3. Counterargument & Refutation
    register_family_capability(
        registry=registry,
        capability_id="writing.counterargument_refutation",
        template_id="comparison.matrix",
        metadata=CapabilityMetadata(
            capability_id="writing.counterargument_refutation",
            category="academic_writing",
            display_name="Counterargument & Refutation Framework",
            description="Contrasts opposing scholarly objections against principled empirical refutations and boundary caveats",
            semantic_tags=["counterargument", "refutation", "objections", "dialectical_writing", "scholarly_rigor"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="academic_writing",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.COMPARATIVE_REASONING,
                primary_intent=SemanticIntent.COMPARE,
                structure=InformationStructure.MATRIX,
                pedagogical_role=PedagogicalRole.ANALYSIS,
                visual_grammar=VisualGrammar.COMPARISON,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 4. Essay Outline & Progression
    register_family_capability(
        registry=registry,
        capability_id="writing.essay_outline",
        template_id="progression.ladder",
        metadata=CapabilityMetadata(
            capability_id="writing.essay_outline",
            category="academic_writing",
            display_name="Essay Structural Progression Ladder",
            description="Section-by-section outline ladder: Introduction Hook → Literature Context → Core Argument → Synthesis",
            semantic_tags=["essay_outline", "essay_development", "writing_roadmap", "drafting_scaffold"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="academic_writing",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.STEPWISE_REASONING,
                primary_intent=SemanticIntent.SEQUENCE,
                structure=InformationStructure.LINEAR_SEQUENCE,
                pedagogical_role=PedagogicalRole.SCAFFOLD,
                visual_grammar=VisualGrammar.CHECKPOINT_CARD,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 5. Coherence & Transition Connectors
    register_family_capability(
        registry=registry,
        capability_id="writing.coherence_flow",
        template_id="process.linear",
        metadata=CapabilityMetadata(
            capability_id="writing.coherence_flow",
            category="academic_writing",
            display_name="Argumentative Coherence & Transition Flow",
            description="Ensures smooth logical transitions between major claims and narrative sections",
            semantic_tags=["coherence", "transitions", "signposting", "flow", "academic_prose"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="academic_writing",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.PROCESS_VISUALIZATION,
                primary_intent=SemanticIntent.SEQUENCE,
                structure=InformationStructure.LINEAR_SEQUENCE,
                pedagogical_role=PedagogicalRole.SCAFFOLD,
                visual_grammar=VisualGrammar.PROCESS_FLOW,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 6. Revision & Peer Review Cycle
    register_family_capability(
        registry=registry,
        capability_id="writing.revision_cycle",
        template_id="process.linear",
        metadata=CapabilityMetadata(
            capability_id="writing.revision_cycle",
            category="academic_writing",
            display_name="Scholarly Revision & Peer Review Protocol",
            description="4-step iterative editing workflow: Structural Alignment → Argument Tightening → Prose Polish → Citation Check",
            semantic_tags=["revision_cycle", "peer_review", "editing", "proofreading", "scholarly_refinement"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="academic_writing",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.PROCESS_VISUALIZATION,
                primary_intent=SemanticIntent.SEQUENCE,
                structure=InformationStructure.LINEAR_SEQUENCE,
                pedagogical_role=PedagogicalRole.SCAFFOLD,
                visual_grammar=VisualGrammar.PROCESS_FLOW,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 7. Introduction Structure Flow
    register_family_capability(
        registry=registry,
        capability_id="writing.introduction_structure",
        template_id="process.linear",
        metadata=CapabilityMetadata(
            capability_id="writing.introduction_structure",
            category="academic_writing",
            display_name="Academic Introduction Funnel Flow",
            description="3-tier funnel: Broad Hook/Context → Scholarly Problem/Gap → Explicit Thesis & Map",
            semantic_tags=["introduction", "opening_funnel", "hook_to_thesis", "essay_introduction"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="academic_writing",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.PROCESS_VISUALIZATION,
                primary_intent=SemanticIntent.SEQUENCE,
                structure=InformationStructure.LINEAR_SEQUENCE,
                pedagogical_role=PedagogicalRole.SCAFFOLD,
                visual_grammar=VisualGrammar.PROCESS_FLOW,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 8. Conclusion Synthesis Architecture
    register_family_capability(
        registry=registry,
        capability_id="writing.conclusion_structure",
        template_id="process.linear",
        metadata=CapabilityMetadata(
            capability_id="writing.conclusion_structure",
            category="academic_writing",
            display_name="Academic Conclusion & Synthesis Flow",
            description="Reverse funnel: Restate Thesis in New Light → Synthesize Main Insights → Broader Scholarly Implications",
            semantic_tags=["conclusion", "reverse_funnel", "synthesis", "closing_paragraph", "essay_conclusion"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="academic_writing",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.PROCESS_VISUALIZATION,
                primary_intent=SemanticIntent.SEQUENCE,
                structure=InformationStructure.LINEAR_SEQUENCE,
                pedagogical_role=PedagogicalRole.SYNTHESIS,
                visual_grammar=VisualGrammar.PROCESS_FLOW,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 9. Argument Chain & Warrant
    register_family_capability(
        registry=registry,
        capability_id="writing.argument_chain",
        template_id="reasoning.evidence_chain",
        metadata=CapabilityMetadata(
            capability_id="writing.argument_chain",
            category="academic_writing",
            display_name="Toulmin Argument Chain & Warrant",
            description="Rigorous argumentative breakdown: Claim → Data/Backing → Warrant → Qualifier",
            semantic_tags=["toulmin", "argumentation", "warrant", "qualifier", "persuasive_writing"],
            supported_artifacts=["presentation", "document", "poster"],
            domain="academic_writing",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.EVIDENCE_ANALYSIS,
                primary_intent=SemanticIntent.ARGUE,
                structure=InformationStructure.EVIDENCE_CHAIN,
                pedagogical_role=PedagogicalRole.ANALYSIS,
                visual_grammar=VisualGrammar.REASONING_FLOW,
                density=DensityProfile.ANALYTICAL,
            ),
        ),
    )
