# PHASE 3A — FORENSIC ARCHITECTURE AUDIT
## UNIVERSAL DOCUMENT INTELLIGENCE SYSTEM V5
### RENDERED-OUTPUT QUALITY INTELLIGENCE & INDEPENDENT INSPECTION LAYER

---

## 1. EXECUTIVE SUMMARY

Phase 3A introduces an independent, adversarial, rendered-output quality intelligence layer for all four artifact types:
1. **PRESENTATION** (16:9 Slide Deck)
2. **HANDOUT** (A4 Reading Material)
3. **WORKSHEET** (LKS / Student Inquiry Activity)
4. **SCIENTIFIC DOCUMENT** (KTI / Research Report)

Before implementing the new inspection subsystem under `app/quality/rendered/`, this forensic audit maps the existing codebase across 12 required areas to prevent code duplication, identify reusable components, assess conflict risks, and define a clear integration strategy.

---

## 2. COMPREHENSIVE COMPONENT MAPPING (12 AUDIT AREAS)

| # | Audit Area | Existing Component | File Location | Responsibility | Reusable? | Conflict Risk | Proposed Integration Strategy |
|---|---|---|---|---|---|---|---|
| **1** | **Render Pipeline** | `MasterRenderEngine` | `app/rendering/engine.py` | Orchestrates hybrid asset rendering, HTML assembly, format resolution, and PDF export. | **Yes (Indirectly)** | Low | Keep untouched. Evaluator consumes its output paths (`.html`, `.pdf`). |
| | | `RendererExecutor` family | `app/integration/render_execution/` | Bridges legacy models (`PresentationDeck`, `HandoutContent`, etc.) to `DocumentComposition` and calls `MasterRenderEngine`. | **Yes** | Low | Executors provide canonical inputs for rendered inspection. No renderer modifications. |
| **2** | **PDF Generation Locations** | `PlaywrightRenderer` | `app/rendering/playwright/pdf_exporter.py` | Headless Chromium PDF export via async Playwright (`page.pdf`). | **Yes** | Low | Source of truth for physical PDF output. Preserved without changes. |
| | | `PDFScreenshotExporter` | `app/rendering/validation/screenshot_exporter.py` | PyMuPDF page rasterization to PNG with basic blank-page detection. | **Yes (Reference)** | Low | Reusable concepts for raster analysis; build enhanced raster inspector in Phase 3A. |
| **3** | **Playwright Usage** | `PlaywrightRenderer.export_pdf` | `app/rendering/playwright/pdf_exporter.py` | Converts HTML to PDF with CSS page-size and viewport margins. | **Yes** | Low | Playwright remains the PDF generator; Phase 3A evaluator inspects the resulting PDF via PyMuPDF/Pillow. |
| **4** | **PyMuPDF Usage** | `PDFValidator` | `app/rendering/validation/pdf_validator.py` | Validates page count, rect dimensions vs `ArtifactFormat`. | **Yes (Utility)** | Low | Reusable for basic physical dimension checks. Phase 3A builds deep geometry inspector. |
| | | `PyMuPDFVisualInspector` | `app/presentation/visual_qa.py` | Presentation-only inspector for text clipping, span sizes, quadrant occupancy. | **Partial (Extract logic)** | Medium (Tied to presentation) | Generalize core geometry algorithms into universal PDF inspector for all 4 artifact formats. |
| **5** | **Existing Visual QA Modules** | `app/presentation/visual_qa.py` | `app/presentation/visual_qa.py` | Presentation-specific DOM & PyMuPDF visual inspection. | **Partial** | Medium | Presentation-specific; Phase 3A creates independent `app/quality/rendered/` architecture. |
| | | `MasterQualityScoringEngine` | `app/quality/calibration/quality_scoring.py` | Phase 2C pre-render / model-level quality evaluation across 4 artifacts. | **Yes (Complementary)** | Low | Phase 2C evaluated model quality. Phase 3A evaluates *rendered output*. They remain orthogonal. |
| **6** | **Presentation Quality Gates** | `PresentationQualityGate` | `app/presentation/quality_gate.py` | Filters presentation issues into blocking vs warnings. | **No (Keep in presentation)** | Low | Phase 3A creates universal quality gates across all 4 formats. |
| | | `CalibratedDecisionEngine` | `app/quality/calibration/decision_engine.py` | Phase 2C decision arbitration (Fidelity vs Quality). | **Yes (Complementary)** | Low | Can consume Phase 3A rendered inspection decisions or integrate into master gate. |
| **7** | **Existing Fidelity Validators** | `UnifiedFidelityValidator` | `app/quality/artifact_fidelity/` | Measures pipeline fidelity (semantic, structural, traceability preservation). | **Yes (Complementary)** | Low | Strictly preserved. Fidelity $\neq$ Quality. Phase 3A inspects rendered quality independently. |
| **8** | **Contact Sheet Generation** | `ContactSheetGenerator` | `app/presentation/contact_sheet.py` | Generates 4-column thumbnail grid from PDF pages using PyMuPDF and Pillow. | **Yes** | Low | Direct reuse for base contact sheets; augment with diagnostic overlays/markers in Phase 3A. |
| **9** | **Existing Quality Reporting** | `ArtifactQualityReport`, `QualitySignalExplanation` | `app/quality/contracts/` | Phase 2C typed reports for model quality. | **Yes (Pattern reference)** | Low | Phase 3A establishes `RenderedArtifactInspection` and `RenderedQualityReport` contracts. |
| **10**| **Existing Failure Taxonomy** | `FailureCategory`, `FailureSeverity`, `QualityFailure` | `app/quality/calibration/failure_taxonomy.py` | Phase 2C failure categorization and severity enums. | **Yes** | Low | Reuse `FailureSeverity` (`CRITICAL`, `WARNING`, `INFO`) and extend with rendered failure codes. |
| **11**| **Existing Artifact Contracts** | `RenderArtifact`, `RenderUnit`, `RenderSection` | `app/integration/artifact_bridge/contracts.py` | Authoritative blueprint bridge contracts. | **Yes** | Low | Read-only input for context and traceability correlation. Evaluator remains independent. |
| **12**| **Existing Integration Tests** | `test_controlled_renderer_execution.py` | `tests/integration/` | 25 tests verifying Phase 2B render execution. | **Yes** | Low | Must remain 100% green. Zero regression requirement. |
| | | `test_cross_fixture_quality_benchmark.py` | `tests/integration/` | 36 tests verifying Phase 2C 28-artifact execution. | **Yes** | Low | Must remain 100% green. Phase 3A runs downstream on rendered artifacts. |

