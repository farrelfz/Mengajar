# Phase 1A Universal Knowledge Intelligence Architecture Design

## 1. Design Goals

1. **Decouple Knowledge from Artifacts**: Establish a strictly artifact-neutral, format-neutral, and renderer-neutral Universal Knowledge Layer that answers solely: *"What does the source material know?"*
2. **Eliminate Format Collapse**: Provide dedicated, first-class structural transformation models for all four target formats (Presentation 16:9, Handout Lengkap A4, Student Worksheet / LKS, and Scientific Document / KTI Paper).
3. **Preserve Presentation System Maturity**: Guarantee 100% backward compatibility for the mature Presentation 16:9 pipeline (25 Quality Gates, Visual Grammar Matrix, Deterministic Repair Engine, and State Machine Invariants) via a zero-overhead compatibility adapter.
4. **Implement Full Traceability**: Provide bidirectional mapping between raw source markdown references, semantic knowledge units, artifact structural nodes, and rendered layout regions.
5. **Establish Immutability and Version Lineage**: Ensure that repair loops mutate only artifact architectures and page compositions, leaving the Universal Knowledge Manifest strictly immutable.
6. **Enforce Local-First & Selective AI Boundaries**: Restrict AI invocation to genuine semantic ambiguity resolution and conceptual relationship inference, keeping structural parsing, manifest compilation, layout composition, rendering, QA, and initial repair 100% deterministic or rule-based.

---

## 2. Non-Goals

1. **No Code Implementation in Phase 1A**: This phase is strictly dedicated to architectural design validation. No python code in `app/orchestration/production_pipeline.py`, `app/composition/bridge.py`, or `app/intelligence/` will be modified or deleted during Phase 1A.
2. **No Premature Deletion of Legacy Branch B**: Branch B in `MaterialProductionPipeline` will remain intact until Phase 1B/2 verification is complete.
3. **No Direct Layout or Visual Formatting in Knowledge Layer**: The Universal Knowledge Layer will NOT contain CSS classes, grid measurements, font sizes, slide counts, page counts, or column structures.
4. **No Artificial Unification of Artifact Intents**: We will not force Presentation, Handout, Worksheet, and Scientific Paper into a single generic layout template.

---

## 3. Core Architectural Principles

The architecture follows a strict 4-tier unidirectional data flow:

```
                          SOURCE KNOWLEDGE
                        (Markdown / PDF / Text)
                                   │
                                   ▼
                    UNIVERSAL KNOWLEDGE LAYER
                (UniversalKnowledgeManifest & Graph)
                                   │
                                   ▼
                         ARTIFACT INTENT LAYER
             (Communicative Goal & Pedagogical Strategy)
                                   │
       ┌───────────────────┬───────┴───────────┬───────────────────┐
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
 PRESENTATION 16:9   HANDOUT A4          WORKSHEET A4        SCIENTIFIC DOC (KTI)
 TRANSFORMER         TRANSFORMER         TRANSFORMER         TRANSFORMER
 (SlidePlan & Acts)  (Reading Chapters)  (Student Tasks)     (IMRAD/BAB 1-5)
       │                   │                   │                   │
       └───────────────────┼───────────────────┼───────────────────┘
                           │
                           ▼
                  PHYSICAL COMPOSITION
               (DocumentComposition & Pages)
                           │
                           ▼
                 MASTER RENDERING ENGINE
            (Jinja2 HTML + Playwright PDF)
                           │
                           ▼
              FORMAT-SPECIFIC QA & REPAIR LOOP
             (State Invalidation & Re-QA Round)
```

### Core separation:
- **Universal Knowledge Layer**: Answers *"WHAT DOES THE SOURCE KNOW?"*
- **Artifact Intent Layer**: Answers *"WHAT SHOULD THIS OUTPUT ACCOMPLISH?"*
- **Artifact Architecture Layer**: Answers *"HOW SHOULD KNOWLEDGE BE STRUCTURED FOR THIS FORMAT?"*
- **Composition & Rendering Layer**: Answers *"HOW IS THIS VISUALLY PRESENTED ON PHYSICAL CANVAS?"*

---

## 4. Universal Knowledge Ontology Options

We evaluated three potential architectural options for modeling the Universal Knowledge Layer:

### Option A: Highly Granular Polymorphic Schemas
- Separate Pydantic classes for `Concept`, `Claim`, `Evidence`, `Formula`, `Procedure`, `Observation`, `Question`, `Argument`, `Example`, `Warning`.
- **Pros**: Strict type checking for every domain concept.
- **Cons**: High schema bloat, complex serialization, rigid maintenance overhead when adding new domain types.

