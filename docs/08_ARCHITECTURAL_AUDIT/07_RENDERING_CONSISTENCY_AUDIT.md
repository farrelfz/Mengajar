# 07 — Rendering Consistency & Dimension Flow Audit

## 1. Dimension Propagation Trace

```
ArtifactFormat (app/formats/)
  ├── css_page_size ("210mm 297mm", "297mm 210mm", "13.333in 7.5in")
  ├── page_class ("page-a4 page-a4-portrait", "page-presentation", etc.)
  ├── playwright_format ("A4", "16:9")
  ├── playwright_width / playwright_height ("13.333in", "7.5in")
  └── width_pt / height_pt (595.28 pt, 841.89 pt, 960.0 pt, 540.0 pt)
          │
          ├─────────────────────────────────────────┐
          ▼                                         ▼
   HTMLAssembler                             MasterRenderEngine
          │                                         │
          ▼                                         ▼
   document.html                             PlaywrightRenderer
   (@page size & page CSS)                   (page.pdf with format/dim)
          │                                         │
          └───────────────────┬─────────────────────┘
                              ▼
                        Physical PDF
                              │
                              ▼
                         PDFValidator
             (fitz rect.width/height vs ArtifactFormat)
```

---

## 2. Rendering Consistency Findings

1. **Single Source of Truth:** With Batch 7.8, all rendering layers consume the canonical `ArtifactFormat`.
2. **SVG ViewBox Resilience:** All vector diagram capabilities define a standardized `viewBox` (e.g. `viewBox="0 0 650 320"`) and use `width="100%" height="100%"`, allowing them to scale cleanly inside HTML flex containers.
3. **PyMuPDF Validation:** PDFValidator enforces exact bounding box checks with a ±4.0 pt tolerance for print precision.
4. **CSS Specificity Flaw in `document.html`:** Discovered during audit that `.page-a4` positioned after `.page-a4-landscape` overrides `height: 210mm` to `height: 297mm`, causing Chromium to split landscape pages into 2 sheets. This is identified as Risk #1 for remediation.
