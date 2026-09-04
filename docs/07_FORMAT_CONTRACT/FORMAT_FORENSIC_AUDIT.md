# Forensic Format Audit — Batch 7.8

## 1. Executive Summary
This forensic audit maps all existing representations, assumptions, and couplings regarding artifact identity, pedagogical mode, and physical page formats across the codebase prior to the architectural hardening in Batch 7.8.

---

## 2. Answers to Explicit Audit Questions

### 1. Where is physical page format currently determined?
Currently, physical page format is inferred at multiple scattered locations:
- **`app/composition/bridge.py` (`compose_material`)**: Maps `TargetArtifactType` directly to `DocumentMode` (`PRESENTATION_16_9`, `A4_LANDSCAPE`, or `A4_PORTRAIT`).
- **`app/rendering/html/assembler.py` (`assemble`)**: Inspects `composition.mode` to select hardcoded CSS `@page` strings (`"13.333in 7.5in"`, `"297mm 210mm"`, or `"210mm 297mm"`) and CSS class names (`page-presentation`, `page-a4 page-a4-landscape`, `page-a4 page-a4-portrait`).
- **`app/rendering/engine.py` (`render`)**: Inspects `composition.mode` to infer `is_landscape` boolean and `fmt` string (`"16:9"` vs `"A4"`).
- **`app/rendering/playwright/pdf_exporter.py` (`export_pdf`)**: Accepts `is_landscape`, `format`, `width`, `height`, and falls back to `"13.333in" x "7.5in"` when `format == "16:9"`.

### 2. Is page size inferred from semantic artifact type?
**Yes.** In `app/composition/bridge.py`, `TargetArtifactType.TEACHING_PRESENTATION` and `RESEARCH_PRESENTATION` force `DocumentMode.PRESENTATION_16_9`, while `SCIENTIFIC_POSTER` forces `A4_LANDSCAPE`, and all others force `A4_PORTRAIT`. There is no mechanism in `SemanticMaterialBlueprint` or `MaterialProductionPipeline` to request a different physical canvas for the same semantic artifact.

### 3. Is orientation inferred from DocumentMode?
**Yes.** `DocumentMode` combines both document type and orientation in its enum values:
- `A4_PORTRAIT` -> portrait
- `A4_LANDSCAPE` -> landscape
- `A4_TUTORIAL` -> landscape
- `PRESENTATION_16_9` -> landscape / presentation

### 4. Are there duplicated page-size constants?
**Yes:**
- In `app/rendering/html/templates/document.html`:
  - `.page-presentation`: `13.333in x 7.5in`
  - `.page-a4-portrait`: `210mm x 297mm`
  - `.page-a4-landscape`: `297mm x 210mm`
  - `.page-a4`: `210mm x 297mm`
- In `app/rendering/html/assembler.py`:
  - `page_size_css = "13.333in 7.5in"` / `"297mm 210mm"` / `"210mm 297mm"`
- In `app/rendering/playwright/pdf_exporter.py`:
  - `width or "13.333in"`, `height or "7.5in"`
- In `app/formats/`:
  - `max_words_per_page` defined in `a4_portrait.py` (550), `a4_landscape.py` (400), `presentation_16_9.py` (120), but dimensions in mm/pt/in are absent from `app/formats/schemas.py`.

### 5. Does CSS have independent format assumptions?
**Yes.** `document.html` defines specific CSS classes with hardcoded pixel/millimeter dimensions (`.page-presentation`, `.page-a4-portrait`, `.page-a4-landscape`).

### 6. Does Playwright have independent format assumptions?
**Yes.** `PlaywrightRenderer` has its own branch for `"16:9"` with hardcoded `"13.333in"` and `"7.5in"`. While `prefer_css_page_size=True` is enabled, Playwright takes `format="A4"` and `landscape=is_landscape`.

### 7. Does composition know about physical dimensions?
**Partially/Implicitly.** `DocumentComposition` contains `mode: DocumentMode`, but does not store an explicit `ArtifactFormat` object, physical width, height, unit, or orientation.

### 8. Can the same semantic artifact theoretically render into multiple physical formats today?
**No.** Passing `target_artifact=TargetArtifactType.TEACHING_PRESENTATION` will always produce `PRESENTATION_16_9`. Passing `target_artifact=TargetArtifactType.DETAILED_HANDOUT` will always produce `A4_PORTRAIT`. There is no way to ask for an A4 Landscape Handout or an A4 Portrait Presentation without altering the pipeline code.

### 9. Which existing assumptions must remain for backward compatibility?
- Default format mappings:
  - `TEACHING_PRESENTATION` -> default `presentation_16_9`
  - `RESEARCH_PRESENTATION` -> default `presentation_16_9`
  - `DETAILED_HANDOUT` -> default `a4_portrait`
  - `SCIENTIFIC_POSTER` -> default `a4_landscape`
  - `KTI_DOCUMENT` -> default `a4_portrait`
  - `STUDENT_WORKSHEET` -> default `a4_portrait`
  - `ONE_PAGE_SUMMARY` -> default `a4_portrait`
- Legacy `DocumentMode` enum values (`A4_PORTRAIT`, `A4_LANDSCAPE`, `A4_TUTORIAL`, `PRESENTATION_16_9`) must remain valid so existing tests and compositions do not break.
- Existing `FormatConfig` constraints in `app/formats/` must remain accessible.

### 10. Which format inconsistencies are intentional legacy artifacts vs actual coupling?
- **Intentional Legacy:** `DocumentMode.A4_TUTORIAL` mapping to A4 Landscape for KTI editorial report style.
- **Architectural Coupling:** Inability for a caller to supply an explicit physical format (e.g. `target_format="a4_portrait"` or `ArtifactFormat`) to `produce_artifact` or `SemanticMaterialBlueprint`.

---

## 3. Coupling Map Diagram

```
BEFORE:
MaterialProductionPipeline(target_artifact=DETAILED_HANDOUT)
   ↓
CompositionBridge: hardcoded if target_artifact == HANDOUT -> DocumentMode.A4_PORTRAIT
   ↓
DocumentComposition(mode=DocumentMode.A4_PORTRAIT)
   ↓
HTMLAssembler: if mode == A4_PORTRAIT -> CSS "210mm 297mm"
MasterRenderEngine: if mode in (LANDSCAPE, TUTORIAL) -> landscape=True else False
PlaywrightRenderer: format="A4", landscape=False
   ↓
Physical PDF
```

```
AFTER (BATCH 7.8 TARGET):
MaterialProductionRequest / Pipeline(
   target_artifact=DETAILED_HANDOUT,
   target_format="a4_landscape" | "a4_portrait" | "presentation_16_9" | None
)
   ↓
Format Resolution Layer (resolve_format):
   Explicit target_format > Artifact Default > Fallback
   ↓
ArtifactFormat (Single Source of Truth: geometry, CSS @page, Playwright args, validator bounds)
   ↓
CompositionBridge (receives ArtifactFormat, sets layout constraints)
   ↓
DocumentComposition (stores resolved ArtifactFormat metadata / ID)
   ↓
HTMLAssembler & MasterRenderEngine (consume ArtifactFormat directly)
   ↓
PlaywrightRenderer & PDFValidator (exact match with ArtifactFormat)
```