### Option B: Monolithic Flat KnowledgeUnit Schema
- A single generic `KnowledgeUnit` with a string `unit_type` and a dictionary payload `data: dict[str, Any]`.
- **Pros**: Simple, highly flexible.
- **Cons**: Lack of Pydantic validation, loss of IDE autocompletion, high risk of runtime `KeyError` exceptions.

### Option C: Hybrid Polymorphic Schema (Recommended)
- A unified, strongly-typed `KnowledgeUnit` containing common metadata (ID, provenance, criticality, importance) combined with a discriminated union payload (`KnowledgePayload`).
- Payload types map to existing codebase enums (`ContentType` in [schemas.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/intelligence/schemas.py)).

| Metric | Option A (Separate Schemas) | Option B (Flat Dict Payload) | Option C (Hybrid Discriminated Union) |
|---|---|---|---|
| Type Safety | High | Low | **High** |
| Extensibility | Low (Requires new classes) | High | **High** |
| Validation Precision | High | Low | **High** |
| Schema Complexity | High (15+ classes) | Very Low | **Balanced (1 container + 4 payloads)** |
| Traceability Coupling | High | Low | **Optimal** |

---

## 5. Recommended Knowledge Ontology

We adopt **Option C (Hybrid Discriminator)**. Existing domain concepts from [schemas.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/intelligence/schemas.py) (`ContentType`) and [content.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/blueprints/content.py) (`ConceptDefinition`, `FactStatement`, `WorkedExampleContent`) are unified under `KnowledgeUnit`.

### Unified Entity Hierarchy
1. **`KnowledgeUnit`**: The fundamental atomic unit of extracted knowledge.
2. **`KnowledgeCategory`**:
   - `CORE_CONCEPT`: Central theoretical definitions, models, laws.
   - `PROCEDURAL`: Step-by-step instructions, experimental protocols, methods.
   - `EMPIRICAL`: Observations, dataset tables, experimental results, measurements.
   - `FORMAL`: Mathematical equations, quantitative formulas, derivations.
   - `EVALUATIVE`: Arguments, claims, evidence, limitations, discussions.
   - `PEDAGOGICAL_STIMULUS`: Questions, misconceptions, warnings, reflection prompts.
3. **`KnowledgeProvenance`**: Exact source tracking (section ID, line numbers, block IDs, verbatim text snippet).
4. **`KnowledgeMetrics`**: Artifact-neutral importance score ($0.0 - 1.0$), criticality tier (`CRITICAL`, `IMPORTANT`, `SUPPORTING`), and ambiguity score.

---

## 6. UniversalKnowledgeManifest Schema Proposal

Below is the complete Pydantic contract proposal for `UniversalKnowledgeManifest`. Notice the **strict exclusion of slide or page counts**:

```python
from __future__ import annotations
from enum import Enum
from typing import Any, List, Dict, Optional, Union
from pydantic import BaseModel, Field

class CriticalityTier(str, Enum):
    CRITICAL = "critical"      # Must be addressed in all artifact formats
    IMPORTANT = "important"    # Essential for complete understanding
    SUPPORTING = "supporting"  # Contextual or supplementary detail

class RelationshipType(str, Enum):
    PREREQUISITE_OF = "prereq_of"
    CAUSES = "causes"
    EXPLAINED_BY = "explained_by"
    SUPPORTED_BY = "supported_by"
    MEASURED_BY = "measured_by"
    DEMONSTRATED_BY = "demonstrated_by"
    CONTRASTED_WITH = "contrasted_with"
    DERIVES_FROM = "derives_from"
    REFUTES = "refutes"

class KnowledgeProvenance(BaseModel):
    source_file: str
    section_id: str
    section_title: str
    block_ids: List[str] = Field(default_factory=list)
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    raw_snippet: str

class KnowledgeRelationship(BaseModel):
    source_unit_id: str
    target_unit_id: str
    relationship: RelationshipType
    confidence: float = 1.0
    notes: Optional[str] = None

class KnowledgeUnit(BaseModel):
    id: str
    title: str
    content_type: str  # Maps to app.intelligence.schemas.ContentType
    category: str      # CORE_CONCEPT, PROCEDURAL, EMPIRICAL, FORMAL, EVALUATIVE, STIMULUS
    criticality: CriticalityTier
    importance_score: float = Field(ge=0.0, le=1.0)
    summary: str
    detailed_text: str
    provenance: KnowledgeProvenance
    payload: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)

class UniversalKnowledgeManifest(BaseModel):
    """Authoritative, artifact-neutral manifest of source knowledge."""
    manifest_id: str
    document_title: str
    domain: str
    audience_level: str
    created_at: float
    
    # Atomic Units
    units: Dict[str, KnowledgeUnit] = Field(default_factory=dict)
    
    # Relationship Graph (DAG)
    relationships: List[KnowledgeRelationship] = Field(default_factory=list)
    
    # Index Views for Rapid Lookup
    critical_unit_ids: List[str] = Field(default_factory=list)
    concept_dependency_order: List[str] = Field(default_factory=list)
    
    # Source Metadata
    total_sections: int
    total_raw_blocks: int
    ambiguity_ratio: float = 0.0

    # ABSOLUTELY PROHIBITED IN THIS SCHEMA:
    # min_slides, max_slides, target_slides, page_count, layout, visual_intent,
    # font_size, column_count, imrad_headings, answer_space, css
```

