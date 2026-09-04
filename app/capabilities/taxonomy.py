"""
KIR AI Document Intelligence — Capability Grammar & Taxonomy.

Defines the multi-axis canonical taxonomy governing all capabilities:
- SemanticIntent (Cognitive need)
- InformationStructure (Intrinsic data shape)
- PedagogicalRole (Learning stage / function)
- VisualGrammar (Visual archetype)
- DensityProfile (Information density capacity)
- CapabilityFamily (Reusable grammatical archetype)
"""

from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


class SemanticIntent(str, Enum):
    """The cognitive / semantic problem a capability solves."""
    EXPLAIN = "explain"
    COMPARE = "compare"
    SEQUENCE = "sequence"
    DERIVE = "derive"
    CLASSIFY = "classify"
    RELATE = "relate"
    ANALYZE = "analyze"
    ARGUE = "argue"
    INVESTIGATE = "investigate"
    NARROW_SCOPE = "narrow_scope"
    ASSESS = "assess"
    EVALUATE = "evaluate"
    SYNTHESIZE = "synthesize"
    INTRODUCE = "introduce"
    HOOK = "hook"


class InformationStructure(str, Enum):
    """The intrinsic structural topology of the consumed information."""
    LINEAR_SEQUENCE = "linear_sequence"
    HIERARCHY = "hierarchy"
    MATRIX = "matrix"
    NETWORK = "network"
    MAPPING = "mapping"
    TRANSFORMATION = "transformation"
    SPATIAL_SYSTEM = "spatial_system"
    EQUATION_SYSTEM = "equation_system"
    EVIDENCE_CHAIN = "evidence_chain"
    QUESTION_SET = "question_set"
    CYCLE = "cycle"
    SINGLE_ENTITY = "single_entity"


class PedagogicalRole(str, Enum):
    """The pedagogical / instructional function in the learner's journey."""
    HOOK = "hook"
    INTRODUCTION = "introduction"
    EXPLANATION = "explanation"
    SCAFFOLD = "scaffold"
    WORKED_EXAMPLE = "worked_example"
    MISCONCEPTION = "misconception"
    ANALYSIS = "analysis"
    PRACTICE = "practice"
    ASSESSMENT = "assessment"
    SYNTHESIS = "synthesis"
    REFERENCE = "reference"


class VisualGrammar(str, Enum):
    """The concrete visual representation paradigm."""
    HERO = "hero"
    CONCEPT_PANEL = "concept_panel"
    PROCESS_FLOW = "process_flow"
    TIMELINE = "timeline"
    FUNNEL = "funnel"
    COMPARISON = "comparison"
    MATRIX = "matrix"
    ANNOTATED_DIAGRAM = "annotated_diagram"
    EQUATION_CHAIN = "equation_chain"
    CONCEPT_MAP = "concept_map"
    CHECKPOINT_CARD = "checkpoint_card"
    REASONING_FLOW = "reasoning_flow"
    TABLE = "table"


class DensityProfile(str, Enum):
    """The appropriate information density and spatial capacity."""
    MINIMAL = "minimal"           # 1 focal item (e.g. Hero statement)
    FOCUSED = "focused"           # 2-4 items (standard card, single vector diagram)
    ANALYTICAL = "analytical"     # 4-8 items (multi-step worked example, gap matrix)
    DENSE_REFERENCE = "dense_reference"  # 8+ items (comprehensive methodology matrix, data table)


class CapabilityFamily(str, Enum):
    """The reusable grammatical archetype grouping capabilities across domains."""
    TITLE_FRAMING = "title_framing"
    CONCEPT_STRUCTURE = "concept_structure"
    PROCESS_VISUALIZATION = "process_visualization"
    COMPARATIVE_REASONING = "comparative_reasoning"
    STEPWISE_REASONING = "stepwise_reasoning"
    SPATIAL_SYSTEMS = "spatial_systems"
    EVIDENCE_ANALYSIS = "evidence_analysis"
    RELATIONSHIP_MAPPING = "relationship_mapping"
    QUANTITATIVE_ANALYSIS = "quantitative_analysis"
    ASSESSMENT_CHECKPOINT = "assessment_checkpoint"


class TaxonomySignature(BaseModel):
    """Complete multi-axis signature describing a capability's grammatical identity."""
    family: CapabilityFamily
    primary_intent: SemanticIntent
    supported_intents: list[SemanticIntent] = Field(default_factory=list)
    structure: InformationStructure
    pedagogical_role: PedagogicalRole
    visual_grammar: VisualGrammar
    density: DensityProfile = DensityProfile.FOCUSED
    preferred_formats: list[str] = Field(default_factory=lambda: ["presentation_16_9", "a4_landscape", "a4_portrait"])

    def matches_query(
        self,
        intent: SemanticIntent | str | None = None,
        structure: InformationStructure | str | None = None,
        role: PedagogicalRole | str | None = None,
        grammar: VisualGrammar | str | None = None,
        family: CapabilityFamily | str | None = None,
        density: DensityProfile | str | None = None,
        format_id: str | None = None,
    ) -> bool:
        """Evaluate intersection query against taxonomy signature."""
        if intent:
            intent_val = SemanticIntent(intent) if isinstance(intent, str) else intent
            if self.primary_intent != intent_val and intent_val not in self.supported_intents:
                return False
        if structure:
            struct_val = InformationStructure(structure) if isinstance(structure, str) else structure
            if self.structure != struct_val:
                return False
        if role:
            role_val = PedagogicalRole(role) if isinstance(role, str) else role
            if self.pedagogical_role != role_val:
                return False
        if grammar:
            gram_val = VisualGrammar(grammar) if isinstance(grammar, str) else grammar
            if self.visual_grammar != gram_val:
                return False
        if family:
            fam_val = CapabilityFamily(family) if isinstance(family, str) else family
            if self.family != fam_val:
                return False
        if density:
            dens_val = DensityProfile(density) if isinstance(density, str) else density
            if self.density != dens_val:
                return False
        if format_id and format_id not in self.preferred_formats:
            return False
        return True
