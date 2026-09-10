# Phase 1A.1 Architecture Revision — Universal Knowledge Core

## 1. Revision Summary

Following an architectural kill-critic review of the Phase 1A design, this document establishes **Phase 1A.1 Architecture Revisions**. It corrects design flaws identified in earlier proposals prior to Phase 1B implementation and enforces strict consistency across all pipeline stages, schemas, graph topologies, and module boundaries.

### Key Corrections Overview

1. **Graph Topology**: Replaced the forced DAG model with a **General Directed Typed Graph** (`UniversalKnowledgeGraph`). Cycles (such as reciprocal contrasts or concept-experiment loops) are explicitly allowed in the core graph, while specialized derived views (e.g., `DependencyGraphView`) enforce DAG constraints on demand.
2. **Elimination of Arbitrary Dictionaries**: Completely removed `payload: Dict[str, Any]` and `structural_constraints: Dict[str, Any]`. Introduced **6 strongly-typed payload families** using Pydantic Discriminated Unions (`KnowledgePayloadUnion`) and strongly-typed intent constraint models (`IntentConstraints`).
3. **Decoupling Intrinsic Importance from Coverage**: Removed presentation-centric criticality tiers (`CRITICAL = must appear in all formats`). Replaced with `intrinsic_importance` (`FOUNDATIONAL`, `CENTRAL`, `SUPPORTING`, `CONTEXTUAL`) inside the manifest, delegating format inclusion decisions to downstream `ArtifactCoveragePolicy` and `CoverageDecision`.
4. **Dynamic Intent Resolution**: Replaced static per-format `ArtifactIntent` with a 2-stage model: `GenerationRequest` + `UniversalKnowledgeManifest` $\rightarrow$ `IntentResolver` $\rightarrow$ `ResolvedArtifactIntent`.
5. **Phased Traceability**: Scaled down initial traceability scope to Phase 1B boundary (`Source` $\rightarrow$ `KnowledgeUnit` $\rightarrow$ `ArtifactNode`), deferring DOM and PDF-region mapping to later phases.
6. **Canonical 9-Stage Knowledge Compilation Pipeline**: Established an authoritative 9-stage modular pipeline (`KnowledgeCompilationPipeline`) with explicit input/output contracts for every stage.
7. **Structured Audience Profile**: Replaced flat `audience_level: str` with a structured `AudienceProfile` (`education_level`, `expertise_level`, `language`).
8. **Single Source of Truth**: Removed derived index fields (`critical_unit_ids`, `concept_dependency_order`) from the manifest to eliminate state duplication.
9. **Relationship Provenance**: Added `RelationshipOrigin` (`EXPLICIT_SOURCE`, `DETERMINISTIC_RULE`, `AI_INFERRED`) and `RelationshipEvidence` to defend against AI hallucinated edges.
10. **Strict Immutability & Diagnostic Cycle Handling**: Established read-only immutability for `UniversalKnowledgeManifest` post-compilation and introduced `DependencyCycleDiagnostic` to log edge exclusions without mutating the core graph.

---

## 2. Knowledge Graph Redesign & Dependency Cycle Diagnostics

### Flaw in Initial Proposal
The initial Phase 1A design forced `UniversalKnowledgeManifest.relationships` to be a Directed Acyclic Graph (DAG). This assumption breaks in real-world knowledge domains:
- **Reciprocal Contrast**: Concept A (Classical Physics) $\leftrightarrow$ `CONTRASTED_WITH` $\leftrightarrow$ Concept B (Quantum Physics) creates a 2-node cycle.
- **Concept-Experiment Feedback**: Concept A (Combustion) $\rightarrow$ `MOTIVATES` $\rightarrow$ Experiment B (Hand Fire) $\rightarrow$ `DEMONSTRATES` $\rightarrow$ Concept A creates a cycle.

### Redesigned Architecture
The core knowledge graph is now defined as a **General Directed Typed Graph**:

```python
class UniversalKnowledgeGraph(BaseModel):
    """General Directed Typed Graph representing raw knowledge relationships.
    Cycles are explicitly allowed in the core graph.
    """
    nodes: Dict[str, KnowledgeUnit] = Field(default_factory=dict)
    edges: List[KnowledgeRelationship] = Field(default_factory=list)
```