---

## 7. Knowledge Relationship Graph

Knowledge is modeled as a **Directed Acyclic Graph (DAG)** to prevent circular reasoning and establish dependency-aware concept order:

```
[ Concept A: Titik Nyala ]
       │
       ├─ (prerequisite_of) ──► [ Concept B: Segitiga Api ]
       │                               │
       │                               ├─ (explained_by) ────► [ Mechanism C: Oxidative Reaction ]
       │                               │
       │                               └─ (demonstrated_by) ─► [ Experiment D: Hand Fire ]
       │                                                               │
       └─ (measured_by) ──────► [ Formula E: Q = m.c.dT ] ◄────────────┘
                                       │
                                       └─ (supported_by) ────► [ Data Table F: Temperature Measurements ]
```

### Minimum Relationship Taxonomy
1. `PREREQUISITE_OF`: Node A must be understood before Node B.
2. `EXPLAINED_BY`: Node A is an abstract concept; Node B provides the underlying mechanism.
3. `SUPPORTED_BY`: Node A is a claim/theory; Node B provides empirical data/evidence.
4. `MEASURED_BY`: Node A is a physical phenomenon; Node B is the quantitative formula/equation.
5. `DEMONSTRATED_BY`: Node A is a theoretical concept; Node B is a concrete experiment or worked example.
6. `CONTRASTED_WITH`: Node A and Node B present opposing or complementary perspectives.

---

## 8. Artifact Intent Layer

The `ArtifactIntent` layer bridges artifact-neutral knowledge to format-specific communicative goals.

### Conceptual Interface
```python
class ArtifactIntent(BaseModel):
    target_format_id: str
    primary_goal: str
    target_audience: str
    cognitive_depth: str  # INTRODUCTORY, CONCEPTUAL, PROCEDURAL, ANALYTICAL, RIGOROUS
    intent_functions: List[str]
```

### Comparison of the 4 Artifact Intents

| Intent Attribute | Presentation 16:9 | Handout Lengkap A4 | Student Worksheet / LKS | Scientific Document / KTI |
|---|---|---|---|---|
| **Primary Goal** | Progressive visual explanation & audience engagement | Independent deep reading & comprehensive mastery | Active student inquiry & hands-on problem solving | Formal scientific argumentation & peer review |
| **Communicative Pace** | Rapid, bite-sized (1-2 key ideas per slide) | Continuous narrative flow with detailed prose | Scaffolding steps (Observe → Predict → Test) | Structural academic hierarchy (BAB 1–5) |
| **Key Intent Functions** | `ENGAGE`, `ORIENT`, `EXPLAIN`, `VISUALIZE`, `COMPARE`, `REFLECT` | `INTRODUCE`, `EXPLAIN`, `ELABORATE`, `EXEMPLIFY`, `SUMMARIZE` | `OBSERVE`, `PREDICT`, `INVESTIGATE`, `RECORD`, `ANALYZE`, `CONCLUDE` | `CONTEXTUALIZE`, `DEFINE_PROBLEM`, `DESCRIBE_METHOD`, `PRESENT_DATA`, `DISCUSS` |
| **Cognitive Load Control** | Strict constraint per slide (< 1200 chars) | Sectional density balance (< 3500 chars/page) | Interactive space allocation (Answer boxes) | Formal academic density (IMRAD structure) |

---

## 9. Artifact Transformer Contract

