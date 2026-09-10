# Universal Artifact Architecture Audit

## 1. Executive Summary

This document presents a comprehensive **Forensic Architecture Audit (Phase 0)** of the KIR & Mengajar AI Document Intelligence repository. The audit evaluates the current codebase state to prepare for the implementation of the **Universal Document Intelligence System V5** across four distinct target output formats:

1. **Presentation 16:9** (`teaching_presentation` / `research_presentation`)
2. **Handout Lengkap A4** (`detailed_handout`)
3. **Worksheet / LKS** (`student_worksheet` / `exam_worksheet`)
4. **Dokumen KTI Ilmiah** (`kti_document`)

### Key Audit Findings

- **Asymmetric Pipeline Dual-Branching**: The production pipeline (`MaterialProductionPipeline` in [production_pipeline.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/orchestration/production_pipeline.py)) suffers from a severe structural bifurcation. Presentation 16:9 executes a rich, dedicated 10-stage deterministic + AI pipeline with real-time progress callbacks, 25 specialized quality gates, and a deterministic repair/re-render loop. Conversely, Handout, Worksheet, and KTI Document are routed to a generic, monolithic fallback branch ("Branch B") that skips structural tree parsing, content manifest building, visual grammar planning, format-specific quality gates, and iterative repair.
- **Pervasive Format Collapse**: The three non-presentation formats (Handout, Worksheet, Scientific Document) are currently **collapsed into a single layout paradigm**. They share the exact same physical format contract (`a4_portrait`), the same 1-step-to-1-page allocation mechanism in [bridge.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/composition/bridge.py), and identical generic fallback blueprints (a 3-step sequence: Hook -> Concept -> Summary).
- **Presentation Assumption Leakage**: Presentation concepts leak into supposedly artifact-neutral core modules. For example, [content_manifest.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/intelligence/content_manifest.py) bakes `min_slides`, `target_slides`, and `max_slides` estimation directly into `ContentManifest`.
- **Ineffective Non-Presentation QA and Repair**: While Presentation 16:9 features a closed-loop `DeterministicRepairEngine` that mutates `SlidePlan`, invalidates state, re-renders HTML/PDF, and re-evaluates QA rounds, the non-presentation formats run a passive `QualityEvaluationEngine` that merely logs scores without triggering re-rendering or repair.
- **Rendering Layer vs. Artifact Intelligence Confusion**: The system successfully uses a unified rendering architecture (Jinja2 + Playwright Chromium PDF export), which is architectural sound. However, because physical rendering is decoupled from artifact intelligence, the repository currently mistakes shared HTML/CSS rendering for shared document intelligence, leaving Handout, Worksheet, and Scientific Document without dedicated structural planning.

---

## 2. Repository Entry Points

The codebase provides three primary user-facing interfaces: FastAPI Web Server, `mengajar` CLI, and `kir` CLI.

### Summary Table: Format to First Function Execution Trace

