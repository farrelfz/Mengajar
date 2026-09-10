# PHASE 3B.0 — UNIVERSAL DESIGN SYSTEM & ASSET LIBRARY FORENSIC AUDIT
## Universal Document Intelligence System V5
### Forensic Investigation Before Design System Implementation

---

## 1. Executive Summary & Audit Purpose

This forensic audit establishes the architectural and empirical baseline for **Phase 3B.0: Universal Design System & Asset Library**.
The system currently transforms structured source knowledge into four distinct artifact types:
1. **PRESENTATION** (16:9 visual slides, distance legibility, low-medium density)
2. **HANDOUT** (A4 continuous educational reading, monotonic hierarchy, print comfort)
3. **WORKSHEET** (A4 inquiry-based student activity sheet, interactive response spaces, anti-spoiling)
4. **SCIENTIFIC_DOCUMENT** (A4 formal Indonesian KTI, Bab I–V structure, claim-evidence rigor)

While semantic intelligence (Phases 1A–1D) and quality authority (Phases 2B, 2C, 3A, 3A.1, 3B) are strictly decoupled, **rendering and visual primitives remain severely fragmented**. Visual constants (colors, fonts, margins, spacing, and page dimensions) are scattered across HTML templates, CSS style blocks, Python ReportLab renderers, PyMuPDF inspectors, and quality threshold dictionaries.

---

## 2. Forensic Audit of Existing Visual Primitives

### 1. Existing Font Declarations
- **HTML Templates** (`app/rendering/html/templates/document.html:18`):
  ```css
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  ```
- **ReportLab Vector Engine** (`app/rendering/reportlab/renderer.py`):
  Uses default ReportLab Helvetica without explicit font loading or TTF registration.
- **PyMuPDF Quality Inspector** (`app/quality/rendered/pdf_inspector.py:58-63`):
  Hardcoded body font thresholds:
  - `PRESENTATION`: 11.0 pt
  - `HANDOUT`: 8.5 pt
  - `WORKSHEET`: 9.0 pt
  - `SCIENTIFIC_DOCUMENT`: 8.0 pt
- **Finding**: There is no central `FontRegistry` mapping font names, font weights, TTF files, HTML font stacks, and ReportLab postscript names.

### 2. Existing CSS Variables & Token Mappings
- **Early Prototype Tokens** (`app/design/tokens.py`):
  Maps `TypographyScale` and `SpacingScale` to CSS variables:
  `var(--text-display)`, `var(--text-title)`, `var(--spacing-md)`.
- **CSS Templates** (`document.html`):
  Rarely consumes these CSS variables; instead uses hardcoded CSS pixel and point values (`11pt`, `10pt`, `14px`, `18px`, `24px`).
- **Finding**: The token system lacks a multi-tier hierarchy (Raw -> Semantic -> Artifact -> Render). Renderers consume arbitrary literals instead of semantic tokens.

### 3. Hardcoded Color Values
- **HTML / CSS** (`document.html`):
  - Primary text: `#0f172a` (Slate 900)
  - Secondary/Muted: `#94a3b8` (Slate 400)
  - Borders: `#e2e8f0` (Slate 200)
  - Accent / Category: `#2563eb` (Blue 600)
  - Background: `#ffffff`, `#f8fafc` (Slate 50)
- **ReportLab Renderer** (`app/rendering/reportlab/renderer.py:19-28`):
  - Line stroke: `#34495e` (Wet Asphalt)
  - Phase 1 accent: `#3498db` (Peter River)
  - Phase 2 accent: `#e74c3c` (Alizarin)
  - Phase 3 accent: `#2ecc71` (Emerald)
  - Background fill: `#ecf0f1`, Border: `#bdc3c7`
- **Finding**: Severe visual drift between HTML output (modern Slate palette) and ReportLab vector output (Flat UI 2013 palette). Neither derives from a shared semantic palette.

### 4. Page Geometry & Canvas Definitions
- **Presentation 16:9**:
  - `document.html:37-41`: `width: 13.333in; min-height: 7.5in; padding: 0.4in 0.7in;` (corresponds to 1280px x 720px at 96 DPI, or 960pt x 540pt).
- **A4 Portrait**:
  - `document.html:42-47`: `width: 210mm; min-height: 297mm; padding: 16mm 18mm;` (595.28pt x 841.89pt, padding 45.35pt 51.02pt).
- **A4 Landscape**:
  - `document.html:48-53`: `width: 297mm; min-height: 210mm; padding: 12mm 18mm;`.
- **Finding**: Geometry dimensions are specified in mixed physical units (`in`, `mm`, `pt`, `px`) without standard bidirectional conversion functions.

### 5. Existing Asset Directories & Resolution
- Directories present: `assets/fonts/`, `assets/icons/`, `assets/diagrams/`, `assets/images/`, `assets/generated/`.
- All directories currently contain zero files or metadata.
- Asset paths in renderers are generated via raw string manipulation:
  `self.asset_manager.generate_asset_path(block_id, "svg")`.
- **Finding**: No `AssetRegistry` with asset type, dimensions, format, license metadata, allowed artifact types, and graceful missing-asset fallback.

### 6. Component Abstractions & Invariants
- `app/design/schemas.py` contains `ComponentFamily` enum (CARD, TIMELINE_ITEM, STAT_CALLOUT, PROCESS_STEP, COMPARISON_COLUMN, etc.), but:
  - No `ComponentSpec` defining slot schema (required/optional slots).
  - No declared artifact compatibility (e.g. `ResponseWorkspace` must be allowed on Worksheet only).
  - No minimum readable size or token constraints.