The `IArtifactTransformer` interface transforms artifact-neutral knowledge into a format-specific architecture model **prior to layout composition**.

### Conceptual Interface Specification
```python
class IArtifactTransformer(ABC):
    @abstractmethod
    def transform(
        self,
        manifest: UniversalKnowledgeManifest,
        intent: ArtifactIntent,
        options: Optional[Dict[str, Any]] = None,
    ) -> ArtifactArchitecture:
        """Transforms Universal Knowledge into a Format-Specific Architecture Model."""
        pass
```

### Boundary Definitions
- **Input**: `UniversalKnowledgeManifest` + `ArtifactIntent`.
- **Output**: `ArtifactArchitecture` (format-specific tree structure, e.g., `SlidePlan`, `HandoutArchitecture`, `WorksheetArchitecture`, `ScientificDocumentArchitecture`).
- **Boundary Rule**: `ArtifactArchitecture` is **NOT** `DocumentComposition`. `ArtifactArchitecture` defines narrative structure, section grouping, and content allocation, whereas `DocumentComposition` defines physical page regions, CSS classes, and HTML blocks.

---

## 10. Artifact Architecture Models

### 10.1 Presentation Architecture (`SlidePlan` Adapter)
To preserve the mature Presentation engine, the transformer uses an adapter mapping `UniversalKnowledgeManifest` to the existing `SlidePlan` / `PlannedSlide` model.

```
UniversalKnowledgeManifest
  ↓ (PresentationArtifactTransformer)
PresentationAdapter
  ↓
SlidePlan (Acts, Storyboard, PlannedSlides, ClaimUnits, VisualIntents)
```

### 10.2 Handout Architecture (`HandoutArchitecture`)
Specifically designed for independent reading and comprehensive material delivery.

```python
class HandoutSection(BaseModel):
    section_id: str
    title: str
    section_type: str  # OVERVIEW, DEEP_DIVE, WORKED_EXAMPLE, COMPARISON, SUMMARY
    knowledge_unit_ids: List[str]
    body_prose: str
    visual_callouts: List[Dict[str, Any]] = Field(default_factory=list)
    key_takeaways: List[str] = Field(default_factory=list)

class HandoutArchitecture(BaseModel):
    document_title: str
    target_format: str = "a4_portrait"
    header_metadata: Dict[str, str]
    chapters: List[HandoutSection]
    appendices: List[HandoutSection] = Field(default_factory=list)
```

### 10.3 Worksheet Architecture (`WorksheetArchitecture`)
Explicitly models student active learning, experimental investigation, and workspace allocation.

```python
class WorksheetTask(BaseModel):
    task_id: str
    task_number: int
    task_type: str  # PREDICTION, OBSERVATION, CALCULATION, ANALYSIS, REFLECTION
    prompt: str
    stimulus_unit_id: Optional[str] = None  # Reference to formula/data/diagram
    allocated_workspace_height_mm: float   # Space reserved for student writing
    points: int = 10
    answer_key: Optional[str] = None
    scoring_rubric: Optional[str] = None

class WorksheetActivityBlock(BaseModel):
    block_id: str
    title: str
    instruction: str
    tasks: List[WorksheetTask]

class WorksheetArchitecture(BaseModel):
    document_title: str
    student_header: Dict[str, str]  # Name, Class, Date, Group
    learning_objectives: List[str]
    stimulus_section: List[str]     # KnowledgeUnit IDs for background phenomenon
    activity_blocks: List[WorksheetActivityBlock]
    conclusion_prompt: WorksheetTask
    has_answer_key_appendix: bool = False
```

### 10.4 Scientific Document / KTI Architecture (`ScientificDocumentArchitecture`)
Structured specifically according to Indonesian KIR/KTI paper standards and formal academic conventions (BAB I–V).

```python
class ScientificSectionNode(BaseModel):
    section_code: str  # e.g., "BAB_1_PENDAHULUAN", "1.1_LATAR_BELAKANG", "BAB_4_HASIL"
    heading_title: str
    level: int         # 1 for BAB, 2 for Sub-bab, 3 for Sub-sub-bab
    knowledge_unit_ids: List[str]
    prose_content: str
    table_references: List[str] = Field(default_factory=list)
    figure_references: List[str] = Field(default_factory=list)
    citation_keys: List[str] = Field(default_factory=list)

class ScientificDocumentArchitecture(BaseModel):
    paper_title: str
    authors: List[str]
    institution: str
    abstract_id: str
    keywords: List[str]
    sections: List[ScientificSectionNode]
    bibliography_entries: List[Dict[str, str]]
    appendices: List[ScientificSectionNode] = Field(default_factory=list)
```