### Derived Specialized Views & Cycle Diagnostics
Derived views are computed on-demand from `UniversalKnowledgeGraph` and apply specific topological constraints:

```
                      ┌──────────────────────────────────────┐
                      │      UniversalKnowledgeGraph         │
                      │  (General Directed Graph w/ Cycles)  │
                      └──────────────────┬───────────────────┘
                                         │
       ┌───────────────────┬─────────────┴─────────────┬───────────────────┐
       │                   │                           │                   │
       ▼                   ▼                           ▼                   ▼
DEPENDENCY VIEW     EVIDENCE VIEW               CAUSAL VIEW         CONTRAST VIEW
(Prerequisite DAG)  (Claims & Evidence)         (Cause & Effect)    (Alternatives & Misconceptions)
  └─ MUST be DAG      └─ Multi-parent Graph       └─ Causal DAG       └─ Bi-directional Graph
```

### Strict Cycle Policy & Diagnostic Rules
1. **Core Graph Immutability**: The core `UniversalKnowledgeGraph` is **NEVER** mutated during cycle detection.
2. **Explicit Source Protection**: Edges with `origin == RelationshipOrigin.EXPLICIT_SOURCE` must **NEVER** be silently removed.
3. **AI Inferred Edge Filtering**: Edges with `origin == RelationshipOrigin.AI_INFERRED` may be excluded from `DependencyGraphView` if they participate in a cycle or have low confidence.
4. **Deterministic Inferred Edge Downgrading**: Deterministic rule edges in a cycle are marked as secondary dependencies rather than hard prerequisites.
5. **No Silent Repair**: Every edge exclusion creates a transparent `DependencyCycleDiagnostic` record:

```python
class CycleResolutionStrategy(str, Enum):
    EXCLUDE_AI_INFERRED = "exclude_ai_inferred"
    DOWNGRADE_DETERMINISTIC = "downgrade_deterministic"
    BREAK_LOWEST_CONFIDENCE = "break_lowest_confidence"
    MANUAL_OVERRIDE_REQUIRED = "manual_override_required"

class DependencyCycleDiagnostic(BaseModel):
    diagnostic_id: str
    cycle_nodes: List[str]
    cycle_edges: List[str]
    excluded_edges: List[str]
    reason: str
    severity: str  # WARNING, ERROR
    resolution_strategy: CycleResolutionStrategy

class DependencyGraphView(BaseModel):
    """Derived read-only DAG view of prerequisite relationships."""
    prerequisite_edges: List[KnowledgeRelationship]
    topological_sort_order: List[str]
    diagnostics: List[DependencyCycleDiagnostic] = Field(default_factory=list)
```

---

## 3. Typed Knowledge Payload Model & Enums

### Flaw in Initial Proposal
The initial design proposed a "Hybrid Discriminator" but left `payload: Dict[str, Any]`, which re-introduced untyped dictionaries into core semantic paths.

### Redesigned Discriminated Union
We establish **6 strongly-typed payload families** using Pydantic Discriminated Unions and explicit enums across all semantic fields:

