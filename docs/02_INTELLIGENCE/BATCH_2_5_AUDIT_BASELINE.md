# Batch 2.5 Audit Baseline

**Date:** 2026-08-23  
**Status:** Baseline Recorded Prior to Hardening  
**Scope:** Evaluation of Batch 2 (AI Content Intelligence & Agent Orchestration)

---

## 1. Repository Structure (Initial State)

```
KIR/
├── app/
│   ├── agents/
│   │   ├── __init__.py (empty stub)
│   │   ├── base.py
│   │   ├── content_intelligence_agent.py
│   │   ├── content_writer.py (empty stub)
│   │   ├── design_director.py (empty stub)
│   │   ├── document_planner.py
│   │   ├── quality_critic.py
│   │   └── visual_planner.py (empty stub)
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── fallback.py
│   │   ├── model_registry.py
│   │   ├── model_selector.py
│   │   ├── ollama_client.py
│   │   └── router.py
│   ├── config/
│   │   ├── __init__.py (empty stub)
│   │   └── settings.py
│   ├── core/
│   │   ├── __init__.py (empty stub)
│   │   ├── exceptions.py
│   │   ├── logging.py
│   │   └── schemas.py (empty stub)
│   ├── design/ (all empty stubs - Batch 3)
│   ├── document/ (all empty stubs - Batch 3-4)
│   ├── intelligence/
│   │   ├── __init__.py
│   │   ├── blueprint_proposer.py
│   │   ├── classifier.py
│   │   ├── importance_scorer.py
│   │   ├── normalizer.py
│   │   ├── output_validator.py
│   │   ├── relationship_extractor.py
│   │   ├── research_role_detector.py
│   │   ├── schemas.py
│   │   ├── segmenter.py
│   │   └── visual_intent_detector.py
│   ├── orchestration/
│   │   ├── __init__.py
│   │   └── pipeline.py
│   ├── quality/ (all empty stubs - Batch 5)
│   └── rendering/ (all empty stubs - Batch 4)
├── docs/
│   ├── 01_FOUNDATION/
│   ├── 02_INTELLIGENCE/
│   ├── DOCS_MANIFEST.md
│   └── README.md
├── prompts/
│   ├── content_intelligence_v1.yaml
│   ├── quality_critic_v1.yaml
│   ├── relationship_extractor_v1.yaml
│   ├── research_role_classifier_v1.yaml
│   └── visual_intent_detector_v1.yaml
└── tests/
    ├── __init__.py
    ├── test_output_validator.py
    └── test_segmenter.py
```

---

## 2. Existing Intelligence Modules

| Module | Purpose | Status in Baseline |
|---|---|---|
| `app.intelligence.normalizer.InputNormalizer` | Text normalization, unicode NFC, protected regions | Implemented |
| `app.intelligence.segmenter.ContentSegmenter` | AST-like heading hierarchy & block segmentation | Implemented |
| `app.intelligence.classifier.SemanticClassifier` | General semantic type classification via LLM | Prompt hardcoded (needs YAML loader) |
| `app.intelligence.research_role_detector.ResearchRoleDetector` | KTI BAB 1-5 semantic role detection | Prompt hardcoded (needs YAML loader) |
| `app.intelligence.relationship_extractor.RelationshipExtractor` | Traceability relationship extraction | Prompt hardcoded (needs YAML loader) |
| `app.intelligence.importance_scorer.ImportanceScorer` | Deterministic multi-factor importance scoring | Implemented |
| `app.intelligence.visual_intent_detector.VisualIntentDetector` | Layout-agnostic visual intent detector | Prompt hardcoded (needs YAML loader) |
| `app.intelligence.blueprint_proposer.BlueprintProposer` | Content-to-blueprint grouping algorithm | Implemented |
| `app.intelligence.output_validator.OutputValidator` | LLM JSON parsing, schema validation, repair loop | Implemented |
| `app.intelligence.schemas` | Pydantic v2 schemas and enums | Implemented |

---

## 3. Existing Tests & Count

- Baseline test count: **5 tests** across 2 files (`test_segmenter.py`, `test_output_validator.py`).
- Test coverage gaps:
  - No KTI BAB 1–5 domain tests
  - No research traceability graph validation tests
  - No source fidelity / hallucination prevention tests
  - No fallback chain offline tests
  - No end-to-end integration tests
  - No schema boundary tests

---

## 4. Existing Dependency & AI Provider Structure

- AI Provider layer properly abstracts capability (`AICapability`) through `AIClient` base class.
- `NineRouterClient` and `OllamaClient` adhere to `AIClient`.
- `ModelSelector` resolves capabilities without exposing hardcoded model names to intelligence logic.
- `FallbackChain` routes between primary and secondary providers.

---

## 5. Suspected Risks & Defect Baseline

1. **Missing ResearchTraceability Engine**: `ContentIntelligenceAgent` did not build the `ResearchTraceability` object from classified units and relationships; `AnalysisResult.research_traceability` was left empty.
2. **Hardcoded System Prompts**: Intelligence classes hardcoded system prompt strings instead of loading them via a YAML prompt loader.
3. **Pydantic Protected Namespace Warning**: `GenerationResponse.model_used` caused a warning due to the `model_` namespace.
4. **Empty `.env.example` and missing `venv/` in `.gitignore`**: Environment template was blank.
5. **Insufficient Test Suite**: Only 5 unit tests existed; missing full offline test fixtures and KTI BAB 1–5 tests.
6. **Limited Dependency Injection**: Intelligence agent and pipeline classes had tight instantiation of internal subcomponents, preventing easy mocking for offline tests.
