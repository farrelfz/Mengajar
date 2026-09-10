# Phase 1B Implementation Forensics Report

## 1. Existing Reusable Components

Forensic inspection of the codebase identified several highly mature, production-grade components in `app/intelligence/` and `app/ai/` that can be directly leveraged or adapted during Phase 1B:

- **`MarkdownTreeParser`** ([markdown_tree_parser.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/intelligence/markdown_tree_parser.py)): High-performance, 100% deterministic AST parser converting Markdown into a hierarchical `ContentTree` (`ContentSection` and `ContentBlock`).
- **`RuleClassifier`** ([rule_classifier.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/intelligence/rule_classifier.py)): Fast, deterministic local semantic classifier detecting LaTeX formulas (`$$`), tables, K3 safety warnings, procedures, questions, and section-based keywords.
- **`NineRouterClient`** ([app/ai/router.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/ai/router.py)): OpenAI-compatible HTTP client connecting to 9Router Gateway with retry logic and active model selection.
- **`ContentType` Enum** ([app/intelligence/schemas.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/intelligence/schemas.py)): Comprehensive 80+ semantic role enumeration (`DEFINITION`, `EXPLANATION`, `FORMULA`, `PROCEDURE`, `EVIDENCE`, `QUESTION`, KTI BAB 1–5 roles).
- **`Settings`** ([app/config/settings.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/config/settings.py)): Centralized configuration management for AI Gateway URLs, timeouts, and active model choices.

---

## 2. Components Requiring Adapters

- **`MarkdownTreeParser` $\rightarrow$ `StructuralExtractor`**: `MarkdownTreeParser` outputs legacy `ContentTree`. `StructuralExtractor` (Stage 1) will wrap `MarkdownTreeParser` and output `StructuralTree` to maintain canonical Phase 1B data contracts.
- **`RuleClassifier` $\rightarrow$ `LocalClassifier`**: `RuleClassifier` returns `LocalClassificationResult`. `LocalClassifier` (Stage 3) will map these outputs into `RuleClassifiedUnit` schemas.
- **`SelectiveReasoner` $\rightarrow$ `AmbiguityResolver`**: Stage 4 will use a narrow, mockable `SemanticResolutionProvider` interface wrapping `NineRouterClient` with batching and offline fallback capability.

---

## 3. Existing Pydantic Conventions

- **Pydantic V2**: Models use `BaseModel` with `Field()`, `@field_validator`, `@model_validator(mode="after")`.
- **String Enums**: All enums inherit from `(str, Enum)` to ensure seamless JSON serialization.
- **Discriminated Unions**: Discriminated union fields use `Field(discriminator="kind")` or `Field(discriminator="payload_kind")`.
- **No Untyped Dicts**: Untyped `dict[str, Any]` is strictly prohibited in core semantic models; strongly-typed sub-models or typed mappings are used instead.

---

## 4. Existing Async Conventions

- Async methods use `async/await` with standard Python `asyncio`.
- Long-running tasks use async generators or callbacks (`progress_callback`).
- HTTP calls use `httpx.AsyncClient` with `tenacity` retry logic.
- Pipeline stages in Phase 1B will provide sync and async execution paths where appropriate (e.g. `AmbiguityResolver` is async for batch LLM calls, while `StructuralExtractor` and `PayloadBuilder` are synchronous).

---

## 5. Existing AI Gateway Interface

- Interface defined in `app.ai.client.AIClient` (`generate()`, `ping()`).
- Primary implementation: `NineRouterClient` in `app/ai/router.py`.
- Supports capabilities (`AICapability.SEMANTIC_REASONING`).
- For Phase 1B, `SemanticResolutionProvider` will injectably wrap `NineRouterClient`, allowing tests to run 100% offline with zero live API calls.

---

## 6. Existing Parser Structures

- Markdown line parsing, heading AST nesting (`#` to `######`), block code stripping, math block extraction (`$$...$$`), table cell parsing (`|...|`).
- `ContentBlock` tracks `source_line_start` and `source_line_end`.
- Stable section hashing via title slugs (`sec-pendahuluan`, `sec-prosedur-eksperimen`).

---

## 7. Dependency Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Modifying existing `app/intelligence/schemas.py` directly could break legacy Presentation pipeline. | Create new isolated subpackage `app/intelligence/schemas/` for Phase 1B schemas while preserving existing root `schemas.py` unchanged. |
| Incompatible imports between legacy `ContentBlock` and new `KnowledgeUnit`. | Clear module boundaries under `app/intelligence/schemas/`, `app/intelligence/graph/`, `app/intelligence/pipeline/`, and `app/intelligence/traceability/`. |
| Unintended invocation of live AI calls during automated unit tests. | Define mock `SemanticResolutionProvider` that resolves ambiguities locally in offline mode during pytest runs. |

---

## 8. Final Implementation Mapping for Phase 1B

```
app/intelligence/
├── schemas/
│   ├── __init__.py
│   ├── provenance.py              # KnowledgeProvenance
│   ├── payloads.py                # KnowledgePayloadUnion & 6 payload families
│   ├── knowledge_unit.py          # KnowledgeUnit & IntrinsicImportance schemas
│   ├── relationships.py           # KnowledgeRelationship & RelationshipEvidence
│   ├── intent_constraints.py      # IntentConstraints & typed constraint models
│   └── universal_manifest.py      # UniversalKnowledgeManifest schema
├── graph/
│   ├── __init__.py
│   ├── universal_graph.py         # UniversalKnowledgeGraph (General Directed Graph)
│   └── views.py                   # DependencyGraphView (DAG) & DependencyCycleDiagnostic
├── pipeline/
│   ├── __init__.py
│   ├── structural_extractor.py    # Stage 1: StructuralExtractor
│   ├── unit_normalizer.py         # Stage 2: UnitNormalizer
│   ├── local_classifier.py        # Stage 3: LocalClassifier
│   ├── ambiguity_resolver.py      # Stage 4: AmbiguityResolver
│   ├── payload_builder.py         # Stage 5: PayloadBuilder
│   ├── claim_evidence_extractor.py# Stage 6: ClaimEvidenceExtractor
│   ├── relationship_inferencer.py # Stage 7: RelationshipInferencer
│   ├── importance_analyzer.py     # Stage 8: ImportanceAnalyzer
│   ├── manifest_assembler.py      # Stage 9: ManifestAssembler
│   └── compiler.py                # KnowledgeCompiler Orchestrator
└── traceability/
    ├── __init__.py
    └── source_index.py            # SourceToKnowledgeUnitTraceabilityIndex

tests/unit/intelligence/
├── test_schemas.py                # Payload & Schema validation tests
├── test_stable_ids.py             # Deterministic stable ID hashing & collision tests
├── test_graph.py                  # UniversalKnowledgeGraph & DependencyGraphView DAG tests
├── test_pipeline_stages.py        # Individual 9 pipeline stage tests
└── test_compiler_integration.py   # Full offline compiler integration tests
```