---

## 3. ARCHITECTURAL GAP ANALYSIS

### Why Existing Modules Are Insufficient for Rendered Inspection
1. **Model vs Physical Output Gap**:
   - Phase 2C evaluated Python data structures (`PresentationDeck`, `HandoutContent`, `WorksheetDocument`, `KtiDocument`).
   - It did NOT inspect what headless Chromium actually painted into PDF vectors and raster pixels.
   - Text wrapping, font substitution, table fracturing across page boundaries, CSS flex/grid overflow, and margin collisions only exist in the rendered PDF.
2. **Presentation-Centric Bias in Legacy Visual QA**:
   - `app/presentation/visual_qa.py` is hardcoded to 16:9 presentations and `GeneratedSlide` classes.
   - Handout, Worksheet, and Scientific Document currently have ZERO post-render visual/geometry inspection.
3. **Workspace Inversion in Worksheets**:
   - Existing tools treat empty space as "accidental void" or "density imbalance".
   - In a worksheet, empty space inside a border is deliberate student response workspace.
4. **Evidence-Proximity in Scientific Documents**:
   - A scientific table or chart may exist in the data model, but in the rendered PDF it might be separated from its explanatory text by three pages.

---

## 4. PROPOSED PHASE 3A ARCHITECTURE & COMPONENT BOUNDARIES

### Dedicated Package: `app/quality/rendered/`

```
app/quality/rendered/
├── __init__.py
├── contracts.py                  # Universal RenderedArtifactInspection & report contracts
├── failure_taxonomy.py           # Rendered failure codes, severities, future repair tags
├── pdf_inspector.py              # PyMuPDF-based text clipping, overflow, font geometry
├── raster_inspector.py           # Pillow-based edge density, blank regions, visual balance
├── composition_fingerprint.py    # 4-quadrant spatial occupancy & layout streak detector
├── whitespace_model.py           # Context-Aware WhitespaceIntentModel (worksheet vs presentation)
├── typography_density.py         # Typographic scale ratios & content density analysis
├── presentation_quality.py       # PresentationRenderedQualityEvaluator (16:9 slides)
├── handout_quality.py            # HandoutRenderedQualityEvaluator (A4 continuous reading)
├── worksheet_quality.py          # WorksheetRenderedQualityEvaluator (Inquiry & student workspace)
├── scientific_quality.py         # ScientificRenderedQualityEvaluator (BAB hierarchy & evidence proximity)
├── quality_engine.py             # MasterRenderedQualityEngine (unified entry point)
└── quality_reporter.py           # JSON and Markdown diagnostic report generators
```

### Clean Boundary Invariants
1. **Independence**: Evaluators take `(pdf_path: Path, html_path: Path | None, artifact_type: str, metadata: dict | None)`. They never trust renderer self-reported success flags.
2. **Zero Renderer Modification**: Zero changes to CSS templates, HTML assemblers, or renderer executors.
3. **Zero AI / Zero LLM**: Strictly deterministic algorithms using `pymupdf` (`fitz`), Pillow (`PIL`), and statistical analysis.
4. **Dimensional Transparency**: Overall score never hides dimensional failures; CRITICAL failures immediately force `QualityDecisionStatus.BLOCKED`.

---

## 5. AUDIT CONCLUSION & SIGN-OFF

The repository has robust PDF generation (`PlaywrightRenderer`), fast PDF parsing (`pymupdf`), and established benchmark corpora (`tests/fixtures/benchmark/`). The new Phase 3A layer will cleanly sit downstream of the render pipeline, inspecting actual rendered PDFs and images without touching legacy rendering code.

**Audit Status**: **APPROVED FOR IMPLEMENTATION**.
