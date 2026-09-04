# Import Graph and Layer Responsibility Audit

**Date:** 2026-08-23  
**Batch:** 2.5 Architecture Audit  
**Scope:** Verification of import directions, circular dependencies, and layer boundaries.

---

## 1. Conceptual Layer Architecture

```
[ ENTRYPOINT / ORCHESTRATION ]  app.orchestration.pipeline
            ↓
[ AGENTS / APPLICATION ]        app.agents (ContentIntelligenceAgent, DocumentPlanner, QualityCritic)
            ↓
[ INTELLIGENCE DOMAIN ]         app.intelligence (Normalizer, Segmenter, Classifier, RoleDetector,
                                                  RelationshipExtractor, ImportanceScorer,
                                                  VisualIntentDetector, TraceabilityEngine,
                                                  BlueprintProposer, OutputValidator)
            ↓
[ AI ADAPTERS & PROVIDERS ]     app.ai (AIClient, ModelSelector, ModelRegistry, FallbackChain, Router, Ollama)
            ↓
[ CORE & CONFIGURATION ]        app.core (Exceptions, Logging), app.config (AppSettings)
```

---

## 2. Module Import Matrix

| Module | Layer | Imports | Imported By | Allowed? | Notes |
|---|---|---|---|---|---|
| `app.config.settings` | Configuration | `pydantic`, `pydantic_settings`, `pathlib` | `app.core`, `app.ai`, `app.intelligence` | **YES** | Root configuration, no downward dependencies |
| `app.core.exceptions` | Core | `typing` | All layers | **YES** | Zero external app dependencies |
| `app.core.logging` | Core | `structlog`, `logging`, `sys` | All layers | **YES** | Zero external app dependencies |
| `app.ai.client` | AI Layer | `pydantic`, `abc`, `enum` | `app.ai.*`, `app.intelligence.*` | **YES** | Base interface and DTOs |
| `app.ai.router` | AI Layer | `httpx`, `tenacity`, `app.ai.client`, `app.config.settings`, `app.core.exceptions`, `app.core.logging` | `app.ai.model_registry` | **YES** | Concrete provider adapter |
| `app.ai.ollama_client` | AI Layer | `httpx`, `tenacity`, `app.ai.client`, `app.config.settings`, `app.core.exceptions`, `app.core.logging` | `app.ai.model_registry` | **YES** | Concrete provider adapter |
| `app.ai.model_registry`| AI Layer | `app.ai.client`, `app.ai.router`, `app.ai.ollama_client` | `app.ai.model_selector`, `app.ai.fallback` | **YES** | Factory registry |
| `app.ai.model_selector`| AI Layer | `app.ai.client`, `app.ai.model_registry`, `app.config.settings`, `app.core.exceptions`, `app.core.logging` | `app.ai.fallback` | **YES** | Capability resolver |
| `app.ai.fallback` | AI Layer | `app.ai.client`, `app.ai.model_selector`, `app.ai.model_registry`, `app.config.settings`, `app.core.exceptions`, `app.core.logging` | `app.intelligence.output_validator` | **YES** | Fallback execution chain |
| `app.intelligence.schemas` | Intelligence | `pydantic`, `enum`, `uuid`, `datetime` | `app.intelligence.*`, `app.agents.*`, `app.orchestration.*` | **YES** | Pure domain schema |
| `app.intelligence.normalizer` | Intelligence | `unicodedata`, `re`, `chardet`, `app.core.exceptions`, `app.core.logging` | `app.intelligence.segmenter`, `app.agents.content_intelligence_agent` | **YES** | Text normalization |
| `app.intelligence.segmenter` | Intelligence | `re`, `uuid`, `app.core.exceptions`, `app.core.logging`, `app.intelligence.normalizer`, `app.intelligence.schemas` | `app.agents.content_intelligence_agent` | **YES** | AST-like segmentation |
| `app.intelligence.output_validator` | Intelligence | `json`, `re`, `pydantic`, `app.ai.client`, `app.ai.fallback`, `app.config.settings`, `app.core.exceptions`, `app.core.logging` | Intelligence classifiers & agents | **YES** | Contract enforcer |
| `app.intelligence.classifier` | Intelligence | `app.ai.client`, `app.config.settings`, `app.core.exceptions`, `app.core.logging`, `app.intelligence.output_validator`, `app.intelligence.schemas` | `app.agents.content_intelligence_agent` | **YES** | Semantic reasoning |
| `app.intelligence.research_role_detector` | Intelligence | `app.ai.client`, `app.config.settings`, `app.core.exceptions`, `app.core.logging`, `app.intelligence.output_validator`, `app.intelligence.schemas` | `app.agents.content_intelligence_agent` | **YES** | KTI semantic role reasoning |
| `app.intelligence.relationship_extractor` | Intelligence | `app.ai.client`, `app.config.settings`, `app.core.exceptions`, `app.core.logging`, `app.intelligence.output_validator`, `app.intelligence.schemas` | `app.agents.content_intelligence_agent` | **YES** | Traceability relationship extraction |
| `app.intelligence.importance_scorer` | Intelligence | `app.core.logging`, `app.intelligence.schemas` | `app.agents.content_intelligence_agent` | **YES** | Pure deterministic calculation |
| `app.intelligence.visual_intent_detector` | Intelligence | `app.ai.client`, `app.config.settings`, `app.core.exceptions`, `app.core.logging`, `app.intelligence.output_validator`, `app.intelligence.schemas` | `app.agents.content_intelligence_agent` | **YES** | Layout-agnostic visual intent detector |
| `app.intelligence.blueprint_proposer` | Intelligence | `uuid`, `app.core.exceptions`, `app.core.logging`, `app.intelligence.schemas` | `app.agents.document_planner` | **YES** | Content-to-blueprint grouping |
| `app.agents.base` | Agents | `abc`, `app.core.exceptions`, `app.core.logging` | `app.agents.*` | **YES** | Agent base class |
| `app.agents.content_intelligence_agent` | Agents | `app.agents.base`, `app.intelligence.*` | `app.orchestration.pipeline` | **YES** | Pipeline stage agent |
| `app.agents.document_planner` | Agents | `app.agents.base`, `app.ai.client`, `app.intelligence.blueprint_proposer`, `app.intelligence.output_validator`, `app.intelligence.schemas` | `app.orchestration.pipeline` | **YES** | Blueprint proposal agent |
| `app.agents.quality_critic` | Agents | `app.agents.base`, `app.ai.client`, `app.intelligence.output_validator`, `app.intelligence.schemas` | `app.orchestration.pipeline` | **YES** | Quality assurance agent |
| `app.orchestration.pipeline` | Orchestration | `datetime`, `app.agents.*`, `app.core.exceptions`, `app.core.logging`, `app.intelligence.schemas` | Entrypoint | **YES** | Top-level workflow runner |

---

## 3. Circular Dependency Audit Result

- **Direct circular imports (A → B → A):** NONE DETECTED.
- **Indirect circular imports (A → B → C → A):** NONE DETECTED.
- **Upward layer violations (Core importing Agents/Rendering):** NONE DETECTED.
- **Rendering coupling in Intelligence layer:** NONE DETECTED (No HTML, CSS, Playwright, or Page coordinates imported in `app.intelligence` or `app.agents`).

---

## 4. Status of Stubs in Unimplemented Batches

The following files in `app/` are empty (0 lines) and are **intentionally reserved** for subsequent batches:
- `app/agents/content_writer.py` (Batch 3/6)
- `app/agents/design_director.py` (Batch 3)
- `app/agents/visual_planner.py` (Batch 3)
- `app/design/*` (Batch 3 - Design System)
- `app/document/*` (Batch 3-4 - Document Assembly)
- `app/rendering/*` (Batch 4 - PDF Rendering)
- `app/quality/*` (Batch 5 - Quality Inspection)
- `app/main.py` (Batch 6 - CLI/Application Entrypoint)

None of these reserved stubs are imported by Batch 2 intelligence modules.