- **Finding**: High risk of the "everything becomes a generic card" anti-pattern without explicit component diversity rules.

---

## 3. Identification of Architectural Deficiencies

| Defect Area | Current Implementation | Architectural Risk | Required Phase 3B.0 Solution |
| :--- | :--- | :--- | :--- |
| **Token Hierarchy** | Flat CSS string mappings in `app/design/tokens.py` | Renderers directly use hex/px literals | 4-tier token model: Raw -> Semantic -> Artifact -> Render |
| **Cross-Renderer Font Parity** | System fonts in HTML, Helvetica in ReportLab | Visual drift; missing font crashes in PDF | `FontRegistry` with cross-renderer font mapping and fallback |
| **Unit Conversions** | Scattered ad-hoc conversions (`96 DPI`, `72 DPI`, `25.4 mm`) | Rounding errors; clipping false positives | Central deterministic unit conversion (`px_to_pt`, `pt_to_mm`, etc.) |
| **Color System & Contrast** | Raw hex literals in HTML and Python | Inaccessible low-contrast text | Semantic color tokens with WCAG contrast ratio calculation |
| **Component Specifications** | Hardcoded HTML string templates | Component collapse into generic cards | Typed `ComponentSpec` with artifact compatibility & token bindings |
| **Asset Resolution** | Raw file paths | Crashes on missing optional assets | `AssetRegistry` with graceful degradation and finding generation |
| **Quality Authority Integration** | Evaluators hardcode thresholds | Evaluators diverge from design profiles | Design system acts as signal provider to `UnifiedQualityAuthority` |

---

## 4. Proposed Design System Architecture (`app/design_system/`)

```
app/design_system/
├── __init__.py
├── contracts/
│   ├── tokens.py        # Raw, Semantic, Artifact, Render tokens
│   ├── typography.py    # FontFace, TypographyScale, TypographyToken
│   ├── colors.py        # ColorToken, Palette, Contrast calculation
│   ├── spacing.py       # SpacingToken, unit-aware spacing scale
│   ├── geometry.py      # CanvasSpec, safe zones, margins
│   ├── borders.py       # BorderToken, RadiusScale
│   ├── shadows.py       # ElevationToken, shadow specs
│   ├── assets.py        # AssetSpec, AssetType, asset metadata
│   ├── components.py    # ComponentSpec, slot definitions, constraints
│   └── profiles.py      # DesignProfile base contract
├── registry/
│   ├── token_registry.py     # Global token storage & lookup
│   ├── font_registry.py      # Cross-renderer font registration
│   ├── asset_registry.py     # Asset lookup & graceful fallback
│   ├── component_registry.py # Component specification registry
│   └── profile_registry.py   # Format profile registration
├── themes/
│   ├── base.py          # BaseTheme definition
│   ├── educational.py   # High school & classroom educational theme
│   ├── scientific.py    # Formal academic / KTI theme
│   └── neutral.py       # Clean minimalist default theme
├── profiles/
│   ├── presentation.py         # PresentationDesignProfile (16:9)
│   ├── handout.py              # HandoutDesignProfile (A4 continuous)
│   ├── worksheet.py            # WorksheetDesignProfile (A4 inquiry)
│   └── scientific_document.py  # ScientificDocumentDesignProfile (A4 formal)
├── adapters/
│   ├── html_adapter.py       # Generates CSS variables & token classes
│   ├── css_adapter.py        # Scoped stylesheet generation
│   ├── reportlab_adapter.py  # Converts tokens to ReportLab ParagraphStyle & Colors
│   ├── pymupdf_adapter.py    # Bounding box geometry expectations
│   └── pillow_adapter.py     # Pixel raster conversions
├── validation/
│   ├── token_validator.py          # Validates token resolution & references
│   ├── typography_validator.py     # Minimum font size & line-height checks
│   ├── color_validator.py          # WCAG contrast ratio checks
│   ├── geometry_validator.py       # Canvas bounds & safe margin checks
│   ├── asset_validator.py          # Asset presence & dimension checks
│   └── cross_renderer_validator.py # Verifies HTML vs ReportLab parity
└── resolver.py          # DesignTokenResolver (contextual resolution & fallback)
```

---

## 5. Architectural Invariants (Phase 3B.0)

- **INV-DESIGN-001**: No renderer may define canonical font family independently.
- **INV-DESIGN-002**: No renderer may define canonical artifact geometry independently.
- **INV-DESIGN-003**: No arbitrary color literals in newly migrated renderer code.
- **INV-DESIGN-004**: Every font used in output must resolve through `FontRegistry`.
- **INV-DESIGN-005**: Every critical asset must resolve through `AssetRegistry`.
- **INV-DESIGN-006**: Artifact-specific minimum font sizes must be strictly enforced.
- **INV-DESIGN-007**: Renderer token resolution must be 100% deterministic and offline.
- **INV-DESIGN-008**: Token resolution must preserve raw provenance trace.
- **INV-DESIGN-009**: Unsupported renderer capabilities must degrade explicitly with recorded provenance.
- **INV-DESIGN-010**: Component specifications must declare artifact compatibility.
- **INV-DESIGN-011**: Design tokens cannot contain semantic source content.
- **INV-DESIGN-012**: `UnifiedQualityAuthority` remains the sole Level-0 export decision authority.

---

*Forensic Architecture Audit Completed. Implementation may proceed sequentially through Steps B to K.*
