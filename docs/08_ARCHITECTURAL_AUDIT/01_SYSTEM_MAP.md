# 01 — System Architecture Map (Actual Production Reality)

## 1. Concrete System Topology

```
┌────────────────────────────────────────────────────────────────────────┐
│ 1. INPUT & CONTENT INGESTION LAYER                                    │
│ - Raw Input: Markdown text, plain text, or topic string                │
│ - Module: ContentIntelligenceAgent (app/agents/content_intelligence_agent.py) │
│ - Subcomponents:                                                       │
│   * MarkdownNormalizer (app/intelligence/normalizer.py)                │
│   * MarkdownSegmenter (app/intelligence/segmenter.py)                  │
│   * SemanticClassifier (app/intelligence/classifier.py)                │
│   * RelationshipExtractor (app/intelligence/visual_intent_detector.py) │
│ - Output: ContentAnalysisResult (app/intelligence/schemas.py)          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 2. BLUEPRINT GENERATION LAYER (Level A, B, C)                         │
│ - Module: MaterialBlueprintGenerator (app/intelligence/material_blueprint_generator.py) │
│ - Output: SemanticMaterialBlueprint (app/blueprints/contracts.py)      │
│   * Level A: ContentBlueprint (concepts, facts, worked_examples, etc.) │
│   * Level B: PedagogicalBlueprint (sequence of narrative steps)        │
│   * Level C: ProductionBlueprint (TargetArtifactType, target_format, requirements) │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 3. CAPABILITY RESOLUTION & DISCOVERY LAYER                            │
│ - Modules:                                                             │
│   * CapabilityRegistry (app/capabilities/registry.py)                  │
│   * LibraryResolver (app/capabilities/resolver.py)                     │
│   * Libraries: Pedagogy, Research Education, Physics, Mathematics     │
│ - Resolution Output: dict[step_id, ResolutionResult]                   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 4. PHYSICAL FORMAT RESOLUTION LAYER (Batch 7.8)                       │
│ - Modules:                                                             │
│   * ArtifactFormat & Presets (app/formats/contracts.py, presets.py)    │
│   * FormatRegistry & Resolver (app/formats/registry.py, resolution.py) │
│ - Authoritative Formats: a4_portrait, a4_landscape, presentation_16_9 │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 5. COMPOSITION BRIDGE LAYER                                           │
│ - Module: CompositionBridge (app/composition/bridge.py)                │
│ - Actions:                                                             │
│   * Executes capability renderers (SVG / HTML generation)              │
│   * Constructs PageComposition & PageRegion objects                    │
│   * Attaches format_id, format metadata, rendered HTML / SVGs          │
│ - Output: DocumentComposition (app/composition/schemas.py)             │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 6. HYBRID RENDERING ENGINE LAYER                                      │
│ - Modules:                                                             │
│   * MasterRenderEngine (app/rendering/engine.py)                       │
│   * HTMLAssembler (app/rendering/html/assembler.py)                    │
│   * Jinja2 Template: document.html                                     │
│   * PlaywrightRenderer (app/rendering/playwright/pdf_exporter.py)      │
│ - Output: Physical .pdf and .html files (contextual slug + final.pdf)  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 7. QUALITY VALIDATION LAYER                                           │
│ - Module: PDFValidator (app/rendering/validation/pdf_validator.py)     │
│ - Uses PyMuPDF (fitz) to verify:                                      │
│   * Page count > 0                                                     │
│   * Non-blank first page                                               │
│   * Physical width/height bounds vs expected ArtifactFormat contract  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Directory Reference

| Layer | Primary Location | Key Entrypoint |
|---|---|---|
| Ingestion & Intel | `app/intelligence/`, `app/agents/` | `ContentIntelligenceAgent.execute` |
| Blueprints | `app/blueprints/` | `MaterialBlueprintGenerator.generate_from_analysis` |
| Capabilities | `app/capabilities/`, `app/libraries/` | `LibraryResolver.resolve` |
| Formats | `app/formats/` | `resolve_format`, `FormatRegistry.get` |
| Composition | `app/composition/` | `CompositionBridge.compose_material` |
| Rendering | `app/rendering/` | `MasterRenderEngine.render` |
| Validation | `app/rendering/validation/` | `PDFValidator.validate` |
| Orchestration | `app/orchestration/` | `MaterialProductionPipeline.produce_artifact` |