---

## 11. Traceability Model

Every node across all transformation stages retains full lineage tracing back to raw source Markdown:

```
[Raw Markdown Section] ──► [KnowledgeUnit ID] ──► [Artifact Structure Node] ──► [PageComposition Block] ──► [Rendered PDF Region]
```

### Bidirectional Traceability Contract
- **Forward Mapping**: `KnowledgeUnit.id` $\rightarrow$ `ArtifactNode.source_refs` $\rightarrow$ `ContentBlock.source_unit_ids`.
- **Backward Mapping**: `ContentBlock` $\rightarrow$ `KnowledgeUnit` $\rightarrow$ `KnowledgeProvenance.raw_snippet`.

This guarantees:
1. **100% Coverage Auditing**: QA engines can verify if any `CRITICAL` `KnowledgeUnit` was omitted from the final PDF.
2. **Hallucination Detection**: Any text block in the PDF without a valid `source_unit_id` is flagged as an ungrounded hallucination.

---

## 12. Versioning & Artifact Lineage

To prevent quality repair loops from corrupting raw knowledge, data structures are split into **Immutable Core** and **Versioned Artifacts**:

```
[UniversalKnowledgeManifest v1] (IMMUTABLE)
               │
               ▼
   [ArtifactArchitecture v1] ──► [Composition v1] ──► [PDF v1] ──► [QA Round 1 Fail]
               │
      (Deterministic Repair)
               │
               ▼
   [ArtifactArchitecture v2] ──► [Composition v2] ──► [PDF v2] ──► [QA Round 2 PASS]
```

### Lineage Rules
1. `UniversalKnowledgeManifest` is compiled **ONCE** per source document and is **IMMUTABLE**.
2. Repair engines mutate **ONLY** `ArtifactArchitecture` (e.g., reflowing text, splitting sections, adjusting worksheet workspace heights).
3. Every repair iteration increments the artifact version (`v1` $\rightarrow$ `v2`) and invalidates downstream `DocumentComposition`, HTML, and PDF files via `PipelineState.invalidate_after_repair()`.

---

## 13. AI Boundary Policy

We enforce a strict **Local-First, Selective AI** execution policy:

| Operation | Policy | Rationale |
|---|---|---|
| **Markdown Tree Parsing** | `DETERMINISTIC` | Regex/AST parsing is 100% reliable and instantaneous. |
| **Local Rule Classification** | `RULE-BASED` | Regex patterns capture titles, formulas, tables, K3 warnings reliably. |
| **Semantic Ambiguity Resolution** | `SELECTIVE AI` | Invoked ONLY when paragraph complexity exceeds local rule confidence. |
| **Concept Relationship Discovery** | `SELECTIVE AI` | AI infers implicit causality and prerequisite graphs across concepts. |
| **Artifact Storyboarding / Planning** | `RULE + SELECTIVE AI` | Deterministic templates handle 80% of layouts; AI handles novel narrative acts. |
| **Composition & Layout Assembly** | `DETERMINISTIC` | HTML/CSS grid positioning must be 100% deterministic. |
| **Rendering (Jinja2 + Playwright)** | `DETERMINISTIC` | Physical PDF generation requires exact browser rendering. |
| **Quality Evaluation & QA Gates** | `DETERMINISTIC` | QA rules must be objective, repeatable, and non-flaky. |
| **Artifact Repair Engine** | `DETERMINISTIC FIRST` | Deduplication, text truncation, and layout remapping must be deterministic. |

---

## 14. Backward Compatibility Strategy

The mature Presentation 16:9 engine (comprising `SlideArchitect`, `SlideGenerator`, `PresentationQualityGate`, `DeterministicRepairEngine`, and `QualityDecisionEngine`) **MUST NOT BE REWRITTEN**.

### Adapter Layer Architecture
We implement `PresentationKnowledgeAdapter`:

```python
class PresentationKnowledgeAdapter:
    @staticmethod
    def to_legacy_manifest(universal_manifest: UniversalKnowledgeManifest) -> ContentManifest:
        """Adapts UniversalKnowledgeManifest to legacy ContentManifest for SlideArchitect."""
        # Maps KnowledgeUnits to ManifestConcept objects
        # Computes slide count bounds dynamically at adapter boundary
        return legacy_manifest
```