| Target Format | UI / CLI Selector | FastAPI / CLI Handler | Primary Orchestration Entry Point | Format Contract ID |
|---|---|---|---|---|
| **Presentation 16:9** | `teaching_presentation` / `research_presentation` | `POST /api/generate` ([server.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/web/server.py#L484)) / `cmd_generate()` ([mengajar_cli.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/cli/mengajar_cli.py#L88)) | `MaterialProductionPipeline.produce_artifact()` (Branch A: `is_presentation=True`) | `presentation_16_9` |
| **Handout Lengkap A4** | `detailed_handout` | `POST /api/generate` ([server.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/web/server.py#L486)) / `cmd_generate()` ([mengajar_cli.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/cli/mengajar_cli.py#L93)) | `MaterialProductionPipeline.produce_artifact()` (Branch B: `is_presentation=False`) | `a4_portrait` |
| **Worksheet / LKS** | `exam_worksheet` / `student_worksheet` | `POST /api/generate` ([server.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/web/server.py#L487)) / `cmd_generate()` ([mengajar_cli.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/cli/mengajar_cli.py#L98)) | `MaterialProductionPipeline.produce_artifact()` (Branch B: `is_presentation=False`) | `a4_portrait` |
| **Dokumen KTI Ilmiah** | `kti_document` | `POST /api/generate` ([server.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/web/server.py#L488)) / `cmd_generate()` ([kir_cli.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/cli/kir_cli.py#L88)) | `MaterialProductionPipeline.produce_artifact()` (Branch B: `is_presentation=False`) | `a4_portrait` |

### Concrete Answer to Entry Point Call Sequence:
**"Ketika user memilih Presentation, fungsi apa yang pertama kali dipanggil?"**
1. Web UI sends JSON payload to `POST /api/generate` in [server.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/web/server.py#L258).
2. `api_generate()` spawns background task `_run_job_pipeline()`.
3. `_run_job_pipeline()` maps `req.format == "teaching_presentation"` to `(TargetArtifactType.TEACHING_PRESENTATION, "presentation_16_9")`.
4. `_run_job_pipeline()` instantiates `pipeline = MaterialProductionPipeline()`.
5. `_run_job_pipeline()` invokes `pipeline.produce_artifact(target_artifact=TargetArtifactType.TEACHING_PRESENTATION, target_format="presentation_16_9", ...)` ([server.py:L521](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/web/server.py#L521)).
6. Inside `produce_artifact()`, `is_presentation` evaluates to `True`, triggering **Branch A** (the 10-stage presentation flow starting at Task 1: `MarkdownTreeParser().parse()`).

---

## 3. Actual Execution Trace

### 3.1 Presentation (16:9 Slide Deck)

```
UI / CLI Choice
  ↓
POST /api/generate (server.py) / _run_pipeline_async() (shared.py)
  ↓
MaterialProductionPipeline.produce_artifact() [app/orchestration/production_pipeline.py]
  ↓ (is_presentation == True)
TASK 1: MarkdownTreeParser.parse() [app/intelligence/markdown_tree_parser.py]
  ↓ (Produces ContentTree)
TASK 2: RuleClassifier.classify() [app/intelligence/rule_classifier.py]
  ↓ (Local taxonomy assignment; identifies ambiguous paragraph blocks)
TASK 3: Selective AI Reasoning via NineRouterClient [app/ai/router.py]
  ↓ (Batched inference for ambiguous blocks only)
TASK 4: ContentManifestBuilder.build() [app/intelligence/content_manifest.py]
  ↓ (Produces ContentManifest with critical/important concepts & slide bounds)
TASK 5: SlideArchitect.plan() [app/presentation/slide_architect.py]
  ↓ (Produces SlidePlan: acts, slide titles, layouts, claim units)
TASK 6: SlideGenerator.generate_slide() [app/presentation/slide_generator.py]
  ↓ (Produces list of GeneratedSlide objects with rendered HTML cards)
TASK 7: DocumentComposition Assembly [app/composition/schemas.py]
  ↓ (Wraps slides into PageComposition objects with DocumentMode.PRESENTATION_16_9)
TASK 8: MasterRenderEngine.render() [app/rendering/engine.py]
  ↓ HTMLAssembler (app/rendering/html/assembler.py using document.html + .page-presentation)
  ↓ PlaywrightRenderer.export_pdf() (Chromium headful/headless PDF export)
  ↓ (Produces PDF v1)
TASK 9: PresentationQualityGate.evaluate() [app/presentation/quality_gate.py]
  ↓ (Evaluates 25 Presentation Quality Gates; active QA stored in PipelineState)
TASK 10: DeterministicRepairEngine.repair() [app/presentation/repair_engine.py]
  ↓ (If repairable failures exist: mutates SlidePlan, invalidates dependent state)
  ↓ (Re-generates slides → Re-composes Document → Re-renders PDF v2)
  ↓ (Re-evaluates PresentationQualityGate Round 2 → RepairConvergenceAnalyzer)
QualityDecisionEngine.evaluate() [app/presentation/decision_engine.py]
  ↓ (Authoritative Export Decision: EXPORT_APPROVED / BLOCKED)
GenerationReporter.emit_report() [app/presentation/generation_reporter.py] + ContactSheetGenerator
  ↓
Export Validated PDF + Contact Sheet PNG + Diagnostic Reports
```

### 3.2 Handout (Detailed A4 Document)

```
UI / CLI Choice
  ↓
POST /api/generate (server.py) / _run_pipeline_async() (shared.py)
  ↓
MaterialProductionPipeline.produce_artifact() [app/orchestration/production_pipeline.py]
  ↓ (is_presentation == False)
ContentIntelligenceAgent.execute() [app/agents/content_intelligence_agent.py]
  ↓ (Calls AI model to produce DocumentAnalysis; fallback on error)
MaterialBlueprintGenerator.generate_from_analysis() [app/intelligence/material_blueprint_generator.py]
  ↓ (Produces SemanticMaterialBlueprint; fallback 3-step blueprint on exception)
CompositionBridge.compose_material() [app/composition/bridge.py]
  ↓ (Resolves capabilities for pedagogical steps; maps each step 1:1 to PageComposition)
MasterRenderEngine.render() [app/rendering/engine.py]
  ↓ HTMLAssembler (app/rendering/html/assembler.py using document.html + .page-a4-portrait)
  ↓ PlaywrightRenderer.export_pdf() (Chromium PDF export)
QualityEvaluationEngine.evaluate_artifact() [app/quality/engine.py]
  ↓ (Calculates generic score across 6 quality dimensions; logs findings)
  ↓ (NO repair loop executed; NO re-rendering; NO export gate blocking)
Return MaterialJobResult with PDF path
```

### 3.3 Worksheet (Student LKS A4)

```
UI / CLI Choice
  ↓
POST /api/generate (server.py) / _run_pipeline_async() (shared.py)
  ↓
MaterialProductionPipeline.produce_artifact() [app/orchestration/production_pipeline.py]
  ↓ (is_presentation == False)
ContentIntelligenceAgent.execute() [app/agents/content_intelligence_agent.py]
  ↓ (Same generic AI prompt execution as Handout)
MaterialBlueprintGenerator.generate_from_analysis() [app/intelligence/material_blueprint_generator.py]
  ↓ [LEAKAGE] Uses generic PedagogicalPattern (Hook -> Concept -> Summary).
  ↓ (NO student exercise scaffolding, NO answer key separation, NO workspace planning)
CompositionBridge.compose_material() [app/composition/bridge.py]
  ↓ [FORMAT COLLAPSE] Maps generic steps 1:1 to A4 portrait pages using presentation capabilities
MasterRenderEngine.render() [app/rendering/engine.py]
  ↓ HTMLAssembler (document.html + .page-a4-portrait) → PlaywrightRenderer
QualityEvaluationEngine.evaluate_artifact() [app/quality/engine.py]
  ↓ (Generic document quality evaluation; NO worksheet-specific QA)
Return MaterialJobResult with PDF path
```

### 3.4 Scientific Document (KTI Paper A4)

```
UI / CLI Choice
  ↓
POST /api/generate (server.py) / _run_pipeline_async() (shared.py)
  ↓
MaterialProductionPipeline.produce_artifact() [app/orchestration/production_pipeline.py]
  ↓ (is_presentation == False)
ContentIntelligenceAgent.execute() [app/agents/content_intelligence_agent.py]
  ↓ (Sets DocumentGenre.RESEARCH_REPORT; executes AI prompt)
MaterialBlueprintGenerator.generate_from_analysis() [app/intelligence/material_blueprint_generator.py]
  ↓ [LEAKAGE] Falls back to 3-step sequence (Pendahuluan -> Alat/Bahan -> Data/Kesimpulan).
  ↓ (NO formal IMRAD/KTI structure engine, NO citation graph, NO academic typography rules)
CompositionBridge.compose_material() [app/composition/bridge.py]
  ↓ [FORMAT COLLAPSE] Maps 3 steps 1:1 to A4 portrait pages
MasterRenderEngine.render() [app/rendering/engine.py]
  ↓ HTMLAssembler (document.html + .page-a4-portrait) → PlaywrightRenderer
QualityEvaluationEngine.evaluate_artifact() [app/quality/engine.py]
  ↓ (Generic document quality evaluation; NO KTI-specific QA)
Return MaterialJobResult with PDF path
```

---

## 4. Shared Architecture

The components listed below represent genuinely shared core architecture utilized by all four output formats:

- **Web Server & Gateway API**: [app/web/server.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/web/server.py) and [app/ai/router.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/ai/router.py) (FastAPI endpoint, job management, SSE event broadcasting, 9Router gateway integration).
- **Format Registry**: [app/formats/registry.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/formats/registry.py) and [app/formats/contracts.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/formats/contracts.py) (central physical canvas format contract definition: `presentation_16_9`, `a4_portrait`, `a4_landscape`).
- **Master Rendering Engine**: [app/rendering/engine.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/rendering/engine.py) (orchestrates rendering steps across all formats).
- **HTML & Template Assembly**: [app/rendering/html/assembler.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/rendering/html/assembler.py) and [app/rendering/html/templates/document.html](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/rendering/html/templates/document.html) (Jinja2 HTML compilation and CSS `@page` rule generation).
- **Playwright PDF Export**: [app/rendering/playwright/pdf_exporter.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/rendering/playwright/pdf_exporter.py) (Chromium headless PDF rendering with custom dimensions).
- **Capability Registry**: [app/capabilities/registry.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/capabilities/registry.py) (central registry of visual and content rendering capabilities).
- **Settings & Logging**: [app/config/settings.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/config/settings.py) and [app/core/logging.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/core/logging.py).

---

## 5. Format-Specific Architecture

### Current Real Implementation vs. Expected Architecture

| Target Format | Actual Dedicated Modules in Codebase | Missing Architecture | Audit Assessment |
|---|---|---|---|
| **Presentation 16:9** | `MarkdownTreeParser`, `RuleClassifier`, `ContentManifestBuilder`, `SlideArchitect`, `SlideGenerator`, `PresentationQualityGate`, `DeterministicRepairEngine`, `PresentationRhythmAnalyzer`, `SlideDeduplicationPlanner` | None. Highly mature presentation intelligence engine. | **Fully Implemented** |
| **Handout A4** | Uses `ContentIntelligenceAgent` + `MaterialBlueprintGenerator` + `CompositionBridge` | Dedicated Handout Structural Parser, Multi-column A4 Layout Planner, Handout Quality Gate, Handout Repair Engine. | **Partial / Generic Fallback** |
| **Worksheet / LKS** | Uses generic Branch B (`STUDENT_WORKSHEET` enum passed as parameter) | Dedicated Worksheet Structuring Engine, Student Response Space Planner, Problem & Solution Pair Engine, Worksheet Quality Gate, Worksheet Repair Engine. | **Missing Architecture (Format Collapse)** |
| **Scientific Document** | Uses generic Branch B (`DocumentGenre.RESEARCH_REPORT` enum passed as parameter) | Dedicated KTI/IMRAD Structural Parser, Formal Academic Section Planner, Citation & Reference Engine, KTI Quality Gate, KTI Repair Engine. | **Missing Architecture (Format Collapse)** |

---

## 6. Dependency Map

### Current Execution & Module Dependency Graph

```
                                  ┌────────────────────────┐
                                  │   app/web/server.py    │
                                  │   app/cli/shared.py    │
                                  └───────────┬────────────┘
                                              │
                                              ▼
                             ┌──────────────────────────────────┐
                             │  MaterialProductionPipeline      │
                             │ (app/orchestration/production)   │
                             └────────┬─────────────────┬───────┘
                                      │                 │
            is_presentation == True   │                 │   is_presentation == False
    ┌─────────────────────────────────┘                 └───────────────────────────────┐
    ▼                                                                                   ▼
┌──────────────────────────────┐                                       ┌──────────────────────────────┐
│ app/intelligence/            │                                       │ app/agents/                  │
│  - markdown_tree_parser.py   │                                       │  - content_intelligence_     │
│  - rule_classifier.py        │                                       │    agent.py                  │
│  - content_manifest.py       │                                       └──────────────┬───────────────┘
└──────────────┬───────────────┘                                                      │
               │                                                                      ▼
               ▼                                                       ┌──────────────────────────────┐
┌──────────────────────────────┐                                       │ app/intelligence/            │
│ app/presentation/            │                                       │  - material_blueprint_       │
│  - slide_architect.py        │                                       │    generator.py              │
│  - slide_generator.py        │                                       └──────────────┬───────────────┘
└──────────────┬───────────────┘                                                      │
               │                                                                      ▼
               ▼                                                       ┌──────────────────────────────┐
┌──────────────────────────────┐                                       │ app/composition/             │
│ app/composition/             │                                       │  - bridge.py                 │
│  - schemas.py (Presentation) │                                       │ (Maps 1 step → 1 A4 page)    │
└──────────────┬───────────────┘                                       └──────────────┬───────────────┘
               │                                                                      │
               ├──────────────────────────────────────────────────────────────────────┘
               ▼
┌──────────────────────────────┐
│ app/rendering/               │
│  - engine.py                 │
│  - html/assembler.py         │
│  - playwright/pdf_exporter.py│
└──────────────┬───────────────┘
               │
               ├──────────────────────────────────┐
               │                                  │
    (Presentation QA & Repair)         (Non-Presentation Generic QA)
               ▼                                  ▼
┌──────────────────────────────┐   ┌──────────────────────────────┐
│ app/presentation/            │   │ app/quality/                 │
│  - quality_gate.py           │   │  - engine.py                 │
│  - repair_engine.py          │   │  (No repair loop, no export  │
│  - decision_engine.py        │   │   gate enforcement)          │
└──────────────────────────────┘   └──────────────────────────────┘
```

### Dependency Directives & Potential Circularities
1. `production_pipeline.py` depends directly on both presentation-specific modules (`app.presentation.*`) and generic orchestration modules (`app.composition.bridge`, `app.quality.engine`).
2. **Circular Dependency Risk**: `app.presentation.quality_gate` imports `ContentManifest` from `app.intelligence.content_manifest`, while `ContentManifest` imports `ContentTree` from `app.intelligence.markdown_tree_parser`. Meanwhile `production_pipeline` imports `PipelineState` which references both `ContentManifest` and `QualityRound`.

---

## 7. Current Content Transformation Model

| Stage | Presentation 16:9 | Handout Lengkap A4 | Worksheet / LKS | Scientific Document (KTI) |
|---|---|---|---|---|
| **Semantic Unit** | `SemanticBlock` (Header, Paragraph, Formula, Table, Warning) | `PedagogicalStep` | `PedagogicalStep` | `PedagogicalStep` |
| **Concept Grouping** | `ManifestConcept` (Critical, Important, Supporting) | Generic LLM Analysis JSON | `LEAKAGE` (Generic LLM Analysis) | `LEAKAGE` (Generic LLM Analysis) |
| **Architecture** | `SlidePlan` (Narrative Acts, Storyboard, Claim Units) | `PedagogicalBlueprint` (Hook, Concept, Summary) | `LEAKAGE` (Generic 3-step sequence) | `LEAKAGE` (Generic 3-step sequence) |
| **Structural Unit** | `PlannedSlide` (Title, Layout, Visual Intent, References) | `PedagogicalStep` | `LEAKAGE` (PedagogicalStep) | `LEAKAGE` (PedagogicalStep) |
| **Composition** | `DocumentComposition` (`page_type="slide"`, 16:9 Grid) | `DocumentComposition` (`page_type="document_page"`) | `LEAKAGE` (1 step = 1 page) | `LEAKAGE` (1 step = 1 page) |
| **QA** | `PresentationQualityGate` (25 Gates, Visual DOM, Cognitive Load) | `QualityEvaluationEngine` (Generic text/density score) | `LEAKAGE` (Generic text/density score) | `LEAKAGE` (Generic text/density score) |
| **Repair** | `DeterministicRepairEngine` (Deduplication, Reflow, Re-render, Re-QA) | `MISSING` (No repair loop) | `MISSING` (No repair loop) | `MISSING` (No repair loop) |

---

## 8. Format Collapse Analysis

Format collapse occurs when distinct output formats are forced through an identical execution pipeline or layout model. Below is the forensic audit of the 10 collapse symptoms:

| Collapse Symptom | Observed State in Repository | Severity |
|---|---|---|
| **1. Semantic block directly becomes page/slide** | In Branch B (Handout, Worksheet, KTI), `CompositionBridge` iterates over `material.pedagogy.sequence` and creates 1 `PageComposition` per step regardless of content length or format. | **CRITICAL** |
| **2. All formats use identical ContentManifest without artifact transformation** | `ContentManifestBuilder` is currently only called in Presentation Branch. Non-presentation formats bypass manifest generation entirely or use un-transformed LLM output. | **HIGH** |
| **3. Universal layout planner used without format awareness** | `CompositionBridge` delegates block styling to capability renderers designed for presentation cards (e.g. `presentation.concept_introduction`). | **HIGH** |
| **4. Presentation assumptions leak to Handout** | Non-presentation formats rendered via `CompositionBridge` execute presentation capabilities (`presentation.hero_statement`, `presentation.takeaway_summary`). | **HIGH** |
| **5. Handout assumptions leak to Worksheet** | Worksheet format uses the exact same `PedagogicalBlueprint` sequence and capabilities as Handout without creating question spaces or answer keys. | **CRITICAL** |
| **6. Worksheet is only Handout + questions** | Codebase has no specialized worksheet transformer. Generating a worksheet simply appends question blocks to standard handout pages. | **CRITICAL** |
| **7. Scientific Document is only Handout + formal headings** | KTI Document generation passes `DocumentGenre.RESEARCH_REPORT` to AI, but falls back to standard 3-step pedagogical layout without academic paper structure. | **CRITICAL** |
| **8. QA uses same thresholds for all formats** | Non-presentation quality evaluation in `QualityEvaluationEngine` uses generic density thresholds without format-specific geometric validation. | **HIGH** |
| **9. Repair engine generic without knowing artifact type** | `DeterministicRepairEngine` is hardcoded specifically for Presentation (`SlidePlan`). Non-presentation formats have NO active repair loop. | **CRITICAL** |
| **10. Renderer treated as artifact intelligence** | `MasterRenderEngine` and `PlaywrightRenderer` can render A4 or 16:9 PDF geometry, causing the team to mistake rendering capability for structural document intelligence. | **HIGH** |

---

## 9. Cross-Format Leakage Analysis

1. **Slide Count Leaked into Content Manifest**:
   In [content_manifest.py:L60-L63](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/intelligence/content_manifest.py#L60-L63), the class `ContentManifest` includes fields:
   ```python
   min_slides: int
   target_slides: int
   max_slides: int
   ```
   `ContentManifest` should be a pure, artifact-neutral representation of source knowledge. Calculating slide bounds inside the manifest leaks presentation constraints into universal knowledge extraction.

2. **Presentation Capabilities Leaked into Generic Blueprint Generator**:
   In [production_pipeline.py:L662-L664](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/orchestration/production_pipeline.py#L662-L664), the fallback logic for non-presentation documents assigns presentation capability IDs:
   ```python
   ProductionRequirement(
       step_id=step_hook.id,
       semantic_type="hook",
       required_capability_id="presentation.hero_statement",
   )
   ```
   This causes A4 Handouts, Worksheets, and KTI Documents to render presentation slide cards on A4 pages.

3. **Presentation QA Leaked into Universal Progress Reporting**:
   `PipelineProgressReporter` in [stage_registry.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/orchestration/stage_registry.py) references presentation terms ("25 Gerbang Mutu", "Slide Storyboard") across standard pipeline stage labels.

---

## 10. AI Usage Audit

The system follows a **Local First, Selective AI** philosophy. Below is the forensic audit of AI usage across pipeline stages:

| Stage | Classification | Is AI Necessary? | AI Input | AI Output | Deterministic Adequacy | Batching | Fallback | Failure Stops Pipeline? | Stored? |
|---|---|---|---|---|---|---|---|---|---|
| **1. Structural Parsing** | `DETERMINISTIC` | No | Raw Markdown Text | `ContentTree` | 100% Adequate | N/A | Regex Parser | No | Yes |
| **2. Local Semantic Classification** | `RULE-BASED` | No | `ContentBlock` text | `SemanticBlockType` | 85-90% Adequate | N/A | Heuristic Rules | No | Yes |
| **3. Selective AI Reasoning** | `AI-ASSISTED` | Only for ambiguous blocks | Ambiguous paragraph text | Semantic taxonomy label | Local rules sufficient for clear text | Batched | Local rule fallback | No | Yes |
| **4. Content Manifest** | `DETERMINISTIC` | No | `ContentTree` | `ContentManifest` | 100% Adequate | N/A | Heuristic manifest builder | No | Yes |
| **5. Architecture Planning** | `RULE-BASED` / `AI-ASSISTED` | For complex storyboarding | `ContentManifest` | `SlidePlan` / `PedagogicalBlueprint` | Rule-based `SlideArchitect` handles presentation well | Single Call | Rule-based architect | No | Yes |
| **6. Visual Grammar & Composition** | `DETERMINISTIC` | No | `SlidePlan` / Blueprint | `DocumentComposition` | 100% Adequate | N/A | Canonical Layout Matrix | No | Yes |
| **7. Rendering** | `DETERMINISTIC` | No | `DocumentComposition` | HTML / PDF File | 100% Adequate | N/A | Playwright / Jinja2 | Yes | Yes |
| **8. Quality Assurance** | `DETERMINISTIC` | No | PDF File + `SlidePlan` + DOM | `QualityRound` / `QualityReport` | 100% Adequate | N/A | PyMuPDF + Regex | No | Yes |
| **9. Repair & Refinement** | `DETERMINISTIC` | No | `QualityRound` + `SlidePlan` | Repaired `SlidePlan` | 100% Adequate | N/A | Deterministic repair actions | No | Yes |

---

## 11. Current 10-Stage Pipeline Audit

The pipeline is defined in [stage_registry.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/orchestration/stage_registry.py) as 10 discrete stages:
1. `STRUCTURAL_PARSING`
2. `LOCAL_SEMANTIC_CLASSIFICATION`
3. `SELECTIVE_AI_REASONING`
4. `CONTENT_MANIFEST`
5. `ARCHITECTURE_PLANNING`
6. `CONTENT_TRANSFORMATION`
7. `COMPOSITION`
8. `RENDERING`
9. `QUALITY_ASSURANCE`
10. `REPAIR_AND_REFINEMENT`

### Forensic Findings:
- **Presentation 16:9**: Implements all 10 stages explicitly and strictly inside `if is_presentation:` ([production_pipeline.py:L178-L592](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/orchestration/production_pipeline.py#L178-L592)). Progress events are emitted for every stage.
- **Handout, Worksheet, Scientific Document**: **DO NOT execute the 10-stage pipeline**. In Branch B ([production_pipeline.py:L594-L800](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/orchestration/production_pipeline.py#L594-L800)), stages 1, 2, 3, 4, 5, 6, 9, 10 are completely skipped or merged into a single call to `ContentIntelligenceAgent`. Emitted progress labels for non-presentation formats are **pure progress UI indicators** rather than active architectural stages.

---

## 12. Quality System Audit

The codebase contains two distinct quality evaluation systems:

1. **Presentation Quality Gate System**: ([app/presentation/quality_gate.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/presentation/quality_gate.py))
   - 25 presentation-specific quality gates (e.g., Gate 1: Slide Count Bounds, Gate 5: Duplicate Slide Analysis, Gate 16: Visual Grammar Alignment, Gate 17: Typography Scale, Gate 24: DOM Overflow).
   - High precision, visually and semantically grounded.
   - **Context Leakage**: Designed exclusively for 16:9 aspect ratio and slide cards.

2. **Master Quality Evaluation Engine**: ([app/quality/engine.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/quality/engine.py))
   - Generic evaluator for non-presentation formats across 6 dimensions (`StructuralEvaluator`, `SemanticEvaluator`, `PedagogicalEvaluator`, `DensityEvaluator`, `RedundancyEvaluator`, `FormatEvaluator`).
   - **Defects**: Evaluates text density using hardcoded character thresholds (`max_slide_chars = 3500` for A4). Does NOT check format-specific structural compliance (e.g. presence of exercise rubrics in Worksheets or citation formatting in KTI Documents).

---

## 13. Repair Loop Audit

### Presentation Repair Loop (Active)
```
QA Failure (PresentationQualityGate)
  ↓
DeterministicRepairEngine.repair()
  ↓ (Mutates SlidePlan: removes duplicate slides, reflows text, remaps layouts)
PipelineState.invalidate_after_repair("blueprint")
  ↓ (Invalidates downstream artifacts; bumps PDF version)
Re-generate Slides → Re-compose Document → Re-render PDF
  ↓
Re-evaluate PresentationQualityGate (Round N+1)
  ↓
RepairConvergenceAnalyzer.analyze_convergence()
  ↓
QualityDecisionEngine (EXPORT_APPROVED / BLOCKED)
```

### Non-Presentation Repair Loop (Inactive / Missing)
```
QA Evaluation (QualityEvaluationEngine)
  ↓
Calculate Quality Report Score
  ↓
Log findings to JobResult
  ↓
[NO REPAIR ACTION PERFORMED]
  ↓
Export Initial PDF (Even if Quality Score is POOR or CRITICAL)
```

### Stale Artifact & Export Risk Assessment
- **Presentation**: **LOW RISK**. Invalidation via `PipelineState.invalidate_after_repair()` guarantees that whenever `SlidePlan` is mutated, cached HTML/PDF versions are marked STALE and forced to re-render.
- **Handout, Worksheet, Scientific Document**: **HIGH RISK**. If `enable_refinement` is set to `True`, `IterativeRefinementController` mutates `SemanticMaterialBlueprint`, but `MasterRenderEngine` is NOT re-invoked in a verified loop, creating potential **STALE PDF** and **STALE METADATA** exports.

---

## 14. Rendering Architecture Audit

The rendering layer is clean, modular, and well-architected:
- **Jinja2 Template Engine**: [app/rendering/html/template_engine.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/rendering/html/template_engine.py) compiles HTML.
- **HTML Assembler**: [app/rendering/html/assembler.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/rendering/html/assembler.py) applies canonical format CSS rules (`@page { size: ... }`).
- **Playwright Chromium Exporter**: [app/rendering/playwright/pdf_exporter.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/rendering/playwright/pdf_exporter.py) produces pixel-exact print PDFs.
- **PyMuPDF Validator**: [app/rendering/validation/pdf_validator.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/rendering/validation/pdf_validator.py) verifies page geometry, dimensions, and visual integrity.

**Architectural Distinction**:
- **Shared Renderer**: Architectural **VALID** and recommended. HTML/CSS + Playwright can render any document format with precision.
- **Shared Artifact Intelligence**: Architectural **INVALID**. Forcing all formats to share presentation intelligence or generic 3-step blueprints destroys format-specific document structure.

---

## 15. Missing Abstractions

Before V5 implementation, the following abstractions must be created:

1. **Universal Knowledge Intelligence Core**: Artifact-neutral knowledge extractor that processes source documents into a pure `UniversalKnowledgeManifest` (core ideas, evidence, procedures, formulas, questions, arguments, claims) without slide or page count assumptions.
2. **Format Artifact Transformer Interface**: `IArtifactTransformer` interface with 4 dedicated implementations:
   - `PresentationArtifactTransformer` (16:9 Storyboard, Acts, Slide Cards)
   - `HandoutArtifactTransformer` (A4 Multi-column, Reading Flow, Deep Explanations)
   - `WorksheetArtifactTransformer` (A4 Exercise Scaffolding, Student Workspaces, Answer Keys)
   - `ScientificDocumentArtifactTransformer` (A4 IMRAD/KTI Formal Sections, Citations, Data Tables)
3. **Artifact-Specific Quality Gate Matrix**: Dedicated QA gates for Handout, Worksheet, and KTI Document.
4. **Universal Deterministic Repair Engine**: Modular repair framework capable of executing format-specific repair actions for all 4 output formats.

---

## 16. Architectural Risks

1. **Format Collapse Risk**: High risk of delivering Handouts, Worksheets, and KTI Documents that look like slide presentation printouts.
2. **Asymmetric Quality Risk**: Presentation output is strictly guarded by 25 quality gates and deterministic repair, while non-presentation output has no quality enforcement or export gating.
3. **Presentation Bias in Core Schema**: Core schemas (`ContentManifest`) containing presentation-specific attributes (`min_slides`) will break non-presentation planning if consumed directly.
4. **AI Latency & Cost Inflation**: Non-presentation pipeline calls LLM for full blueprint generation even when local deterministic parsing (`MarkdownTreeParser`) would be faster, cheaper, and 100% accurate.
5. **Stale PDF / Metadata Export Risk**: Non-presentation refinement lacks state-machine cache invalidation, creating potential divergence between returned metadata and rendered PDF.

---

## 17. Recommended Target Architecture

### Architecture Diagram: Current vs. Target

#### CURRENT ARCHITECTURE (Asymmetric & Collapsed)

```
                       SOURCE KNOWLEDGE (Markdown / Text)
                                       │
                    ┌──────────────────┴──────────────────┐
                    │ MaterialProductionPipeline.produce │
                    └──────────────────┬──────────────────┘
                                       │
                    Is Target Presentation 16:9?
                      /                         \
           YES       /                           \  NO (Handout, Worksheet, KTI)
                    ▼                             ▼
   ┌────────────────────────────────┐   ┌────────────────────────────────┐
   │ Dedicated 10-Stage Pipeline    │   │ Branch B (Generic Pipeline)    │
   │  - MarkdownTreeParser          │   │  - ContentIntelligenceAgent    │
   │  - RuleClassifier + AI         │   │    (LLM Call)                  │
   │  - ContentManifestBuilder      │   │  - MaterialBlueprintGenerator  │
   │  - SlideArchitect & Generator  │   │    (Fallback 3-step blueprint) │
   │  - 16:9 DocumentComposition    │   │  - CompositionBridge           │
   │  - MasterRenderEngine          │   │    (1 step = 1 A4 page)       │
   │  - PresentationQualityGate     │   │  - MasterRenderEngine          │
   │    (25 Gates)                  │   │  - QualityEvaluationEngine     │
   │  - DeterministicRepairEngine   │   │    (Passive text score, NO     │
   │    (Re-render & Re-QA Loop)    │   │     repair loop)               │
   └───────────────┬────────────────┘   └───────────────┬────────────────┘
                   │                                    │
                   ▼                                    ▼
       Presentation 16:9 PDF                    A4 PDF (FORMAT COLLAPSE:
       (High Quality, Repaired)                 Handout / Worksheet / KTI
                                                all look like slide cards)
```

#### TARGET ARCHITECTURE V5 (Universal Knowledge Core + 4 Specialized Engines)

```
                       SOURCE KNOWLEDGE (Markdown / Text)
                                       │
                                       ▼
                    UNIVERSAL KNOWLEDGE INTELLIGENCE CORE
         (MarkdownTreeParser + RuleClassifier + Selective AI Reasoning)
                                       │
                                       ▼
                           UNIVERSAL KNOWLEDGE MANIFEST
          (Artifact-Neutral: Concepts, Evidence, Formulas, Procedures,
                 Questions, Claims, Provenance & Importance Scores)
                                       │
       ┌───────────────────────┬───────┴───────────────┬───────────────────────┐
       │                       │                       │                       │
       ▼                       ▼                       ▼                       ▼
PRESENTATION 16:9      HANDOUT LENGKAP A4       WORKSHEET / LKS         SCIENTIFIC DOC (KTI)
TRANSFORMER            TRANSFORMER              TRANSFORMER             TRANSFORMER
(Storyboard, Acts,     (Reading Flow, Multi-    (Exercise Scaffolding,  (IMRAD/KTI Structure,
 Slide Cards)          column, Deep Content)    Workspaces, Keys)       Citations, Equations)
       │                       │                       │                       │
       ▼                       ▼                       ▼                       ▼
PRESENTATION 16:9      HANDOUT A4               WORKSHEET A4            KTI DOCUMENT A4
COMPOSITION            COMPOSITION              COMPOSITION             COMPOSITION
       │                       │                       │                       │
       └───────────────────────┼───────────────────────┼───────────────────────┘
                               │
                               ▼
                   MASTER RENDERING ENGINE
           (Jinja2 HTML + Playwright Chromium PDF Export)
                               │
                               ▼
              UNIVERSAL QUALITY & REPAIR ORCHESTRATOR
    (Format-Specific Quality Gates + Deterministic Repair & Re-QA Loop)
                               │
                               ▼
            AUTHORITATIVE EXPORT DECISION & ARTIFACT V2
```

---

## 18. Migration Strategy

To transition safely to V5 without breaking working features, execution must follow a strict 5-step order:

1. **Phase 1: Knowledge Extraction Decoupling**
   - Create `UniversalKnowledgeManifest` (artifact-neutral schema).
   - Refactor `ContentManifestBuilder` to output pure knowledge metadata without slide assumptions.
2. **Phase 2: Universal 10-Stage Pipeline Unification**
   - Refactor `MaterialProductionPipeline` so all 4 formats execute the full 10-stage pipeline.
   - Replace generic Branch B with universal stage execution.
3. **Phase 3: Format Artifact Transformers**
   - Implement `IArtifactTransformer` interface.
   - Build dedicated transformers for Handout A4, Worksheet LKS, and Scientific Document KTI.
4. **Phase 4: Format-Specific Quality Gate Expansion**
   - Implement `HandoutQualityGate`, `WorksheetQualityGate`, and `KTIQualityGate`.
5. **Phase 5: Universal Repair & Re-QA Loop**
   - Extend `DeterministicRepairEngine` to support non-presentation document reflow, workspace adjustment, and section re-ordering.

---

## 19. Files Likely To Change

- [app/orchestration/production_pipeline.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/orchestration/production_pipeline.py) (Unify pipeline branches)
- [app/intelligence/content_manifest.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/intelligence/content_manifest.py) (Extract `UniversalKnowledgeManifest`)
- [app/composition/bridge.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/composition/bridge.py) (Remove 1-step-to-1-page assumption for A4 documents)
- [app/quality/engine.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/quality/engine.py) (Integrate format-aware quality gates)
- [app/web/server.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/web/server.py) (Update SSE progress mapping for universal stages)
- [app/cli/shared.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/cli/shared.py) (Update CLI progress display)

---

## 20. Files That Must NOT Be Changed Yet

During Phase 0 and early Phase 1 migration, the following files MUST NOT be modified to preserve existing stable presentation functionality:

- [app/presentation/slide_architect.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/presentation/slide_architect.py)
- [app/presentation/slide_generator.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/presentation/slide_generator.py)
- [app/presentation/quality_gate.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/presentation/quality_gate.py)
- [app/presentation/repair_engine.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/presentation/repair_engine.py)
- [app/presentation/decision_engine.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/presentation/decision_engine.py)
- [app/rendering/playwright/pdf_exporter.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/rendering/playwright/pdf_exporter.py)
- [app/formats/registry.py](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/formats/registry.py)

---

## 21. Answers to Critical Audit Questions

1. **Apakah empat format saat ini benar-benar memiliki architecture berbeda?**
   *Tidak.* Hanya Presentation 16:9 yang memiliki arsitektur khusus (10-stage pipeline, `SlideArchitect`, 25 quality gates, `DeterministicRepairEngine`). Tiga format lainnya (Handout, Worksheet, KTI Document) digabung ke dalam Branch B generik yang menggunakan blueprint 3-step yang sama dan alokasi 1-step-to-1-page.

2. **Di titik mana source knowledge pertama kali berubah menjadi artifact-specific structure?**
   Untuk Presentation: pada Task 5 di `SlideArchitect.plan()`. Untuk non-presentation: pada `MaterialBlueprintGenerator.generate_from_analysis()`.

3. **Apakah titik tersebut terlalu terlambat?**
   *Ya.* Untuk non-presentation, transformasi langsung melompat dari teks LLM ke `PedagogicalBlueprint` tanpa melalui `ContentManifest` atau `ContentTree` structural parsing, sehingga kehilangan granularitas semantik.

4. **Apakah Presentation Intelligence saat ini bocor ke format lain?**
   *Ya.* Non-presentation fallback di `production_pipeline.py` secara langsung menggunakan ID kapabilitas presentation (`presentation.hero_statement`, `presentation.takeaway_summary`), dan `ContentManifest` menyimpan estimasi slide count.

5. **Apakah ada format yang sebenarnya hanya template variation?**
   *Ya.* Handout, Worksheet, dan Scientific Document saat ini hanya variasi nama parameter pada template CSS A4 portrait (`a4_portrait`) tanpa perbedaan arsitektur transformasi konten.

6. **Apakah Content Manifest sudah cukup artifact-neutral?**
   *Belum.* `ContentManifest` saat ini masih menyimpan atribut `min_slides`, `target_slides`, dan `max_slides`.

7. **Apakah Quality Gate saat ini terlalu presentation-centric?**
   *Ya.* Quality Gate utama (`PresentationQualityGate` dengan 25 gerbang) dirancang khusus untuk slide 16:9. Quality gate untuk non-presentation (`QualityEvaluationEngine`) bersifat sangat generik.

8. **Apakah Repair Engine benar-benar memperbaiki artifact?**
   Untuk Presentation: *Ya*, `DeterministicRepairEngine` mengubah `SlidePlan`, menghapus slide duplikat, serta memicu re-render dan re-QA. Untuk non-presentation: *Tidak*, tidak ada repair loop yang berjalan.

9. **Apakah setelah repair dilakukan re-render dan re-QA?**
   Untuk Presentation: *Ya*, dipicu oleh `PipelineState.invalidate_after_repair()`. Untuk non-presentation: *Tidak*.

10. **Apakah ada stale artifact/export risk?**
    Untuk Presentation: *Rendah*. Untuk non-presentation: *Tinggi*, jika refinement diaktifkan tanpa re-render loop.

11. **Stage mana yang benar-benar membutuhkan AI?**
    Hanya Stage 3 (Selective AI Reasoning untuk teks paragraf ambigu) dan Stage 5 (Instructional Storyboarding untuk materi non-standar).

12. **Stage mana yang seharusnya deterministic?**
    Stage 1 (Structural Parsing), Stage 2 (Local Classification), Stage 4 (Content Manifest), Stage 6 (Composition), Stage 7 (Rendering), Stage 8 (QA Validation), Stage 9 (Deterministic Repair).

13. **Apakah 10-stage pipeline merupakan real architecture atau hanya progress labels?**
    Untuk Presentation: *Real Architecture*. Untuk non-presentation: *Hanya progress labels UI* karena Branch B melompati sebagian besar stage tersebut.

14. **Apa 5 architectural changes paling penting sebelum V5 diimplementasikan?**
    - Abstraksi `UniversalKnowledgeManifest` (hapus slide bounds dari manifest).
    - Penyatuan 10-stage pipeline untuk semua format di `MaterialProductionPipeline`.
    - Pembuatan interface `IArtifactTransformer` dengan 4 transformer khusus per format.
    - Implementasi Quality Gate khusus per format (Handout, Worksheet, KTI).
    - Extensi `DeterministicRepairEngine` dan re-render loop untuk semua format.
