# 02 — Production Truth Audit & Dead Pipeline Detection

## 1. End-to-End Execution Trace

We traced a realistic execution from raw Markdown text to a validated PDF artifact via `MaterialProductionPipeline.produce_artifact`:

```
Input: Raw topic / markdown on "Physics of Rotational Motion: Understanding Torque"
```

| Stage | Module & Function | Input Object | Output Object | Actually Consumed? | Production vs Test | Evidence |
|---|---|---|---|---|---|---|
| **1. Normalization** | `MarkdownNormalizer.normalize` | `raw_input: str` | `NormalizedDocument` | **YES** | Production | Strips CRLF, standardizes headings, isolates code blocks |
| **2. Segmentation** | `MarkdownSegmenter.segment` | `NormalizedDocument` | `list[ContentUnit]` | **YES** | Production | Extracts 7 atomic units with word counts & line indices |
| **3. Semantic Classification** | `SemanticClassifier.classify_all` | `list[ContentUnit]` | `list[ContentUnit]` (tagged) | **YES** | Production | Tags units with `ContentType` (CONCEPT, FACT, etc.) |
| **4. Visual Intent & Rel.** | `RelationshipExtractor`, `VisualIntentDetector` | `list[ContentUnit]` | `list[RelationshipEdge]`, `list[VisualIntent]` | **PARTIAL** | Production | Edges and intents attached to `ContentAnalysisResult` |
| **5. Material Blueprint Gen.** | `MaterialBlueprintGenerator.generate_from_analysis` | `ContentAnalysisResult` | `SemanticMaterialBlueprint` | **YES** | Production | Generates Levels A (Content), B (Pedagogy), C (Production) |
| **6. Capability Resolution** | `LibraryResolver.resolve` | `ProductionBlueprint`, `ContentBlueprint` | `dict[str, ResolutionResult]` | **YES** | Production | Resolves requirements to registered capabilities |
| **7. Format Resolution** | `resolve_format` (`app/formats`) | `target_format`, `target_artifact` | `ArtifactFormat` | **YES** | Production | Authoritative geometry, CSS rules, Playwright parameters |
| **8. Composition Bridge** | `CompositionBridge.compose_material` | `SemanticMaterialBlueprint`, `output_dir` | `DocumentComposition`, `list[AssetMetadata]` | **YES** | Production | Executes capability renderers, generates SVGs, builds pages |
| **9. HTML Assembly** | `HTMLAssembler.assemble` | `DocumentComposition`, `assets` | `document.html` (Path) | **YES** | Production | Renders Jinja2 template with canonical `@page` size |
| **10. PDF Export** | `PlaywrightRenderer.export_pdf` | `html_path`, `pdf_path`, `format_args` | `.pdf` file on disk | **YES** | Production | Headless Chromium prints exact vector PDF |
| **11. PDF Validation** | `PDFValidator.validate` | `pdf_path`, `expected_format` | `dict` (`valid=True`, metadata) | **YES** | Production | Validates page count, non-blank status, dimension bounds |

---

## 2. Dead Pipeline Detection (Create $\rightarrow$ Store $\rightarrow$ Consume)

| Subsystem / Field | Created / Stored | Consumed Downstream | Classification | Finding & Evidence |
|---|---|---|---|---|
| **Semantic Material Blueprint** | `material.content.concepts`, `worked_examples`, `misconceptions` | Used in `_infer_spec_params` to populate capability parameters | **GREEN** | Genuinely used to parameterize capabilities |
| **Pedagogical Sequence** | `material.pedagogy.sequence` | Used in `bridge.py` to allocate pages 1:1 | **GREEN** | Each step becomes a `PageComposition` |
| **Target Artifact & Format** | `material.production.target_format` | Resolves canonical `ArtifactFormat` for CSS/Playwright/Validation | **GREEN** | Fully active across rendering and validation |
| **Relationship Edges** | `analysis.relationships` | Stored in `ContentAnalysisResult` | **YELLOW** | Extracted by AI intelligence, but `MaterialBlueprintGenerator` currently uses heuristic rules rather than graph traversal |
| **Importance Scores** | `analysis.units[*].importance_score` | Calculated in intelligence stage | **YELLOW** | Calculated, but not yet used to prune or paginate content in composition |
| **Legacy `DocumentMode`** | `composition.mode` | Maintained on `DocumentComposition` | **GREEN (Compatible)** | Kept synchronized with `ArtifactFormat.legacy_document_mode` for backwards compatibility |
| **Composition Density Engine** | `app/design/density.py` | Standalone module with tests | **YELLOW** | Evaluates density tokens, but `CompositionBridge` currently operates on 1-step-per-page rather than dynamic multi-component packing |
| **Quality Critic Model** | `QualityCritic` (`app/agents/quality_critic.py`) | Evaluates blueprint quality in tests | **YELLOW** | Works in unit tests, but not yet wired as an automatic feedback loop in `MaterialProductionPipeline` |

---

## 3. Verdict on Pipeline Integration
The pipeline is **genuinely integrated from Raw Input to PDF** through `MaterialProductionPipeline`. It is NOT merely benchmark glue. However, certain advanced intelligence layers (Importance-based pruning, graph relationship traversal, critic feedback loop) are currently **declarative or partial** rather than driving dynamic page composition.
