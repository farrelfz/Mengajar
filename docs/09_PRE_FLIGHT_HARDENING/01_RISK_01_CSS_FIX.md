# 01 — RISK-01: Forensic CSS Investigation & Hardening

## 1. Forensic Confirmation

### Cascade Inspection
Before modifying code, we inspected `app/rendering/html/templates/document.html` and `app/formats/presets.py`:
- In `document.html`:
  ```css
  .page-a4-landscape {
      width: 297mm;
      min-height: 210mm;
      height: 210mm;
      padding: 12mm 18mm;
  }
  .page-a4 {
      width: 210mm;
      min-height: 297mm;
      height: 297mm;
      padding: 16mm 18mm;
  }
  ```
- In `presets.py`:
  - `A4_LANDSCAPE.page_class` was defined as `"page-a4 page-a4-landscape"`.
- Because `.page-a4` appeared *after* `.page-a4-landscape` in `document.html` and had equal class selector specificity (`.page-a4` vs `.page-a4-landscape`), the CSS cascade applied `height: 297mm` and `width: 210mm` to the landscape page container div!
- When Chromium rendered a 297mm-tall DOM element on a 210mm-tall landscape PDF page canvas (`@page { size: 297mm 210mm; }`), it triggered an automatic physical page break, splitting each landscape step across 2 sheets.

---

## 2. The Clean Structural Fix

Rather than using fragile `!important` hacks, we enforced format-specific ownership:
1. **Eliminated Generic `.page-a4`:** Removed the conflicting `.page-a4` dimension definition from `document.html`.
2. **Dedicated Clean Classes:**
   - `.page-a4-portrait`: `width: 210mm; height: 297mm; min-height: 297mm;`
   - `.page-a4-landscape`: `width: 297mm; height: 210mm; min-height: 210mm;`
   - `.page-presentation`: `width: 13.333in; height: 7.5in; min-height: 7.5in;`
3. **Format Contract Presets Updated:**
   - `A4_PORTRAIT.page_class = "page-a4-portrait"`
   - `A4_LANDSCAPE.page_class = "page-a4-landscape"`

---

## 3. Physical Verification Result
- **Before Fix:** 4 steps $\rightarrow$ **8 physical pages**
- **After Fix:** 4 steps $\rightarrow$ **4 physical pages** (1:1 perfect step-to-page alignment)
- **Geometry Tolerance:** PyMuPDF measured `841.9 x 595.0 pt` (297.0 x 209.9 mm), which matches ISO A4 landscape dimensions with 0.01mm tolerance.