```python
from enum import Enum
from typing import Literal, Union, List, Optional, Dict
from pydantic import BaseModel, Field
from app.intelligence.schemas import ContentType

class KnowledgeCategory(str, Enum):
    CORE_CONCEPT = "core_concept"
    PROCEDURAL = "procedural"
    EMPIRICAL = "empirical"
    FORMAL = "formal"
    EVALUATIVE = "evaluative"
    STIMULUS = "stimulus"

class IntrinsicImportance(str, Enum):
    FOUNDATIONAL = "foundational"  # Fundamental law or core definition
    CENTRAL = "central"            # Primary mechanism or main topic
    SUPPORTING = "supporting"      # Illustrative example or secondary detail
    CONTEXTUAL = "contextual"      # Historical background or optional trivia

class EvidenceType(str, Enum):
    OBSERVATION = "observation"
    MEASUREMENT = "measurement"
    EXPERIMENTAL_RESULT = "experimental_result"
    LITERATURE = "literature"
    CITATION = "citation"
    COMPARATIVE_EXAMPLE = "comparative_example"
    QUALITATIVE_ANALYSIS = "qualitative_analysis"

# ── 1. Concept Payload ────────────────────────────────────────────────────────
class ConceptPayload(BaseModel):
    kind: Literal["concept"] = "concept"
    formal_definition: str
    intuitive_explanation: Optional[str] = None
    key_principles: List[str] = Field(default_factory=list)
    underlying_mechanisms: List[str] = Field(default_factory=list)
    symbol: Optional[str] = None
    si_unit: Optional[str] = None

# ── 2. Procedure Payload ──────────────────────────────────────────────────────
class ProcedureStep(BaseModel):
    step_number: int
    action: str
    safety_note: Optional[str] = None
    expected_result: Optional[str] = None

class ProcedurePayload(BaseModel):
    kind: Literal["procedure"] = "procedure"
    objective: str
    apparatus_and_materials: List[str] = Field(default_factory=list)
    steps: List[ProcedureStep] = Field(default_factory=list)
    safety_level: str = "standard"  # standard, warning, K3_critical

# ── 3. Formal Payload ─────────────────────────────────────────────────────────
class VariableDefinition(BaseModel):
    symbol: str
    name: str
    unit: str
    is_constant: bool = False

class FormalPayload(BaseModel):
    kind: Literal["formal"] = "formal"
    latex_equation: str
    variables: List[VariableDefinition] = Field(default_factory=list)
    derivation_notes: Optional[str] = None
    conditions_of_validity: List[str] = Field(default_factory=list)

# ── 4. Generalized Evidence Payload (Quantitative & Qualitative) ─────────────
class QuantitativeEvidenceData(BaseModel):
    numeric_values: Dict[str, float] = Field(default_factory=dict)
    units: Dict[str, str] = Field(default_factory=dict)
    uncertainty: Optional[float] = None
    sample_size: Optional[int] = None

class QualitativeEvidenceData(BaseModel):
    observed_phenomenon: str
    textual_findings: str
    context_notes: Optional[str] = None

class EvidenceSourceMetadata(BaseModel):
    citation_key: Optional[str] = None
    authors: List[str] = Field(default_factory=list)
    year: Optional[int] = None
    doi_or_url: Optional[str] = None

class EvidencePayload(BaseModel):
    kind: Literal["evidence"] = "evidence"
    evidence_type: EvidenceType
    statement: str
    supports_claim_ids: List[str] = Field(default_factory=list)
    quantitative_data: Optional[QuantitativeEvidenceData] = None
    qualitative_data: Optional[QualitativeEvidenceData] = None
    source_metadata: Optional[EvidenceSourceMetadata] = None

# ── 5. Argument Payload ───────────────────────────────────────────────────────
class ArgumentPayload(BaseModel):
    kind: Literal["argument"] = "argument"
    claim_statement: str
    reasoning: str
    limitations: List[str] = Field(default_factory=list)
    counterarguments: List[str] = Field(default_factory=list)

# ── 6. Pedagogical Payload ────────────────────────────────────────────────────
class PedagogicalPayload(BaseModel):
    kind: Literal["pedagogical"] = "pedagogical"
    prompt_type: str  # QUESTION, MISCONCEPTION, WARNING, REFLECTION
    misconception_belief: Optional[str] = None
    correct_explanation: Optional[str] = None
    distractor_options: List[str] = Field(default_factory=list)
    hint: Optional[str] = None

# ── Discriminated Union Family ────────────────────────────────────────────────
KnowledgePayloadUnion = Union[
    ConceptPayload,
    ProcedurePayload,
    FormalPayload,
    EvidencePayload,
    ArgumentPayload,
    PedagogicalPayload,
]
```

### KnowledgeUnit Core Model with Deterministic Stable IDs

Random UUIDs (`ku_<uuid8>`) are **prohibited** for canonical knowledge identity. KnowledgeUnit IDs are generated deterministically:

