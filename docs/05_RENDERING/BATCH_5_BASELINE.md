# BATCH 5 BASELINE: HYBRID PDF REALIZATION ENGINE

## 1. Current Architecture
The current pipeline successfully converts raw content into structured `DocumentComposition` via:
`Raw Content` → `Intelligence` → `BlueprintProposal` → `VisualMapper` → `VisualBlueprint` → `DocumentComposer` → `DocumentComposition`

## 2. Existing Contracts
- `app.composition.schemas.DocumentComposition`: Contains exact physical page divisions, mapped regions (`HEADER`, `PRIMARY`), and semantic component families.
- **Rendering Boundary**: The current rendering boundary starts at `DocumentComposition`. The renderer must ONLY accept this object as input.

## 3. Existing Tests
- Baseline test suite (`pytest tests/ -v`) passes with 58/58 tests.
- Core logic from Batches 1–4 is robust and tested.

## 4. Dependencies
- HTML/CSS (Jinja2) for core layout.
- ReportLab for vector diagram assets (`reportlab.graphics`).
- Matplotlib for data charts.
- Playwright for final PDF generation via Chromium headless.

## 5. Renderer Input & Forbidden Coupling
- The renderer MUST NOT access raw content directly.
- The renderer MUST NOT call LLMs to determine CSS, pixel coordinates, or layout logic.
- Hardcoded design tokens must originate from the `app.design` token layer, not duplicated in CSS indiscriminately.

## 6. Compatibility Risks
- Transitioning from placeholder renderer scripts (`app/rendering/html_renderer.py` etc.) to the new hybrid directory structure. The existing `app/rendering/` files will be replaced/moved to the new structure.

## 7. Proposed Rendering Architecture
`DocumentComposition` → `HybridRenderPlanner` → `RenderPlan` → (HTML | ReportLab | Matplotlib) → `AssetRegistry` → `HTML Assembly` → `Playwright` → PDF.
