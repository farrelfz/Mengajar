# 01 — Intelligent Material Director: Forensic Architectural Audit

## 1. Executive Summary & Objective
Before implementing the **Intelligent Material Director & Pedagogical Choreography Engine**, this forensic audit investigates the exact pipeline mechanisms governing material generation, content ordering, pedagogical sequencing, and capability resolution in the current system.

---

## 2. Concrete Architectural Audit Answers

### 1. Where does a raw `MaterialRequest` enter the system?
- **Entry Point**: `MaterialProductionPipeline.produce_artifact()` located in [`app/orchestration/production_pipeline.py:53-118`](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/orchestration/production_pipeline.py#L53-L118).
- Accepts `raw_input: str`, `source_hint: str`, `domain: KnowledgeDomain`, `audience: AudienceLevel`, `target_artifact: TargetArtifactType`, `target_format: str`.

### 2. Where is semantic analysis performed?
- **Analysis Engine**: `ContentIntelligenceAgent.analyze()` in [`app/intelligence/agent.py`](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/intelligence/agent.py).
- Normalizes text (`Normalizer`), segments into units (`Segmenter`), extracts semantic intents (`ContentIntelligence`), detects research roles (`ResearchRoleDetector`), extracts causal links (`RelationshipExtractor`), and discovers visual intent (`VisualIntentDetector`).

### 3. Where is `SemanticMaterialBlueprint` generated?
- **Blueprint Generator**: `MaterialBlueprintGenerator.generate_blueprint()` in [`app/blueprints/generator.py`](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/blueprints/generator.py).
- Synthesizes 3 blueprint layers:
  - **Level A (Content Blueprint)**: Concepts, claims, definitions, empirical data.
  - **Level B (Pedagogical Blueprint)**: List of `PedagogicalStep` items (title, content, pedagogical role, visual intent, key points).
  - **Level C (Production Blueprint)**: Target format, color palette, typography, visual weight.

### 4. Where does capability resolution happen?
- **Resolver Invocation**: Inside `CompositionBridge.compose()` in [`app/composition/bridge.py:72-135`](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/composition/bridge.py#L72-L135).
- For each `PedagogicalStep`, `CapabilityResolver.resolve_for_step()` finds the highest-scoring registered capability using multi-axis taxonomy matching (family, semantic intent, visual grammar, domain, format compatibility).

### 5. What currently determines content ordering?
- **Content Ordering**: Linear source document ordering.
- `Segmenter.segment()` parses headings and paragraphs in their verbatim source order.
- The blueprint generator iterates over these segments sequentially.

### 6. What currently determines pedagogical ordering?
- **Pedagogical Ordering**: Implicitly mirrors the author's raw text sequence.
- If the raw text lists the mathematical formula first and intuition second, the system generates the mathematical derivation first.
- There is currently no higher-level pedagogical director restructuring content into an optimal learning journey.

### 7. Is there currently a concept of learning progression?
- **Status**: Rudimentary / Local only.
- Individual capabilities (such as `pedagogy.question_progression` or `progression.ladder`) model internal stage ladders, but the overarching document lacks a macro-level `LearningJourney` orchestrator.

### 8. Is there currently a concept of narrative progression?
- **Status**: Minimal / Local.
- Presentation slide groups have `presentation.narrative_arc` as an isolated capability, but the system cannot orchestrate a complete multi-page dramatic or pedagogical narrative across an entire document.

### 9. Can the system distinguish "Explain" vs "Teach"?
- **Status**: **NO**.
- Both are mapped to `PedagogicalRole.EXPLANATION` or `SemanticIntent.EXPLAIN`.
- The system does not yet distinguish between:
  - *Explaining* (pure informational decomposition for passive comprehension).
  - *Teaching* (scaffolded knowledge construction: Hook → Misconception → Concrete Model → Formalization → Worked Example → Practice → Reflection).

### 10. Can the current system determine: "This concept should be introduced before this formula"?
- **Status**: **NO**.
- Only if the user wrote the concept before the formula in the input markdown.

### 11. Can the current system determine: "The learner should encounter a misconception before correction"?
- **Status**: **NO**.
- Unless the raw input explicitly structures it that way.

### 12. Can the current system determine: "A worked example should appear before independent practice"?
- **Status**: **NO**.
- No stage transition grammar currently exists to flag or reorder practice before examples.

### 13. Locations where ordering logic currently exists:
- `app/intelligence/segmenter.py`: Source AST traversal order.
- `app/intelligence/blueprint_proposer.py`: Source segment iteration order.
- `app/composition/bridge.py`: Sequential step-by-step resolution loop.

### 14. Nature of current content ordering:
- **Verdict**: **Implicit, Linear, and Accidentally Bound to Input Text Structure**.

---

## 3. Required Architectural Shift in Batch 11

```
[RAW INPUT / GOAL]
       │
       ▼
[Content Intelligence] (Extracts concepts, claims, formulas)
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│                 INTELLIGENT MATERIAL DIRECTOR               │
│                                                             │
│  - Analyzes Learning Goal & Audience Profile                │
│  - Selects Pedagogical / Narrative Strategy                 │
│  - Plans Ordered LearningJourney Stages                     │
│  - Validates Stage Transitions via Transition Grammar       │
│  - Enforces Cognitive Progression (Recognize → Create)      │
│  - Budgets Semantic Density per Format                      │
│  - Produces Stage-by-Stage CapabilityRequirements           │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 CAPABILITY CHOREOGRAPHER                    │
│   (Emits Taxonomy Requirements: Intent, Role, Grammar)      │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     RESOLVER V2 ENGINE                      │
│        (Selects best capability from 80+ library)           │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Key Invariants for Batch 11
1. **Separation of Intent and Implementation**: The Director produces `CapabilityRequirement` (Taxonomy criteria), **never** hardcoded capability IDs.
2. **Resolver Decoupling**: Resolver V2 remains the sole engine selecting concrete capabilities.
3. **Format Purity**: Director reasons about pedagogical density (Low/Medium/High), never about pixel/CSS coordinates.
4. **Backward Compatibility**: `MaterialProductionPipeline` must support `director_enabled=True` while maintaining 100% backward compatibility.