$$\text{hash} = \text{SHA256}(\text{source\_fingerprint} + \text{normalized\_content} + \text{content\_type})[:12]$$
$$\text{KnowledgeUnit.id} = \text{ku\_} + \text{hash}$$

```python
class KnowledgeUnit(BaseModel):
    id: str  # Deterministic stable ID: "ku_<12-char-hex-hash>"
    title: str
    content_type: ContentType
    category: KnowledgeCategory
    intrinsic_importance: IntrinsicImportance
    provenance: KnowledgeProvenance
    payload: KnowledgePayloadUnion = Field(discriminator="kind")
    tags: List[str] = Field(default_factory=list)
```

#### Stable ID Rules:
1. **Identical Semantic Content**: Re-running the pipeline on identical text produces identical `ku_<hash>` IDs.
2. **Formatting Changes**: Minor whitespace changes are stripped during normalization, preserving stable IDs.
3. **Semantic Changes**: Substantive content edits generate a new `ku_<hash>` ID.
4. **Collision Handling**: In the extremely rare event of a hash collision, a sequence suffix (`ku_<hash>_2`) is appended.

---

## 4. Intrinsic Importance vs. Artifact Coverage

### Flaw in Initial Proposal
The initial design coupled `CriticalityTier.CRITICAL` directly to *"Must appear explicitly in all artifact formats"*. This caused presentation constraints to dictate handout and worksheet inclusion logic.

### Redesigned Architecture

1. **Manifest Layer (`intrinsic_importance`)**: Reflects the objective importance of the concept within the source domain, independent of target format.
2. **Downstream Layer (`ArtifactCoveragePolicy` & `CoverageDecision`)**: Formats evaluate `intrinsic_importance` against their specific `ArtifactIntent` to issue a `CoverageDecision`:

```python
class CoverageAction(str, Enum):
    INCLUDE_PRIMARY = "include_primary"      # Main focal point (e.g. Slide Card / Main Section)
    INCLUDE_DETAILED = "include_detailed"    # Complete prose elaboration
    USE_AS_STIMULUS = "use_as_stimulus"      # Problem prompt or phenomenon in Worksheet
    USE_AS_EVIDENCE = "use_as_evidence"      # Citation/data point in KTI Paper
    SUMMARIZE = "summarize"                  # Compressed reference
    OMIT = "omit"                            # Omitted due to format constraints

class CoverageDecision(BaseModel):
    unit_id: str
    format_id: str
    action: CoverageAction
    rationale: str
```

### Cross-Format Coverage Matrix Example

| Source Knowledge Unit | Intrinsic Importance | Presentation 16:9 | Handout A4 | Student Worksheet | Scientific KTI Paper |
|---|---|---|---|---|---|
| **Segitiga Api (Teori)** | `FOUNDATIONAL` | `INCLUDE_PRIMARY` | `INCLUDE_DETAILED` | `USE_AS_STIMULUS` | `INCLUDE_DETAILED` |
| **Persamaan Kalor ($Q=mc\Delta T$)** | `CENTRAL` | `INCLUDE_PRIMARY` | `INCLUDE_DETAILED` | `USE_AS_STIMULUS` | `USE_AS_EVIDENCE` |
| **Prosedur Cuci Tangan K3** | `SUPPORTING` | `OMIT` | `INCLUDE_DETAILED` | `INCLUDE_PRIMARY` | `OMIT` |
| **Sejarah Penemuan Gas Butana** | `CONTEXTUAL` | `OMIT` | `SUMMARIZE` | `OMIT` | `SUMMARIZE` |

---

## 5. Generation Request & Strongly-Typed Intent Constraints

Replaces all `Dict[str, Any]` escape hatches in generation requests and resolved intents with strongly-typed constraint models:

