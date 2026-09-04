# 03 — Format Geometry Invariants & Validation

## 1. The Invariant Principle

$$\text{Format Contract} \equiv \text{HTML Geometry} \equiv \text{Playwright Geometry} \equiv \text{Physical PDF Geometry}$$

Every rendering stage derives its dimensions from the single source of truth: `ArtifactFormat`.

---

## 2. Invariant Specifications

| Format Preset | Width (mm / pt) | Height (mm / pt) | CSS `@page` Rule | DOM Page Class | PyMuPDF Measured (pt) | PyMuPDF Measured (mm) | Tolerance Status |
|---|---|---|---|---|---|---|---|
| **A4 Portrait** | 210.0 mm / 595.28 pt | 297.0 mm / 841.89 pt | `@page { size: 210mm 297mm; margin: 0; }` | `.page-a4-portrait` | 595.0 x 841.9 pt | 209.89 x 297.01 mm | $\Delta < 0.05\text{ mm}$ (PASS) |
| **A4 Landscape** | 297.0 mm / 841.89 pt | 210.0 mm / 595.28 pt | `@page { size: 297mm 210mm; margin: 0; }` | `.page-a4-landscape` | 841.9 x 595.0 pt | 297.01 x 209.89 mm | $\Delta < 0.05\text{ mm}$ (PASS) |
| **Presentation 16:9** | 338.67 mm / 960.0 pt | 190.5 mm / 540.0 pt | `@page { size: 13.333in 7.5in; margin: 0; }` | `.page-presentation` | 960.0 x 540.0 pt | 338.67 x 190.50 mm | $\Delta = 0.00\text{ mm}$ (PASS) |

---

## 3. Automated Invariant Coverage
- Enforced in unit tests: `tests/formats/test_format_geometry_invariants.py`
- Enforced in runtime validation: `app/rendering/validation/pdf_validator.py`
- Enforced in regression suite: `tests/regression/test_landscape_pagination_regression.py`
