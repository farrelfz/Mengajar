# 03 — Spatial Composition Audit & Capacity Analysis

## 1. Capacity & Geometry Analysis Across Formats

| Format ID | Physical Dimensions | Canvas Area (mm²) | Usable Area (approx mm² after margin/padding) | Composition Pages | Rendered PDF Pages | Root Cause of Divergence |
|---|---|---|---|---|---|---|
| `a4_portrait` | 210.0 × 297.0 mm | 62,370 mm² | ~50,400 mm² (16mm top/bottom, 18mm sides) | 4 | 4 | **Clean 1:1 Page Alignment** |
| `a4_landscape` | 297.0 × 210.0 mm | 62,370 mm² | ~50,400 mm² (12mm top/bottom, 18mm sides) | 4 | 8 | **CSS Class Precedence Conflict** |
| `presentation_16_9` | 338.67 × 190.5 mm | 64,516 mm² | ~54,800 mm² (0.4in top/bottom, 0.7in sides) | 4 | 4 | **Clean 1:1 Page Alignment** |

---

## 2. Root Cause of the A4 Landscape 8-Page Anomaly

During our forensic audit, we discovered the exact reason why `a4_landscape` produced 8 PDF pages for 4 composition steps:

### The Mechanism:
1. In `app/formats/presets.py`, `A4_LANDSCAPE` defined:
   ```python
   page_class = "page-a4 page-a4-landscape"
   ```
2. In `app/rendering/html/templates/document.html`:
   ```css
   /* Defined at line 47 */
   .page-a4-landscape {
       width: 297mm;
       min-height: 210mm;
       height: 210mm;
       padding: 12mm 18mm;
   }

   /* Defined at line 53 (LATER in stylesheet) */
   .page-a4 {
       width: 210mm;
       min-height: 297mm;
       height: 297mm;
       padding: 16mm 18mm;
   }
   ```
3. Because `.page-a4` appeared *after* `.page-a4-landscape` in the stylesheet, CSS cascade rules caused `.page-a4` to override the container height to `height: 297mm; min-height: 297mm;`.
4. However, the `@page` size for `A4_LANDSCAPE` was correctly set to `297mm 210mm` (height 210mm).
5. When Playwright/Chromium rendered each page `<div>` with height `297mm` onto a physical paper sheet of height `210mm`, the container was 87mm taller than the physical page. Chromium automatically generated a page break and pushed the remainder onto a second physical sheet.
6. Therefore: **4 composition pages × 2 sheets per page = 8 physical PDF pages.**

### Architectural Classification:
- **Classification:** `CSS / Template Specificity & Precedence Bug` in rendering realization.
- **Is Content Duplicated?** No. Content was simply broken across 2 sheets per step.
- **Did Composition Algorithm Diverge?** No, `DocumentComposition` had exactly 4 pages in all formats.

---

## 3. Composition Model: Current Reality vs Ideal Evolution

### Current Reality: Step-to-Page Allocation
- `CompositionBridge` currently operates on a **1 Pedagogical Step = 1 Page/Slide** allocation model.
- It iterates through `material.pedagogy.sequence` and assigns each step to one `PageComposition` with a `PRIMARY` region.
- This works cleanly for slide-style and step-by-step modular teaching materials, but does not yet implement multi-column multi-step flowing density for long narrative documents.

### Future Evolution Requirement:
- For dense handouts or narrative KTI reports, the composition layer should support packing multiple small steps into one physical page based on `density_estimate` and format capacity before triggering a new page.