```python
class LengthConstraint(BaseModel):
    target_pages_or_slides: Optional[int] = None
    max_words_per_section: Optional[int] = None

class DepthConstraint(BaseModel):
    detail_level: str = "standard"  # summary, standard, exhaustive
    include_worked_examples: bool = True
    include_math_derivations: bool = False

class CitationConstraint(BaseModel):
    style: str = "indonesian_kti"   # indonesian_kti, apa7, ieee
    require_doi: bool = False

class FormatIntentConstraint(BaseModel):
    allow_two_column: bool = False
    include_answer_key_appendix: bool = True
    custom_accent_color: Optional[str] = None

class IntentConstraints(BaseModel):
    length: LengthConstraint = Field(default_factory=LengthConstraint)
    depth: DepthConstraint = Field(default_factory=DepthConstraint)
    citation: CitationConstraint = Field(default_factory=CitationConstraint)
    format_specific: FormatIntentConstraint = Field(default_factory=FormatIntentConstraint)

class GenerationRequest(BaseModel):
    request_id: str
    raw_source_text: str
    source_filename: str = "input.md"
    target_format_id: str
    audience: AudienceProfile
    constraints: IntentConstraints = Field(default_factory=IntentConstraints)
```

---

## 6. Resolved Artifact Intent

`IntentResolver` takes `GenerationRequest` + `UniversalKnowledgeManifest` metadata and dynamically resolves the specific generation strategy without any generic dictionaries:

```python
class ResolvedArtifactIntent(BaseModel):
    intent_id: str
    target_format_id: str
    strategy_mode: str      # e.g., "HANDOUT_ADVANCED_INDEPENDENT" vs "HANDOUT_BEGINNER_GUIDED"
    primary_goal: str
    audience: AudienceProfile
    ordered_intent_functions: List[str]  # e.g., ["ENGAGE", "EXPLAIN", "REFLECT"]
    constraints: IntentConstraints
```

---

## 7. Phased Traceability Model

Full traceability is broken into discrete implementation phases to keep Phase 1B lean and verifiable:

```
PHASE 1B BOUNDARY:
[Raw Source Markdown] ──(Provenance)──► [KnowledgeUnit ID] ──(SourceRef)──► [ArtifactNode ID]

PHASE 2 (Composition Layer):
                                                                             │
                                                                             ▼
                                                                   [CompositionBlock ID]

PHASE 4/5 (Physical Layer):
                                                                             │
                                                                             ▼
                                                                  [Rendered PDF Region]
```

### Stable ID Contract (Established in Phase 1B)
- `KnowledgeProvenance.block_ids`: List of raw Markdown paragraph block IDs.
- `KnowledgeUnit.id`: `ku_<12-char-hex-hash>` (Deterministic)
- `ArtifactNode.source_refs`: List of `KnowledgeUnit.id` strings.

---

## 8. Canonical 9-Stage Knowledge Compilation Pipeline

To prevent a single "Universal Extractor" god object, manifest construction is governed by an authoritative **9-Stage Pipeline** with strict stage ownership boundaries:

```
Raw Source Text
      │
      ▼
1. StructuralExtractor     ──(RawSource)──────────────────► (StructuralTree)
      │
      ▼
2. UnitNormalizer          ──(StructuralTree)─────────────► (CandidateUnits)
      │
      ▼
3. LocalClassifier         ──(CandidateUnits)─────────────► (RuleClassifiedUnits)
      │
      ▼
4. AmbiguityResolver       ──(RuleClassifiedUnits)────────► (ResolvedUnits)
      │
      ▼
5. PayloadBuilder          ──(ResolvedUnits)──────────────► (TypedPayloadUnits)
      │
      ▼
6. ClaimEvidenceExtractor  ──(TypedPayloadUnits)──────────► (ClaimEvidenceGraph)
      │
      ▼
7. RelationshipInferencer  ──(ClaimEvidenceGraph)─────────► (KnowledgeGraphEdges)
      │
      ▼
8. ImportanceAnalyzer      ──(GraphEdges + PayloadUnits)──► (ImportanceScoredUnits)
      │
      ▼
9. ManifestAssembler       ──(ScoredUnits + Edges)────────► (ImmutableManifest)
```

### Explicit Input/Output Contracts & Stage Responsibilities