This adapter pattern guarantees that:
- Existing presentation unit tests pass without modification.
- All 25 Presentation Quality Gates remain operational.
- The 16:9 repair and convergence loop functions without regression.

---

## 15. Failure Mode Analysis

| Risk | Cause | Impact | Mitigation Strategy |
|---|---|---|---|
| **1. Manifest Schema Becomes God Object** | Attempting to store format-specific fields in `UniversalKnowledgeManifest`. | Breaks non-presentation formats; re-introduces format collapse. | Strict Pydantic validation forbidding slide/page/CSS fields in manifest. |
| **2. Transformer Abstraction Too Generic** | Forcing all 4 formats to return a single generic `DocumentBlueprint`. | Destroys format-specific intelligence (e.g. loses worksheet workspace heights). | Define distinct architecture classes (`HandoutArchitecture`, `WorksheetArchitecture`, etc.). |
| **3. Presentation Engine Regression** | Modifying `SlideArchitect` directly during universal manifest rollout. | Breaks existing 25 QA gates and presentation generation tests. | Use `PresentationKnowledgeAdapter` as a strict compatibility bridge. |
| **4. AI Cost & Latency Escalation** | Calling AI for every stage instead of using local deterministic parsers. | Pipeline latency increases from 5s to 45s+; API costs balloon. | Enforce `Selective AI` policy; restrict LLM calls to ambiguous blocks. |
| **5. Stale Export Artifacts** | Repairing blueprint without invalidating cached HTML/PDF. | User receives outdated PDF that doesn't match repaired blueprint metadata. | Enforce `PipelineState.invalidate_after_repair()` across all 4 formats. |

---

## 16. Proposed Module Boundaries

To enforce clean separation of concerns, new V5 modules will be structured as follows:

```
app/
├── intelligence/
│   ├── universal_manifest.py         # UniversalKnowledgeManifest & KnowledgeUnit schemas
│   ├── universal_extractor.py        # Local-first manifest builder
│   └── relationship_graph.py         # Knowledge DAG builder
├── intent/
│   ├── contracts.py                  # ArtifactIntent & IntentFunction schemas
│   └── resolver.py                   # Intent resolver per target format
├── transformers/
│   ├── base.py                       # IArtifactTransformer interface
│   ├── presentation_transformer.py   # Adapter to SlideArchitect
│   ├── handout_transformer.py        # HandoutArchitecture builder
│   ├── worksheet_transformer.py      # WorksheetArchitecture builder (with workspaces)
│   └── kti_transformer.py            # ScientificDocumentArchitecture builder (BAB 1-5)
├── quality/
│   ├── gates/
│   │   ├── presentation_gates.py     # 25 Presentation Gates
│   │   ├── handout_gates.py          # Handout Density & Reading Flow Gates
│   │   ├── worksheet_gates.py        # Workspace & Answer Key Gates
│   │   └── kti_gates.py              # IMRAD & Citation Integrity Gates
```

---

## 17. Migration Plan Phase 1B

1. **Step 1: Create Schemas (`app/intelligence/universal_manifest.py`)**
   - Implement `UniversalKnowledgeManifest`, `KnowledgeUnit`, and `KnowledgeRelationship`.
2. **Step 2: Build Universal Extractor (`app/intelligence/universal_extractor.py`)**
   - Refactor `MarkdownTreeParser` output mapping to generate `UniversalKnowledgeManifest`.
3. **Step 3: Implement Presentation Adapter (`app/transformers/presentation_transformer.py`)**
   - Create `PresentationKnowledgeAdapter` to bridge `UniversalKnowledgeManifest` $\rightarrow$ `ContentManifest`.
   - Verify that all existing presentation unit tests pass 100%.

---

## 18. Open Design Decisions

| ID | Decision Item | Status | Options | Recommendation |
|---|---|---|---|---|
| **ODD-1** | Knowledge Graph Storage Format | **Ready for Implementation** | NetworkX in-memory vs Pydantic list of DAG edges | Pydantic list of DAG edges (lightweight, zero external C-deps) |
| **ODD-2** | Worksheet Answer Key Location | **Requires Human Review** | Inline Appendix vs Separate PDF Artifact | Configurable flag (`has_answer_key_appendix: bool`), defaulting to Appendix |
| **ODD-3** | KTI Citation Format Standard | **Requires Human Review** | APA 7th vs IEEE vs Indonesian Academic Standard | Default to Indonesian Academic Standard (BAB 1-5 + IEEE/APA numbering) |
