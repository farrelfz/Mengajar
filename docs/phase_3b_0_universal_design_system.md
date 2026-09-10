# PHASE 3B.0 — UNIVERSAL DESIGN SYSTEM & ASSET LIBRARY
## Universal Document Intelligence System V5
### Cross-Renderer Tokenization & Physical Component Foundation

---

## 1. Executive Summary & Architecture Overview

Phase 3B.0 establishes `app/design_system/` as the single canonical source of truth for visual and physical document primitives across all renderers (HTML/CSS, ReportLab vector, PyMuPDF physical inspector, and Pillow raster).

Prior to this phase, visual constants were severely fragmented:
- CSS variables in `document.html` were decoupled from Python constants.
- ReportLab rendered with hardcoded 2013 Flat UI palette colors (`#34495e`, `#3498db`), divergent from HTML's modern Slate palette.
- Physical PDF inspectors (`pdf_inspector.py`) hardcoded body font thresholds.
- Components risked collapsing into generic cards without explicit artifact compatibility.

Phase 3B.0 resolves these defects with an immutable, deterministic, 100% offline token and component subsystem.

---

## 2. 4-Tier Hierarchical Token Model

```
Level 1: RawToken
└── Physical constant (e.g. name="color.slate.900", value="#0f172a", category="color")

Level 2: SemanticToken
└── Functional abstraction referencing RawToken (e.g. name="color.text.primary", ref="color.slate.900")

Level 3: ArtifactToken
└── Format override (e.g. artifact="PRESENTATION", name="typography.presentation.title", value=28.0pt)

Level 4: RenderToken
└── Renderer-executable value with degradation tracking (e.g. ReportLab RGB float: (0.0588, 0.0902, 0.1647))
```

Every resolution produces an immutable `DesignResolutionTrace`, recording:
- `artifact_type`
- `renderer`
- `requested_token`
- `semantic_token`
- `artifact_token`
- `raw_token`
- `resolved_value`
- `fallback_applied`
- `degradation_recorded`

---

## 3. Four Format Profiles & Non-Collapsing Invariants

| Invariant | PRESENTATION | HANDOUT | WORKSHEET | SCIENTIFIC_DOCUMENT |
| :--- | :--- | :--- | :--- | :--- |
| **Canvas** | 16:9 Landscape (960pt x 540pt) | A4 Portrait (210mm x 297mm) | A4 Portrait (210mm x 297mm) | A4 Portrait (210mm x 297mm) |
| **Min Body Size** | **11.0 pt** | **8.5 pt** | **9.0 pt** | **8.0 pt** |
| **Min Heading Size** | **14.0 pt** | **12.0 pt** | **12.0 pt** | **12.0 pt** |
| **Font Family** | Inter (Sans) | Inter (Sans) | Inter (Sans) | Merriweather (Formal Serif) |
| **Anti-Spoiling** | Disabled | Disabled | **Strictly Required (True)** | Disabled |
| **Citation Required**| Disabled | Optional | Disabled | **Strictly Required (True)** |
| **Allowed Components**| HEADER, CARD, STAT_CALLOUT, TIMELINE, PROCESS, TABLE | HEADER, CALLOUT_BOX, EVIDENCE_CARD, PROCESS, TABLE | HEADER, **RESPONSE_WORKSPACE**, CALLOUT_BOX, CARD, TABLE | HEADER, **EVIDENCE_CARD**, FORMULA_BLOCK, TABLE |

---

## 4. Cross-Renderer Adapters

1. **`HtmlDesignAdapter`**:
   - Compiles tokens to `:root` CSS custom properties (`--ds-color-text-primary`).
   - Generates scoped canvas rules (`.document-canvas.artifact-presentation`).
2. **`ReportLabDesignAdapter`**:
   - Maps `ColorValue` to `reportlab.lib.colors.Color` and `HexColor`.
   - Generates `ParagraphStyle` adhering to profile font size floors.
   - Calculates `SimpleDocTemplate` page geometry and margins.
3. **`PyMuPdfDesignAdapter`**:
   - Supplies expected page rects and safe printable zones.
   - Provides dynamic minimum font floors (`floors["body"]`) to replace hardcoded values.
4. **`PillowDesignAdapter`**:
   - Converts point dimensions to pixel grids at 96 DPI (`1280px x 720px` for 16:9).
   - Generates integer `(r, g, b)` tuples.

---

## 5. Architectural Invariants Enforced

- **INV-DESIGN-001**: Centralized font definition in `FontRegistry`.
- **INV-DESIGN-002**: Canvas dimensions governed strictly by `CanvasSpec`.
- **INV-DESIGN-003**: WCAG 2.1 AA contrast checked by `ColorValidator`.
- **INV-DESIGN-004**: Fonts resolve with deterministic fallback in `FontRegistry`.
- **INV-DESIGN-005**: Critical assets resolve through `AssetRegistry`.
- **INV-DESIGN-006**: Font size floors validated by `TypographyValidator`.
- **INV-DESIGN-007**: Deterministic and 100% offline resolution.
- **INV-DESIGN-008**: Full provenance chain preserved in `DesignResolutionTrace`.
- **INV-DESIGN-009**: Degradation recorded when features unsupported in target renderer.
- **INV-DESIGN-010**: Whitelist component usage per artifact checked by `ComponentRegistry`.
- **INV-DESIGN-011**: Zero semantic text content in tokens.
- **INV-DESIGN-012**: `UnifiedQualityAuthority` remains the sole Level-0 export decision kernel via `DesignSystemQualityBridge`.

---

## 6. Verification & Test Metrics

- **Total Passing Tests**: 372 passed across all quality, repair, and design system suites.
- **Design System Test Coverage**: 31 dedicated tests in `tests/unit/design_system/` and `tests/integration/design_system/`.