| Stage | Module Name | Input Contract | Output Contract | Responsibility Boundary |
|---|---|---|---|---|
| **1. StructuralExtractor** | `structural_extractor.py` | `raw_text: str` | `StructuralTree` | Parses Markdown heading AST and section hierarchy. |
| **2. UnitNormalizer** | `unit_normalizer.py` | `StructuralTree` | `List[CandidateUnit]` | Strips formatting noise and generates stable block IDs. |
| **3. LocalClassifier** | `local_classifier.py` | `List[CandidateUnit]` | `List[RuleClassifiedUnit]` | Applies regex heuristics for formulas, tables, and K3 warnings. |
| **4. AmbiguityResolver** | `ambiguity_resolver.py` | `List[RuleClassifiedUnit]` | `List[ResolvedUnit]` | Calls Selective AI Gateway **only** for ambiguous paragraph blocks. |
| **5. PayloadBuilder** | `payload_builder.py` | `List[ResolvedUnit]` | `List[KnowledgeUnit]` | Constructs atomic `KnowledgeUnit`s with strongly-typed `KnowledgePayloadUnion` instances. |
| **6. ClaimEvidenceExtractor** | `claim_evidence_extractor.py` | `List[KnowledgeUnit]` | `ClaimEvidenceGraph` | Identifies claim/evidence semantics and builds associations between claim units and evidence units. |
| **7. RelationshipInferencer** | `relationship_inferencer.py` | `ClaimEvidenceGraph` | `List[KnowledgeRelationship]` | Generates cross-unit typed edges connecting concepts, claims, evidence, and procedures. |
| **8. ImportanceAnalyzer** | `importance_analyzer.py` | `Units + Edges` | `List[KnowledgeUnit]` | Assigns domain-intrinsic `intrinsic_importance` scores ($0.0-1.0$). |
| **9. ManifestAssembler** | `manifest_assembler.py` | `Units + Edges` | `UniversalKnowledgeManifest` | Assembles final frozen, immutable manifest instance. |

### Ownership Boundary Rule:
- **`PayloadBuilder`**: Constructs individual, atomic `KnowledgeUnit` objects (including raw payloads).
- **`ClaimEvidenceExtractor`**: Analyzes relationships between claims and evidence across units.
- **`RelationshipInferencer`**: Generates all cross-unit `KnowledgeRelationship` edges in the graph.
- **No Overlapping Responsibility**: No stage duplicates another stage's payload generation or edge building.

---

## 9. Audience Profile

Replaces flat `audience_level: str` with a structured `AudienceProfile`:

```python
class EducationLevel(str, Enum):
    PRIMARY = "primary"            # SD
    JUNIOR_HIGH = "junior_high"    # SMP
    SENIOR_HIGH = "senior_high"    # SMA/SMK
    UNDERGRADUATE = "undergraduate"# S1
    POSTGRADUATE = "postgraduate"  # S2/S3
    GENERAL = "general"

class ExpertiseLevel(str, Enum):
    NOVICE = "novice"
    DEVELOPING = "developing"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class AudienceProfile(BaseModel):
    education_level: EducationLevel = EducationLevel.SENIOR_HIGH
    expertise_level: ExpertiseLevel = ExpertiseLevel.NOVICE
    language: str = "id"           # Bahasa Indonesia default
    age_band: Optional[str] = None # e.g. "15-18"
```

---

## 10. Derived Views & Single Source of Truth

### Single Source of Truth Rule
The `UniversalKnowledgeManifest` stores **ONLY** atomic units (`units: Dict[str, KnowledgeUnit]`) and relationship edges (`relationships: List[KnowledgeRelationship]`).

### Removed Derived Fields
The following fields from earlier drafts are **EXPLICITLY REMOVED** from the manifest schema:
- `critical_unit_ids`: Computed on-demand via `manifest.get_units_by_importance(IntrinsicImportance.FOUNDATIONAL)`.
- `concept_dependency_order`: Computed on-demand via `DependencyGraphView.get_topological_sort()`.

---

## 11. Relationship Provenance & Confidence

Relationships inferred by AI are explicitly distinguishable from relationships declared explicitly in the source text or deduced via deterministic rules.

