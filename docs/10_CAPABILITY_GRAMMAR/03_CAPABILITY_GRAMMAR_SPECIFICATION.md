# 03 — Capability Grammar Specification

## Mathematical Formalism

A capability in the KIR AI Architecture is formally defined as a tuple across orthogonal axes:

$$\text{Capability} = \langle \mathcal{I}_\text{semantic}, \mathcal{S}_\text{info}, \mathcal{R}_\text{pedagogy}, \mathcal{G}_\text{visual}, \mathcal{D}_\text{density}, \mathcal{C}_\text{domain}, \mathcal{F}_\text{formats} \rangle$$

Where:
1. **$\mathcal{I}_\text{semantic} \in \text{SemanticIntent}$**: The cognitive or analytical goal (e.g. `EXPLAIN`, `COMPARE`, `SEQUENCE`, `DERIVE`, `CLASSIFY`, `RELATE`, `ANALYZE`, `ARGUE`, `INVESTIGATE`, `NARROW_SCOPE`, `ASSESS`, `SYNTHESIZE`, `INTRODUCE`, `HOOK`).
2. **$\mathcal{S}_\text{info} \in \text{InformationStructure}$**: The structural topology of data (e.g. `LINEAR_SEQUENCE`, `HIERARCHY`, `MATRIX`, `NETWORK`, `MAPPING`, `TRANSFORMATION`, `SPATIAL_SYSTEM`, `EVIDENCE_CHAIN`, `QUESTION_SET`, `SINGLE_ENTITY`).
3. **$\mathcal{R}_\text{pedagogy} \in \text{PedagogicalRole}$**: The instructional function in the learner's journey (e.g. `HOOK`, `INTRODUCTION`, `EXPLANATION`, `WORKED_EXAMPLE`, `MISCONCEPTION`, `ANALYSIS`, `SYNTHESIS`, `ASSESSMENT`, `SCAFFOLD`, `REFERENCE`).
4. **$\mathcal{G}_\text{visual} \in \text{VisualGrammar}$**: The concrete layout idiom rendered (e.g. `HERO`, `CONCEPT_PANEL`, `PROCESS_FLOW`, `COMPARISON`, `ANNOTATED_DIAGRAM`, `EQUATION_CHAIN`, `MATRIX`, `FUNNEL`, `CHECKPOINT_CARD`, `REASONING_FLOW`, `CONCEPT_MAP`, `TABLE`).
5. **$\mathcal{D}_\text{density} \in \text{DensityProfile}$**: Information density budget (e.g. `MINIMAL`, `FOCUSED`, `ANALYTICAL`, `DENSE_REFERENCE`).
6. **$\mathcal{C}_\text{domain}$**: Domain specificity constraint (`"general"`, `"physics"`, `"mathematics"`, `"research_education"`, etc.).
7. **$\mathcal{F}_\text{formats} \subset \text{PhysicalFormats}$**: Supported layout formats (e.g. `["presentation_16_9", "a4_portrait", "a4_landscape"]`).

## Declarative Contract

Every capability must attach a `TaxonomySignature` to its `CapabilityMetadata`:

```python
from app.capabilities.taxonomy import (
    CapabilityFamily,
    SemanticIntent,
    InformationStructure,
    PedagogicalRole,
    VisualGrammar,
    DensityProfile,
    TaxonomySignature,
)

taxonomy = TaxonomySignature(
    family=CapabilityFamily.COMPARATIVE_REASONING,
    primary_intent=SemanticIntent.COMPARE,
    supported_intents=[SemanticIntent.ANALYZE, SemanticIntent.EVALUATE],
    structure=InformationStructure.MATRIX,
    pedagogical_role=PedagogicalRole.ANALYSIS,
    visual_grammar=VisualGrammar.COMPARISON,
    density=DensityProfile.ANALYTICAL,
    preferred_formats=["a4_portrait", "a4_landscape", "presentation_16_9"],
)
```