```python
class RelationshipOrigin(str, Enum):
    EXPLICIT_SOURCE = "explicit_source"    # Declared directly in source text
    DETERMINISTIC_RULE = "rule_deduced"    # Deduced via deterministic heuristic (e.g. section nesting)
    AI_INFERRED = "ai_inferred"            # Inferred via Selective AI Gateway

class RelationshipEvidence(BaseModel):
    origin: RelationshipOrigin
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_snippet: Optional[str] = None
    rule_name: Optional[str] = None

class KnowledgeRelationship(BaseModel):
    source_unit_id: str
    target_unit_id: str
    relationship: RelationshipType
    evidence: RelationshipEvidence
```

---

## 12. Manifest Immutability Contract

1. **Compilation Phase**: `KnowledgeCompiler` constructs the `UniversalKnowledgeManifest`.
2. **Post-Compilation Lock**: Once returned by `KnowledgeCompiler.compile()`, the manifest instance is **READ-ONLY** and frozen.
3. **Derived View Immutability**: Derived views (`DependencyGraphView`, `EvidenceGraphView`) return read-only data structures.
4. **Repair Engine Rule**: Downstream repair engines (`DeterministicRepairEngine`) are **STRICTLY PROHIBITED** from modifying `KnowledgeUnit` or manifest attributes. Repairs must mutate `ArtifactArchitecture` only.

---

## 13. Revised Architecture Diagram

```
                             RAW SOURCE TEXT (Markdown)
                                         │
                                         ▼
                   CANONICAL 9-STAGE KNOWLEDGE COMPILATION PIPELINE
             ┌────────────────────────────────────────────────────────┐
             │ 1. StructuralExtractor     ──► AST Hierarchy           │
             │ 2. UnitNormalizer          ──► Candidate Units         │
             │ 3. LocalClassifier         ──► Regex Rules (Formulas)  │
             │ 4. AmbiguityResolver       ──► Selective AI Gateway    │
             │ 5. PayloadBuilder          ──► 6 Payload Families      │
             │ 6. ClaimEvidenceExtractor  ──► Claim/Evidence Graph    │
             │ 7. RelationshipInferencer  ──► Typed Graph Edges       │
             │ 8. ImportanceAnalyzer      ──► Intrinsic Importance    │
             │ 9. ManifestAssembler       ──► Frozen Manifest         │
             └───────────────────────────┬────────────────────────────┘
                                         │
                                         ▼
                           UNIVERSAL KNOWLEDGE MANIFEST
                        (Strictly Immutable, Format-Neutral)
                          - units: Dict[str, KnowledgeUnit]
                          - relationships: List[KnowledgeRelationship]
                                         │
                    ┌────────────────────┴────────────────────┐
                    │                                         │
                    ▼                                         ▼
          ON-DEMAND DERIVED VIEWS                   GENERATION REQUEST
     - DependencyGraphView (DAG)              (Format, AudienceProfile, Depth)
     - EvidenceGraphView                                      │
     - CausalGraphView                                        ▼
                                                    INTENT RESOLVER
                                                              │
                                                              ▼
                                                    RESOLVED ARTIFACT INTENT
                                                              │
                                                              ▼
                                                    ARTIFACT COVERAGE POLICY
                                                              │
                                                              ▼
                                                    ARTIFACT TRANSFORMERS
                                            (Presentation, Handout, Worksheet, KTI)
```

---

## 14. Updated Module Boundaries

All Phase 1B files will be placed strictly in new, isolated module directories:

```
app/
├── intelligence/
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── provenance.py              # KnowledgeProvenance
│   │   ├── payloads.py                # KnowledgePayloadUnion & 6 payload families
│   │   ├── knowledge_unit.py          # KnowledgeUnit & IntrinsicImportance schemas
│   │   ├── relationships.py           # KnowledgeRelationship & RelationshipEvidence
│   │   ├── intent_constraints.py      # IntentConstraints & typed constraint models
│   │   └── universal_manifest.py      # UniversalKnowledgeManifest schema
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── universal_graph.py         # UniversalKnowledgeGraph (General Directed Graph)
│   │   └── views.py                   # DependencyGraphView (DAG) & DependencyCycleDiagnostic
│   └── pipeline/
│       ├── __init__.py
│       ├── structural_extractor.py    # Stage 1
│       ├── unit_normalizer.py         # Stage 2
│       ├── local_classifier.py        # Stage 3
│       ├── ambiguity_resolver.py      # Stage 4
│       ├── payload_builder.py         # Stage 5
│       ├── claim_evidence_extractor.py# Stage 6
│       ├── relationship_inferencer.py # Stage 7
│       ├── importance_analyzer.py     # Stage 8
│       ├── manifest_assembler.py      # Stage 9
│       └── compiler.py                # KnowledgeCompiler Orchestrator
```

---

## 15. Phase 1B Implementation Boundary

Phase 1B is strictly limited to constructing the **Universal Knowledge Core data layer and compilation pipeline**.

### Included in Phase 1B:
1. `UniversalKnowledgeManifest` and `KnowledgeUnit` Pydantic schemas.
2. 6 strongly-typed `KnowledgePayloadUnion` families (`ConceptPayload`, `ProcedurePayload`, `FormalPayload`, `EvidencePayload`, `ArgumentPayload`, `PedagogicalPayload`).
3. `KnowledgeProvenance` and deterministic stable ID assignment (`ku_<12-char-hex-hash>`).
4. `KnowledgeRelationship` and `RelationshipEvidence` schemas.
5. `UniversalKnowledgeGraph` (General Graph), `DependencyGraphView` (DAG View), and `DependencyCycleDiagnostic`.
6. Canonical 9-stage `KnowledgeCompilationPipeline` (`StructuralExtractor`, `UnitNormalizer`, `LocalClassifier`, `AmbiguityResolver`, `PayloadBuilder`, `ClaimEvidenceExtractor`, `RelationshipInferencer`, `ImportanceAnalyzer`, `ManifestAssembler`).
7. Source Markdown $\rightarrow$ `KnowledgeUnit` forward/backward traceability.
8. Comprehensive unit test suite for manifest creation, payload validation, graph view topological sorting, and cycle diagnostics.

### EXCLUDED from Phase 1B (Deferred to Phase 2+):
- ❌ NO `ArtifactTransformer` implementations (`HandoutTransformer`, `WorksheetTransformer`, `KTI_Transformer`).
- ❌ NO modification to `production_pipeline.py`.
- ❌ NO deletion of Branch B.
- ❌ NO changes to `SlideArchitect` or Presentation 16:9 engine.
- ❌ NO universal QA gates or repair engine changes.
- ❌ NO PDF region traceability.

---

## 16. Architecture Consistency Check

| Check Item | Description | Status |
|---|---|---|
| **1. Pipeline consistency** | Canonical 9-stage pipeline defined identically across Sections 8, 13, 14, and 15 with explicit input/output contracts. | **PASS** |
| **2. Schema typing** | All semantic models and constraints use explicit Pydantic models/enums. Zero `Dict[str, Any]` escape hatches remain in semantic core models. | **PASS** |
| **3. Graph integrity** | `UniversalKnowledgeGraph` is a General Directed Typed Graph allowing cycles without artificial topological restrictions. | **PASS** |
| **4. Cycle diagnostics** | Core graph is never mutated during cycle resolution. Edge exclusions generate transparent `DependencyCycleDiagnostic` records. | **PASS** |
| **5. Stable IDs** | Replaced random UUIDs with deterministic `ku_<12-char-hex-hash>` based on source fingerprint, normalized content, and content type. | **PASS** |
| **6. Evidence generality** | `EvidencePayload` generalized via `EvidenceType` enum to support both qualitative prose and quantitative measurement data. | **PASS** |
| **7. Claim/Evidence boundaries** | Clear responsibility boundaries between `PayloadBuilder` (atomic units), `ClaimEvidenceExtractor` (associations), and `RelationshipInferencer` (edges). | **PASS** |
| **8. Phase 1B boundary** | Scope strictly isolated to Universal Knowledge Core schemas, graph, and 9-stage pipeline. No downstream transformer or production pipeline changes. | **PASS** |

---

# PHASE 1A.1 FINAL ARCHITECTURE APPROVED
# READY FOR PHASE 1B IMPLEMENTATION
